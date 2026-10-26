"""The browser soundfile shim against real libsndfile (US-179, Q3).

The shim is loaded under a private name so the real ``soundfile`` package
(libsndfile) stays importable as the reference.
"""

import importlib.util
import io
import struct
from pathlib import Path

import numpy as np
import pytest
import soundfile as real_sf

SHIM_PATH = Path(__file__).resolve().parents[2] / "py" / "soundfile.py"


@pytest.fixture(scope="module")
def shim():
    spec = importlib.util.spec_from_file_location("webrc_soundfile", SHIM_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _chunks(raw):
    pos, out = 12, []
    while pos + 8 <= len(raw):
        cid = raw[pos:pos + 4]
        size = struct.unpack_from("<I", raw, pos + 4)[0]
        out.append((cid, raw[pos + 8:pos + 8 + size]))
        pos += 8 + size + (size & 1)
    return out


def _fir(n=16384, seed=3):
    rng = np.random.default_rng(seed)
    return (rng.standard_normal(n) * np.exp(-np.arange(n) / 800.0)) * 0.3


def test_written_bytes_match_libsndfile_except_peak(shim, tmp_path):
    fir = _fir().astype(np.float32)
    ours, ref = tmp_path / "ours.wav", tmp_path / "ref.wav"
    shim.write(ours, fir, 48000, subtype="FLOAT")
    real_sf.write(ref, fir, 48000, subtype="FLOAT")
    ref_chunks = [c for c in _chunks(ref.read_bytes()) if c[0] != b"PEAK"]
    assert _chunks(ours.read_bytes()) == ref_chunks
    raw = ours.read_bytes()
    assert struct.unpack_from("<I", raw, 4)[0] == len(raw) - 8


def test_libsndfile_reads_shim_output(shim, tmp_path):
    fir = _fir()
    path = tmp_path / "ours.wav"
    shim.write(path, fir.astype(np.float32), 48000, subtype="FLOAT")
    data, sr = real_sf.read(path, dtype="float64")
    info = real_sf.info(path)
    assert sr == 48000
    assert info.subtype == "FLOAT"
    assert info.frames == 16384
    np.testing.assert_array_equal(data, fir.astype(np.float32).astype(np.float64))


@pytest.mark.parametrize("subtype", ["FLOAT", "DOUBLE", "PCM_16", "PCM_24", "PCM_32"])
def test_shim_reads_libsndfile_output(shim, tmp_path, subtype):
    x = np.clip(_fir(4096), -0.99, 0.99)
    path = tmp_path / f"{subtype}.wav"
    real_sf.write(path, x, 48000, subtype=subtype)
    want, want_sr = real_sf.read(path, dtype="float64")
    got, got_sr = shim.read(path, dtype="float64")
    assert got_sr == want_sr == 48000
    assert got.dtype == np.float64
    np.testing.assert_array_equal(got, want)
    info = shim.info(path)
    ref = real_sf.info(path)
    assert (info.subtype, info.samplerate, info.channels, info.frames) == \
        (ref.subtype, ref.samplerate, ref.channels, ref.frames)


def test_stereo_and_always_2d(shim, tmp_path):
    x = np.stack([_fir(256, 1), _fir(256, 2)], axis=1).astype(np.float32)
    path = tmp_path / "st.wav"
    real_sf.write(path, x, 48000, subtype="FLOAT")
    got, _ = shim.read(path)
    assert got.shape == (256, 2)
    np.testing.assert_array_equal(got, x.astype(np.float64))
    mono = tmp_path / "mono.wav"
    shim.write(mono, x[:, 0], 48000)
    assert shim.read(mono, always_2d=True)[0].shape == (256, 1)
    assert shim.read(mono)[0].shape == (256,)


def test_bytes_and_file_objects(shim):
    buf = io.BytesIO()
    shim.write(buf, np.ones(8, dtype=np.float32), 48000)
    raw = buf.getvalue()
    assert shim.info(raw).frames == 8
    assert shim.read(io.BytesIO(raw))[0].tolist() == [1.0] * 8


def test_rejects_what_it_cannot_do(shim, tmp_path):
    with pytest.raises(shim.SoundFileError):
        shim.write(tmp_path / "x.wav", np.zeros(4), 48000, subtype="PCM_16")
    with pytest.raises(shim.SoundFileError):
        shim.read(b"RIFF\x00\x00\x00\x00AIFF")
    path = tmp_path / "u8.wav"
    real_sf.write(path, np.zeros(8), 48000, subtype="PCM_U8")
    with pytest.raises(shim.SoundFileError):
        shim.read(path)
    good = io.BytesIO()
    shim.write(good, np.zeros(8, dtype=np.float32), 48000)
    truncated = good.getvalue()[:-10]
    with pytest.raises(shim.SoundFileError):
        shim.read(truncated)
