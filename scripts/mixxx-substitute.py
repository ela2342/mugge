#!/usr/bin/env python3
"""Mixxx substitute JACK client for local-demo (US-075 Bug #3).

Registers as JACK client "Mixxx" with 8 output ports (out_0..out_7),
matching GM's routing table expectations (Prefix("Mixxx"), MixxxOutput
port naming). Plays a stereo WAV/MP3 file on channels 1-2 (out_0/out_1)
in a loop, or with --tone a fixed sine test stimulus (F-394). Channels
3-8 output silence.

Must be run under pw-jack so that PipeWire's JACK shim handles the
client registration and port creation.

Usage:
    pw-jack python3 scripts/mixxx-substitute.py [--file PATH | --tone] [--channels 8]

The --file argument specifies the audio file to play (WAV or MP3).
--tone plays TONE_FREQ_HZ at TONE_PEAK_DBFS peak on channels 1-2; test
runs use it so their stimulus is known (AE Q1 V1). With neither, outputs
silence on all channels.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import os
import signal
import sys
import threading
import time
from pathlib import Path

try:
    import soundfile as sf
    import numpy as np
except ImportError:
    print("ERROR: soundfile and numpy required. Run via nix run .#local-demo.", file=sys.stderr)
    sys.exit(1)


# JACK constants
JackPortIsOutput = 0x2
JackDefaultAudioType = b"32 bit float mono audio"

# JACK callback type: int (*process)(jack_nframes_t nframes, void *arg)
JACK_PROCESS_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_uint32, ctypes.c_void_p)

# --tone stimulus (F-394, AE Q1 V1). Tests derive their expected levels
# from these. 1000 Hz is exactly 48 samples per cycle at 48 kHz.
TONE_FREQ_HZ = 1000
TONE_PEAK_DBFS = -20.0
TONE_CHANNELS = 2  # out_0/out_1 (Master L/R); the rest stay silent


def tone_block(start_frame: int, nframes: int, rate: int = 48000,
               freq_hz: int = TONE_FREQ_HZ, peak_dbfs: float = TONE_PEAK_DBFS,
               channels: int = 8) -> np.ndarray:
    """Return a (channels, nframes) float32 block of the tone stimulus.

    The phase comes from the absolute frame index, so consecutive blocks
    join without a click whatever the block size. Channels from
    TONE_CHANNELS on are exactly 0.
    """
    n = np.arange(start_frame, start_frame + nframes, dtype=np.int64)
    # Reduce the phase in integers before the float multiply, so it stays
    # exact however long the stream runs.
    phase = 2.0 * np.pi * ((n * freq_hz) % rate) / rate
    sine = (10.0 ** (peak_dbfs / 20.0) * np.sin(phase)).astype(np.float32)
    block = np.zeros((channels, nframes), dtype=np.float32)
    block[:min(TONE_CHANNELS, channels)] = sine
    return block


def load_libjack() -> ctypes.CDLL:
    """Load libjack.so (provided by pw-jack LD_LIBRARY_PATH)."""
    # pw-jack sets LD_LIBRARY_PATH to include PW's JACK shim
    lib = ctypes.util.find_library("jack")
    if lib is None:
        # Try direct path
        for path in (os.environ.get("LD_LIBRARY_PATH", "")).split(":"):
            candidate = os.path.join(path, "libjack.so")
            if os.path.exists(candidate):
                lib = candidate
                break
    if lib is None:
        print("ERROR: libjack.so not found. Run under pw-jack.", file=sys.stderr)
        sys.exit(1)
    return ctypes.CDLL(lib)


class AudioFile:
    """Audio file reader using soundfile (supports WAV, FLAC, OGG, MP3 via ffmpeg fallback)."""

    def __init__(self, path: str, num_channels: int = 2):
        self.path = path
        self.num_channels = num_channels
        self._position = 0
        self._tmp_wav: str | None = None
        self._load()

    def _load(self):
        import subprocess, tempfile

        read_path = self.path
        # soundfile/libsndfile may not support MP3 — convert via ffmpeg if needed
        try:
            data, _sr = sf.read(read_path, dtype="float32", always_2d=True)
        except Exception:
            # Try ffmpeg conversion to temp WAV
            self._tmp_wav = tempfile.mktemp(suffix=".wav")
            try:
                subprocess.run(
                    ["ffmpeg", "-i", self.path, "-ar", "48000", "-ac", "2",
                     "-f", "wav", "-y", self._tmp_wav],
                    check=True, capture_output=True,
                )
                read_path = self._tmp_wav
                data, _sr = sf.read(read_path, dtype="float32", always_2d=True)
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                print(f"ERROR: Cannot read {self.path} (no ffmpeg or conversion failed): {e}",
                      file=sys.stderr)
                # Return silence
                data = np.zeros((48000, self.num_channels), dtype=np.float32)

        file_channels = data.shape[1]

        # Store per-channel sample arrays
        self._samples: list[np.ndarray] = []
        for ch in range(self.num_channels):
            if ch < file_channels:
                self._samples.append(data[:, ch].copy())
            elif ch < 2 and file_channels >= 1:
                # Duplicate channel 0 for stereo fill
                self._samples.append(data[:, 0].copy())
            else:
                self._samples.append(np.zeros(data.shape[0], dtype=np.float32))

        self._length = data.shape[0]

    def read_frames(self, channel: int, nframes: int) -> np.ndarray:
        """Read nframes from the given channel, looping at end."""
        if channel >= self.num_channels or self._length == 0:
            return np.zeros(nframes, dtype=np.float32)

        samples = self._samples[channel]
        length = self._length
        pos = self._position

        if pos + nframes <= length:
            return samples[pos : pos + nframes].copy()

        # Wrap around
        result = np.empty(nframes, dtype=np.float32)
        first = length - pos
        result[:first] = samples[pos:length]
        remaining = nframes - first
        while remaining > 0:
            chunk = min(remaining, length)
            result[nframes - remaining : nframes - remaining + chunk] = samples[:chunk]
            remaining -= chunk
        return result

    def advance(self, nframes: int):
        """Advance the read position (call once per process cycle)."""
        if self._length > 0:
            self._position = (self._position + nframes) % self._length


def main():
    parser = argparse.ArgumentParser(description="Mixxx substitute JACK client")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file", type=str, default=None, help="Audio file to play (WAV)")
    source.add_argument("--tone", action="store_true",
                        help=f"Play a {TONE_FREQ_HZ} Hz sine at {TONE_PEAK_DBFS} dBFS peak on ch 1-2")
    parser.add_argument("--channels", type=int, default=8, help="Number of output ports")
    parser.add_argument("--client-name", type=str, default="Mixxx", help="JACK client name")
    args = parser.parse_args()

    jack = load_libjack()

    # Set up function signatures
    jack.jack_client_open.restype = ctypes.c_void_p
    jack.jack_client_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    jack.jack_port_register.restype = ctypes.c_void_p
    jack.jack_port_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong]
    jack.jack_set_process_callback.restype = ctypes.c_int
    jack.jack_set_process_callback.argtypes = [ctypes.c_void_p, JACK_PROCESS_CALLBACK, ctypes.c_void_p]
    jack.jack_activate.restype = ctypes.c_int
    jack.jack_activate.argtypes = [ctypes.c_void_p]
    jack.jack_deactivate.restype = ctypes.c_int
    jack.jack_deactivate.argtypes = [ctypes.c_void_p]
    jack.jack_client_close.restype = ctypes.c_int
    jack.jack_client_close.argtypes = [ctypes.c_void_p]
    jack.jack_port_get_buffer.restype = ctypes.c_void_p
    jack.jack_port_get_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    jack.jack_get_sample_rate.restype = ctypes.c_uint32
    jack.jack_get_sample_rate.argtypes = [ctypes.c_void_p]

    # Open client
    status = ctypes.c_int(0)
    client = jack.jack_client_open(
        args.client_name.encode(),
        0,  # JackNoStartServer would be 1, but 0 is fine under pw-jack
        ctypes.byref(status),
    )
    if not client:
        print(f"ERROR: Failed to open JACK client (status={status.value})", file=sys.stderr)
        sys.exit(1)

    print(f"[mixxx-substitute] JACK client '{args.client_name}' opened")

    # Register output ports (out_0..out_N)
    ports = []
    for i in range(args.channels):
        port_name = f"out_{i}".encode()
        port = jack.jack_port_register(
            client,
            port_name,
            JackDefaultAudioType,
            JackPortIsOutput,
            0,
        )
        if not port:
            print(f"ERROR: Failed to register port out_{i}", file=sys.stderr)
            sys.exit(1)
        ports.append(port)

    print(f"[mixxx-substitute] Registered {args.channels} output ports (out_0..out_{args.channels - 1})")

    # Load audio file if provided
    audio: AudioFile | None = None
    if args.file and os.path.exists(args.file):
        try:
            audio = AudioFile(args.file, num_channels=min(2, args.channels))
            print(f"[mixxx-substitute] Loaded audio: {args.file}")
        except Exception as e:
            print(f"WARNING: Failed to load {args.file}: {e}", file=sys.stderr)
            audio = None
    elif args.file:
        print(f"WARNING: File not found: {args.file}", file=sys.stderr)

    rate = jack.jack_get_sample_rate(client)
    if args.tone:
        print(f"[mixxx-substitute] Audio source: tone {TONE_FREQ_HZ} Hz {TONE_PEAK_DBFS} dBFS")
    tone_frame = 0

    # Process callback
    @JACK_PROCESS_CALLBACK
    def process_callback(nframes, _arg):
        nonlocal tone_frame
        tone = None
        if args.tone:
            tone = tone_block(tone_frame, nframes, rate=rate, channels=len(ports))
            tone_frame += nframes
        for i, port in enumerate(ports):
            buf = jack.jack_port_get_buffer(port, nframes)
            if not buf:
                continue

            if tone is not None:
                ctypes.memmove(buf, tone[i].ctypes.data, nframes * 4)
            elif audio and i < 2:
                # Play audio on channels 0-1
                samples = audio.read_frames(i, nframes)
                ctypes.memmove(buf, samples.ctypes.data, nframes * 4)
            else:
                # Silence on other channels
                ctypes.memset(buf, 0, nframes * 4)

        if audio:
            audio.advance(nframes)
        return 0

    # Keep a reference to prevent GC
    _callback_ref = process_callback

    jack.jack_set_process_callback(client, process_callback, None)

    if jack.jack_activate(client) != 0:
        print("ERROR: Failed to activate JACK client", file=sys.stderr)
        sys.exit(1)

    print("[mixxx-substitute] Client active, playing audio...")

    # Wait for signal
    stop = threading.Event()

    def handler(signum, frame):
        print(f"\n[mixxx-substitute] Signal {signum}, shutting down...")
        stop.set()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    stop.wait()

    jack.jack_deactivate(client)
    jack.jack_client_close(client)
    print("[mixxx-substitute] Shutdown complete")


if __name__ == "__main__":
    main()
