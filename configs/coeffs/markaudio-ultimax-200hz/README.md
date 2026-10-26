# markaudio-ultimax-200hz: crossover-only FIR coefficients (US-173 M2)

Venue source set. These are the committed source files for the first DJ
venue; they are not the live coefficient layout on the Pi. The convolver
loads the flat files `/etc/pi4audio/coeffs/combined_*.wav`, and the
US-174d deploy path installs a source set there. Until 174d lands, the
install is a CM CHANGE that copies these exact bytes into place.

Crossover-only, minimum-phase FIR filters for the Markaudio CHN-50P mains
and one Dayton Ultimax UMII18-22 sub at 200 Hz (venue
`configs/venues/markaudio-ultimax-200hz.yml`). No room correction: US-174
replaces these after measurement.

| Source file | Installed as | Convolver channel |
|---|---|---|
| combined_left_hp.wav | combined_left_hp.wav | AUX0, left main (200 Hz highpass) |
| combined_right_hp.wav | combined_right_hp.wav | AUX1, right main (200 Hz highpass) |
| combined_sub1_lp.wav | combined_sub1_lp.wav | AUX2, sub 1 (200 Hz lowpass) |
| combined_sub2_lp.wav | combined_sub2_lp.wav | AUX3, sub 2: muted, no second sub (byte copy of `../zero.wav`) |

All files: 48 kHz, mono, IEEE float32, 16384 samples. `../zero.wav` is
canonical (all samples exactly 0.0) and is never regenerated;
combined_sub2_lp.wav is a byte copy of it. The venue `coefficients:` field
is metadata only: the convolver always loads the flat combined_*.wav
names, so the set ships the sub 2 file itself.

## Provenance

Generated on the Mac on 2026-10-26 from a66576eb (F-374 LR crossover,
PR #55; generator, profile and identities unmodified in the worktree) in
`nix develop` (Python 3.13.12) with:

    python scripts/generate-crossover-coeffs.py \
        --profile configs/speakers/profiles/2way-200hz-markaudio-ultimax.yml \
        --output-dir /tmp/w3-us173/gen --deploy-names

Only the three generated WAVs were copied in; combined_sub2_lp.wav is
`cp ../zero.wav`. Inputs (sha256):

- `configs/speakers/profiles/2way-200hz-markaudio-ultimax.yml`:
  8510ec304df0553e82be082abb7e7c27038ee131662e98b6cf051365f2416ec9
- `configs/speakers/identities/markaudio-chn-50p-sealed-1l16.yml`:
  04f31e3f8c9438de1b1827e38ec0c1b260af2abd96ab94cd3766417522f7948e
- `configs/speakers/identities/dayton-ultimax-umii18-22-sealed-120l.yml`:
  9cdc93f1a0a78123508280871c424c78ab523bb4aca9d7faf7576794abd1f97c

## Hashes

`SHA256SUMS` covers the committed bytes of the four WAVs in this
directory; combined_sub2_lp.wav's entry equals the pinned hash of
`../zero.wav` (97b9d9db...0c56). Never regenerate on
the Pi: libsndfile writes a PEAK chunk with a timestamp, so every run
produces different bytes for identical samples. After the install, the
deployed files are checked against these hashes.

## Checks

`src/web-ui/tests/unit/test_committed_venue_coeffs.py` checks the hashes
and the zero.wav layout, then runs these on the three WAVs (FFT of 65536
points; "relative" means relative to max |H| over [200 Hz, 16 kHz]):

- format, and D-009 (no bin above -0.5 dB), via `room_correction.verify`;
- D-031 floor for channels with a numeric `mandatory_hpf_hz` f_h (the
  CHN-50P mains, 80 Hz): relative |H| <= -6 dB on [10 Hz, f_h] and
  <= -18 dB on [10 Hz, f_h/2];
- M2 regression for the mains: relative |H(80 Hz)| <= -30 dB (analytic
  LR4 at 200 Hz: -32.0 dB);
- the UMII18-22 is a D-031 exception, keyed on its identity (null HPF,
  sealed, exception documented); instead it must not boost: absolute
  |H| <= max_boost_db + 0.5 dB on [10 Hz, 200 Hz].

The response itself is the AE's acceptance.
