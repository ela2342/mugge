"""Minimal pure-Python stand-in for the ``soundfile`` package (US-179).

Pyodide has no libsndfile. The shared room_correction modules only use
``write`` (float32, subtype 'FLOAT'), ``read`` (as float64) and ``info``, so
this module implements exactly that for RIFF/WAVE files. It is installed
under the name ``soundfile`` in the browser bundle only; native runs keep
the real package.

Written files match libsndfile's FLOAT layout (fmt with format tag 3,
fact, data) minus the PEAK chunk. libsndfile stamps PEAK with the current
time, so leaving it out makes the bytes deterministic.

Readable sample formats: PCM_16, PCM_24, PCM_32, FLOAT, DOUBLE. Anything
else raises RuntimeError, as libsndfile would refuse it too.
"""

import os
import struct
from types import SimpleNamespace

import numpy as np

__version__ = "0.0-mugge-web-rc"

_WAVE_FORMAT_PCM = 1
_WAVE_FORMAT_IEEE_FLOAT = 3
_WAVE_FORMAT_EXTENSIBLE = 0xFFFE

_SUBTYPES = {
    (_WAVE_FORMAT_PCM, 16): "PCM_16",
    (_WAVE_FORMAT_PCM, 24): "PCM_24",
    (_WAVE_FORMAT_PCM, 32): "PCM_32",
    (_WAVE_FORMAT_IEEE_FLOAT, 32): "FLOAT",
    (_WAVE_FORMAT_IEEE_FLOAT, 64): "DOUBLE",
}

_SUBTYPE_INFO = {
    "PCM_16": "Signed 16 bit PCM",
    "PCM_24": "Signed 24 bit PCM",
    "PCM_32": "Signed 32 bit PCM",
    "FLOAT": "32 bit float",
    "DOUBLE": "64 bit float",
}


class SoundFileError(RuntimeError):
    pass


def _open_bytes(file):
    if isinstance(file, (bytes, bytearray, memoryview)):
        return bytes(file)
    if hasattr(file, "read"):
        return file.read()
    with open(os.fspath(file), "rb") as fh:
        return fh.read()


def _parse(raw):
    """Return (format_tag, channels, samplerate, bits, data_bytes)."""
    if len(raw) < 12 or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise SoundFileError("not a RIFF/WAVE file")
    pos = 12
    fmt = None
    data = None
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        size = struct.unpack_from("<I", raw, pos + 4)[0]
        body = raw[pos + 8:pos + 8 + size]
        if len(body) < size:
            raise SoundFileError(f"truncated {cid!r} chunk")
        if cid == b"fmt ":
            if size < 16:
                raise SoundFileError("fmt chunk too short")
            tag, channels, rate, _byte_rate, block_align, bits = \
                struct.unpack_from("<HHIIHH", body, 0)
            if tag == _WAVE_FORMAT_EXTENSIBLE:
                if size < 40:
                    raise SoundFileError("extensible fmt chunk too short")
                # SubFormat GUID: first two bytes are the real format tag.
                tag = struct.unpack_from("<H", body, 24)[0]
            fmt = (tag, channels, rate, bits, block_align)
        elif cid == b"data":
            data = body
        pos += 8 + size + (size & 1)
    if fmt is None:
        raise SoundFileError("no fmt chunk")
    if data is None:
        raise SoundFileError("no data chunk")
    tag, channels, rate, bits, block_align = fmt
    if (tag, bits) not in _SUBTYPES:
        raise SoundFileError(f"unsupported WAV format tag {tag}, {bits} bit")
    if channels < 1 or block_align != channels * bits // 8:
        raise SoundFileError("inconsistent fmt chunk")
    usable = len(data) - len(data) % block_align
    return tag, channels, rate, bits, data[:usable]


def _decode(tag, bits, data):
    if tag == _WAVE_FORMAT_IEEE_FLOAT:
        return np.frombuffer(data, dtype="<f4" if bits == 32 else "<f8")
    if bits == 16:
        return np.frombuffer(data, dtype="<i2") / 32768.0
    if bits == 32:
        return np.frombuffer(data, dtype="<i4") / 2147483648.0
    b = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
    v = np.where(v & 0x800000, v - 0x1000000, v)
    return v / 8388608.0


def read(file, frames=-1, start=0, stop=None, dtype="float64",
         always_2d=False, **_ignored):
    """Read a WAV file. Returns (data, samplerate) like soundfile.read."""
    tag, channels, rate, bits, data = _parse(_open_bytes(file))
    samples = _decode(tag, bits, data).reshape(-1, channels)
    end = samples.shape[0] if stop is None else stop
    if frames >= 0:
        end = min(end, start + frames)
    samples = samples[start:end].astype(dtype)
    if not always_2d and channels == 1:
        samples = samples[:, 0]
    return samples, rate


def info(file):
    """Return an object with the soundfile.info attributes the pipeline uses."""
    tag, channels, rate, bits, data = _parse(_open_bytes(file))
    subtype = _SUBTYPES[(tag, bits)]
    frames = len(data) // (channels * bits // 8)
    return SimpleNamespace(
        name=str(file) if not hasattr(file, "read") else "<file>",
        samplerate=rate,
        channels=channels,
        frames=frames,
        duration=frames / rate if rate else 0.0,
        format="WAV",
        format_info="WAV (Microsoft)",
        subtype=subtype,
        subtype_info=_SUBTYPE_INFO[subtype],
    )


def write(file, data, samplerate, subtype=None, format=None, **_ignored):
    """Write float32 IEEE WAV (subtype 'FLOAT', the only one supported)."""
    if subtype not in (None, "FLOAT"):
        raise SoundFileError(f"only subtype FLOAT is supported, got {subtype}")
    if format not in (None, "WAV"):
        raise SoundFileError(f"only WAV is supported, got {format}")
    arr = np.asarray(data)
    if arr.ndim == 1:
        arr = arr[:, None]
    if arr.ndim != 2:
        raise SoundFileError("data must be 1-D or 2-D")
    frames, channels = arr.shape
    payload = np.ascontiguousarray(arr, dtype="<f4").tobytes()
    block_align = channels * 4
    fmt = struct.pack("<HHIIHH", _WAVE_FORMAT_IEEE_FLOAT, channels,
                      int(samplerate), int(samplerate) * block_align,
                      block_align, 32)
    chunks = (b"fmt " + struct.pack("<I", len(fmt)) + fmt
              + b"fact" + struct.pack("<II", 4, frames)
              + b"data" + struct.pack("<I", len(payload)) + payload)
    raw = b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks
    if hasattr(file, "write"):
        file.write(raw)
    else:
        with open(os.fspath(file), "wb") as fh:
            fh.write(raw)


__all__ = ["read", "write", "info", "SoundFileError"]
