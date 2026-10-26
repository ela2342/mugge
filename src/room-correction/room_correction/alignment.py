"""
Capture alignment: find the direct sound in a sweep capture and window the IR.

The capture start is not a reliable time reference: pw-record starts on the
wall clock and playback starts on a graph cycle, so the direct sound lands
anywhere in the capture (F-262: 1212-1324 ms, in whole 256-sample quanta).
This module finds the onset in the capture itself, anchors the IR window on
it, and fails closed when the capture can't be trusted (set A ruling: AE +
Architect, S3 / O1-O4, F1-F5).

Onset (O1, O2): the earliest local maximum of |h| within ONSET_REL_DB of the
global maximum, where h is the deconvolution of the capture against the
reference, over the full lag range. On the played reference the onset must
also stand ONSET_SNR_DB above the RMS of |h| over the pre-roll before it.

Misaligned, fail closed ("capture misaligned"), if any of these holds (O3):

- (i) onset/window: the onset is less than WINDOW_PRE samples into the
  capture, the window [onset - 5 ms, onset + 500 ms] plus the sweep overruns
  the capture, or the loudest arrival sits in the last 50 ms of the window
  (TRUNCATED);
- (ii) direct-sound SNR: no arrival stands ONSET_SNR_DB above the floor on
  the played reference;
- (iii) the onsets on the played reference and on the session sweep differ
  by more than one quantum (a sweep-law mismatch).

The raw cross-correlation width and normalized peak are logged per capture.
For room captures they are diagnostic only (F3): the room is the unknown, so
the expected width can't be known. Where the path IS known (dry loopback,
unit tests), check_expected_width() applies the 1.5x rule.
"""

import logging
from dataclasses import dataclass, field

import numpy as np

from . import dsp_utils
from .deconvolution import deconvolve_lags


logger = logging.getLogger(__name__)

SAMPLE_RATE = dsp_utils.SAMPLE_RATE

ONSET_REL_DB = 12.0     # O2: onset candidates within 12 dB of max |h|
ONSET_SNR_DB = 30.0     # O3(ii): onset above the pre-onset floor
QUANTUM = 256           # O3(iii): one PipeWire quantum
WINDOW_PRE = 240        # 5 ms before the onset
WINDOW_POST = 24000     # 500 ms after the onset (covers 16k taps)
FADE_IN = 48            # 1 ms half-Hann
FADE_OUT = 2400         # 50 ms half-Hann
TRUNCATED_GUARD = 2400  # loudest arrival within 50 ms of the window end
PRE_ROLL = 24000        # SNR floor taken over (onset - 500 ms, onset - 5 ms)
WIDTH_TRIGGER = 1.5     # check_expected_width: measured / expected


class CaptureMisaligned(RuntimeError):
    """The capture can't be aligned; no IR and no filter come from it."""

    def __init__(self, criterion, detail):
        self.criterion = criterion
        super().__init__(f"capture misaligned: ({criterion}) {detail}")


@dataclass(frozen=True)
class AlignedCapture:
    """An onset-anchored IR and the numbers behind it."""

    ir: np.ndarray
    onset: int              # session-sweep onset; the IR window anchor
    played_onset: int       # played-reference onset (O2/O3(ii))
    snr_db: float           # O3(ii) margin on the played reference
    window_margin: int      # samples to spare before the window overruns
    xcorr_width: float      # raw cross-correlation -3 dB width (logged)
    norm_peak: float        # raw cross-correlation normalized peak (logged)
    log: dict = field(default_factory=dict)


def find_onset(h, zero, rel_db=ONSET_REL_DB, snr_db=ONSET_SNR_DB,
               pre_roll=PRE_ROLL, guard=WINDOW_PRE):
    """
    Earliest local maximum of |h| within rel_db of its global maximum.

    With snr_db set, a candidate must also stand snr_db above the RMS of
    |h| over [onset - pre_roll, onset - guard). snr_db=None skips that
    floor (F2: the session-sweep onset until F-403 S2).

    Returns
    -------
    (int or None, float or None)
        The onset lag (index minus zero) and its SNR in dB; (None, None)
        if no candidate qualifies.
    """
    a = np.abs(np.asarray(h, dtype=np.float64))
    if len(a) < 3 or not np.all(np.isfinite(a)) or a.max() == 0.0:
        return None, None
    thr = a.max() * dsp_utils.db_to_linear(-rel_db)
    peaks = np.where((a[1:-1] >= a[:-2]) & (a[1:-1] > a[2:])
                     & (a[1:-1] >= thr))[0] + 1
    for i in peaks:
        lo, hi = max(0, i - pre_roll), i - guard
        floor = float(np.sqrt(np.mean(a[lo:hi] ** 2))) if hi > lo else 0.0
        snr = float(20.0 * np.log10(a[i] / max(floor, 1e-300)))
        if snr_db is None or snr >= snr_db:
            return int(i - zero), snr
    return None, None


def xcorr_width(recording, reference):
    """
    -3 dB width (samples) and normalized peak of the raw cross-correlation.

    The width is measured on |xcorr| around its maximum, with linear
    interpolation at both -3 dB crossings.
    """
    rec = np.asarray(recording, dtype=np.float64)
    ref = np.asarray(reference, dtype=np.float64)
    n_fft = dsp_utils.next_power_of_2(len(rec) + len(ref))
    c = np.abs(np.fft.irfft(np.fft.rfft(rec, n_fft)
                            * np.conj(np.fft.rfft(ref, n_fft)), n_fft))
    p = int(np.argmax(c))
    peak = c[p]
    norms = float(np.linalg.norm(rec) * np.linalg.norm(ref))
    if peak == 0.0:
        return 0.0, 0.0
    half = peak / np.sqrt(2.0)

    # Circular indices: negative lags wrap to the end of the FFT buffer.
    def edge(step):
        i = p
        while abs(i - p) < n_fft // 2 and c[(i + step) % n_fft] >= half:
            i += step
        j = (i + step) % n_fft
        return i + step * (c[i % n_fft] - half) / (c[i % n_fft] - c[j])

    return float(edge(1) - edge(-1)), float(peak / norms) if norms else 0.0


def check_expected_width(recording, reference, path_ir,
                         trigger=WIDTH_TRIGGER):
    """
    The 1.5x relative width rule, for captures through a KNOWN path.

    The expected width is that of a clean capture through the path: the
    cross-correlation of (reference filtered by path_ir) with the
    reference. A measured width above trigger x expected is a smeared
    capture. Not for room captures, where the path is the unknown (F3).

    Returns
    -------
    (float, float)
        Measured and expected widths.

    Raises
    ------
    CaptureMisaligned
        Criterion "iv", if the measured width exceeds the trigger.
    """
    ref = np.asarray(reference, dtype=np.float64)
    expected, _ = xcorr_width(np.convolve(ref, np.asarray(path_ir, dtype=np.float64)), ref)
    measured, _ = xcorr_width(recording, ref)
    if not expected > 0.0 or measured > trigger * expected:
        raise CaptureMisaligned(
            "iv", f"cross-correlation width {measured:.1f} samples exceeds "
            f"{trigger}x the expected {expected:.1f}")
    return measured, expected


def align_capture(recording, sweep, played=None, sr=SAMPLE_RATE,
                  regularization=1e-3):
    """
    Find the onset in a sweep capture and cut the onset-anchored IR.

    Parameters
    ----------
    recording : np.ndarray
        The capture, mono. Its length bounds the window (no fixed cutoff).
    sweep : np.ndarray
        The session's sweep. The IR is deconvolved against it.
    played : np.ndarray or None
        The reference for the onset and SNR checks: what was actually
        played (sweep.signal_gen_sweep() on the signal-gen path).
        None means the session sweep itself was played.
    sr : int
        Sample rate.

    Returns
    -------
    AlignedCapture
        The IR is [onset - 5 ms, onset + 500 ms] of the session-sweep
        response, with a 1 ms half-Hann fade-in and a 50 ms fade-out.

    Raises
    ------
    CaptureMisaligned
        On any of the criteria (i)-(iii) in the module docstring.
    """
    recording = np.asarray(recording, dtype=np.float64)
    sweep = np.asarray(sweep, dtype=np.float64)
    played_ref = sweep if played is None else np.asarray(played, dtype=np.float64)

    h_played, zero_played = deconvolve_lags(recording, played_ref, regularization)
    played_onset, snr = find_onset(h_played, zero_played)
    if played_onset is None:
        raise CaptureMisaligned(
            "ii", f"no arrival {ONSET_SNR_DB:.0f} dB above the pre-onset floor")

    if played is None:
        h, zero, onset = h_played, zero_played, played_onset
    else:
        h, zero = deconvolve_lags(recording, sweep, regularization)
        onset, _ = find_onset(h, zero, snr_db=None)
        if onset is None or abs(onset - played_onset) > QUANTUM:
            raise CaptureMisaligned(
                "iii", f"onset {onset} on the session sweep vs {played_onset} "
                f"on the played reference (more than {QUANTUM} samples apart)")

    window_end = onset + WINDOW_POST
    margin = (len(recording) - len(sweep)) - window_end
    width, norm_peak = xcorr_width(recording, played_ref)
    log = {
        "onset": onset, "played_onset": played_onset,
        "snr_db": round(snr, 1), "window_margin": margin,
        "xcorr_width": round(width, 2), "norm_peak": round(norm_peak, 4),
    }
    logger.info("Capture alignment: %s", log)

    if onset < WINDOW_PRE:
        raise CaptureMisaligned(
            "i", f"onset at lag {onset} is before the {WINDOW_PRE}-sample "
            f"window start")
    if margin < 0:
        raise CaptureMisaligned(
            "i", f"window overruns the capture by {-margin} samples "
            f"(onset at lag {onset})")
    loudest = int(np.argmax(np.abs(h))) - zero
    if loudest > window_end - TRUNCATED_GUARD:
        raise CaptureMisaligned(
            "i", f"TRUNCATED: loudest arrival at lag {loudest} is within "
            f"{TRUNCATED_GUARD} samples of the window end ({window_end})")

    ir = h[zero + onset - WINDOW_PRE:zero + window_end].copy()
    ir *= dsp_utils.fade_window(len(ir), FADE_IN, FADE_OUT)
    return AlignedCapture(ir=ir, onset=onset, played_onset=played_onset,
                          snr_db=snr, window_margin=margin, xcorr_width=width,
                          norm_peak=norm_peak, log=log)
