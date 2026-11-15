import os
import wave
import pytest
from video import sfx


def test_generate_whoosh(tmp_path):
    out = str(tmp_path / "whoosh.wav")
    path = sfx.generate_whoosh(out, duration=0.1)
    assert os.path.exists(path)
    with wave.open(path, "rb") as f:
        assert f.getnchannels() == 1
        assert f.getframerate() == 44100
        assert f.getnframes() > 0


def test_generate_pop(tmp_path):
    out = str(tmp_path / "pop.wav")
    path = sfx.generate_pop(out, duration=0.05)
    assert os.path.exists(path)
    with wave.open(path, "rb") as f:
        assert f.getnchannels() == 1
        assert f.getframerate() == 44100
        assert f.getnframes() > 0


def test_generate_sub_drop(tmp_path):
    out = str(tmp_path / "sub_drop.wav")
    path = sfx.generate_sub_drop(out, duration=0.2)
    assert os.path.exists(path)
    with wave.open(path, "rb") as f:
        assert f.getnchannels() == 1
        assert f.getframerate() == 44100
        assert f.getnframes() > 0
