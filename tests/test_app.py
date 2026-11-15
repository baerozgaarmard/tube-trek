"""Core pipeline, description builder, watermark, config and stock behaviour."""
import numpy as np
import pytest

import config
from video import creator, stock
from uploader.youtube import build_description

SCRIPT = {
    "title": "What If the Moon Disappeared?",
    "description": "A thought experiment about our Moon.",
    "tags": ["moon", "space", "physics"],
    "sections": [{"id": i, "title": f"Part {i}", "narration": "word " * 120} for i in range(1, 6)],
}


def test_description_has_content_and_tags():
    d = build_description(SCRIPT)
    assert "A thought experiment about our Moon." in d
    assert "#moon #space #physics" in d


def test_credit_can_be_toggled(monkeypatch):
    monkeypatch.setattr(config, "CREDIT_TUBE_TREK", True, raising=False)
    assert "Tube Trek" in build_description(SCRIPT)
    monkeypatch.setattr(config, "CREDIT_TUBE_TREK", False, raising=False)
    assert "Tube Trek" not in build_description(SCRIPT)


@pytest.mark.parametrize("w, h", [(1080, 1920)])
def test_watermark_fits_inside_frame_and_is_semi_transparent(w, h):
    x, y, rgb, alpha = creator._watermark_patch(w, h)
    ph, pw = alpha.shape[:2]
    assert 0 <= x and x + pw <= w and 0 <= y and y + ph <= h
    assert alpha.max() <= creator.WATERMARK_OPACITY + 1e-6


def test_watermark_is_burned_into_frames():
    class FakeClip:
        def fl_image(self, fn):
            self.fn = fn
            return self
    clip = creator._apply_watermark(FakeClip(), 1080, 1920)
    frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
    out = clip.fn(frame)
    assert out.shape == frame.shape


def test_watermark_text_is_default_empty():
    assert creator.WATERMARK_TEXT == ""


def test_save_env_updates_in_place(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# my keys\nPEXELS_API_KEY=old\nOTHER=keep\n", encoding="utf-8")
    config.save_env({"PEXELS_API_KEY": "new"}, path=str(env))
    text = env.read_text(encoding="utf-8")
    assert "# my keys" in text and "OTHER=keep" in text
    assert "PEXELS_API_KEY=new" in text and "PEXELS_API_KEY=old" not in text


def test_section_images_finds_downloaded_files(tmp_path):
    for name in ("section_01_img01.jpg", "section_01_img02.jpg", "section_02_img01.jpg"):
        (tmp_path / name).write_bytes(b"x")
    assert [p.split("section_")[-1] for p in stock.section_images(str(tmp_path), 1)] == ["01_img01.jpg", "01_img02.jpg"]


def test_pollinations_logo_strip_is_cropped(tmp_path):
    from PIL import Image
    from apis.images import strip_pollinations_logo
    p = tmp_path / "ai.jpg"
    Image.new("RGB", (1024, 576), (10, 10, 10)).save(p)
    strip_pollinations_logo(str(p))
    with Image.open(p) as im:
        assert im.size == (1024, int(576 * 0.93))
