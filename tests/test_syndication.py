import os
import pytest
from uploader import tiktok, instagram, multi


def test_tiktok_config_check(monkeypatch):
    monkeypatch.delenv("TIKTOK_ACCESS_TOKEN", raising=False)
    assert not tiktok.is_tiktok_configured()

    monkeypatch.setenv("TIKTOK_ACCESS_TOKEN", "valid_secret_token_123")
    assert tiktok.is_tiktok_configured()


def test_instagram_config_check(monkeypatch):
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("INSTAGRAM_ACCOUNT_ID", raising=False)
    assert not instagram.is_instagram_configured()

    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "valid_ig_token")
    monkeypatch.setenv("INSTAGRAM_ACCOUNT_ID", "17841400000000000")
    assert instagram.is_instagram_configured()


def test_publish_short_graceful_unconfigured(monkeypatch, tmp_path):
    monkeypatch.delenv("TIKTOK_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)
    
    script = {"title": "Test Viral Short", "tags": ["Test"]}
    vid = str(tmp_path / "mock.mp4")
    with open(vid, "wb") as f:
        f.write(b"mock video data")

    results = multi.publish_short(
        script=script,
        video_path=vid,
        platforms=["tiktok", "instagram"],
    )
    assert "tiktok" in results
    assert "instagram" in results
    assert "Skipped" in results["tiktok"]
    assert "Skipped" in results["instagram"]
