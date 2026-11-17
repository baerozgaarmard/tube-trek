"""
Video Creator — Cinematic Edition (Normal) + Shorts Edition
Normal  : Kurzgesagt-style 1920×1080, one image per section, Ken Burns,
          animated title cards, bullet points, lower-third captions.
Shorts  : Fast-paced 1080×1920, image slideshow (cuts every 2-3 s),
          NO section-type labels, synced SRT captions burnt in,
          high-energy zoom pulses, gradient text overlay.

Runs fully offline: MoviePy 1.0.3 + Pillow + NumPy.
"""
import os, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import VideoClip, AudioFileClip, concatenate_videoclips

import config

# ── globals (overwritten per call) ────────────────────────────
W   = config.SHORTS_WIDTH
H   = config.SHORTS_HEIGHT
FPS = config.SHORTS_FPS
C   = config.COLORS

# FIX: Font cache — load each (variant, size) pair once, not every frame.
_font_cache: dict = {}


# ══════════════════════════════════════════════════════════════
#  FONT LOADING
# ══════════════════════════════════════════════════════════════

def _load_font(variant: str, size: int) -> ImageFont.FreeTypeFont:
    key = (variant, size)
    if key in _font_cache:
        return _font_cache[key]
    paths = config.FONT_PATHS.get(variant, config.FONT_PATHS["regular"])
    font  = None
    for path in paths:
        try:
            font = ImageFont.truetype(path, size)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()
    _font_cache[key] = font
    return font


# ══════════════════════════════════════════════════════════════
#  SRT CAPTION PARSER
# ══════════════════════════════════════════════════════════════

def _parse_srt(srt_path: str) -> list:
    """
    Returns list of {"start": float_sec, "end": float_sec, "text": str}.
    Prints a clear warning if the file is missing or empty.
    """
    if not srt_path or not os.path.exists(srt_path):
        print(f"   ⚠ SRT file not found: {srt_path}")
        print("      Captions will not appear. Run the Narration step first.")
        return []

    raw = open(srt_path, encoding="utf-8").read().strip()
    if not raw:
        print(f"   ⚠ SRT file exists but is empty: {srt_path}")
        print("      This usually means edge-tts returned no word-boundary events.")
        return []

    def _ts(s):
        h, m, rest = s.strip().split(":")
        sec, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

    captions = []
    for block in re.split(r"\n{2,}", raw):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        try:
            times = lines[1].split(" --> ")
            captions.append({
                "start": _ts(times[0]),
                "end":   _ts(times[1]),
                "text":  " ".join(lines[2:]),
            })
        except Exception:
            continue

    if not captions:
        print(f"   ⚠ SRT file has content but no valid cues could be parsed.")
        print(f"      First 300 chars: {raw[:300]!r}")

    return captions


# ══════════════════════════════════════════════════════════════
#  IMAGE UTILITIES
# ══════════════════════════════════════════════════════════════

def _load_bg_image(path: str) -> np.ndarray | None:
    """Load + cover-resize to current W×H."""
    if not path or not os.path.exists(path):
        return None
    img  = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale  = max(W / iw, H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img    = img.resize((nw, nh), Image.LANCZOS)
    left   = (nw - W) // 2
    top    = (nh - H) // 2
    return np.array(img.crop((left, top, left + W, top + H)), dtype=np.uint8)


def _load_broll_shot(path: str):
    """Load either a video clip or cover-resized image array."""
    if not path or not os.path.exists(path):
        return None
    if path.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
        try:
            from moviepy.editor import VideoFileClip
            vclip = VideoFileClip(path)
            return {"type": "video", "clip": vclip, "path": path}
        except Exception as e:
            print(f"   ⚠ VideoFileClip fallback: {e}")
    arr = _load_bg_image(path)
    if arr is not None:
        return {"type": "image", "array": arr, "path": path}
    return None


def _get_shot_frame(shot, t_shot: float, idx: int, slot_dur: float) -> np.ndarray:
    """Extract a frame from either a video clip or zoom-pulsed static image."""
    if isinstance(shot, dict) and shot.get("type") == "video":
        vclip = shot["clip"]
        v_t = t_shot % max(vclip.duration, 0.1)
        raw = vclip.get_frame(v_t)
        fh, fw = raw.shape[:2]
        if fw != W or fh != H:
            scale = max(W / fw, H / fh)
            nw, nh = int(fw * scale), int(fh * scale)
            img = Image.fromarray(raw).resize((nw, nh), Image.LANCZOS)
            left = (nw - W) // 2
            top = (nh - H) // 2
            return np.array(img.crop((left, top, left + W, top + H)), dtype=np.uint8)
        return raw
    elif isinstance(shot, dict) and shot.get("type") == "image":
        return _zoom_pulse(shot["array"], t_shot, idx, slot_dur)
    else:
        return _zoom_pulse(shot, t_shot, idx, slot_dur)


def _apply_overlay(arr: np.ndarray, opacity: float = None) -> np.ndarray:
    op = opacity if opacity is not None else config.OVERLAY_OPACITY
    return (arr * (1 - op)).astype(np.uint8)


def _gradient_bg(t: float) -> np.ndarray:
    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        r = int(C["background"][0] + (C["primary"][0] - C["background"][0]) * (y / H) * 0.4)
        g = int(C["background"][1] + (C["primary"][1] - C["background"][1]) * (y / H) * 0.3)
        b = int(C["background"][2] + (C["primary"][2] - C["background"][2]) * (y / H) * 0.5)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    for i in range(3):
        phase = t * 0.3 + i * 2.1
        cx = W // 2 + int(300 * math.cos(phase * 0.5 + i))
        cy = H // 2 + int(200 * math.sin(phase * 0.4 + i))
        r_px = int(280 + 60 * math.sin(phase))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.ellipse([cx - r_px, cy - r_px, cx + r_px, cy + r_px],
                   fill=(*C["primary"], 20))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    return np.array(img, dtype=np.uint8)


# ══════════════════════════════════════════════════════════════
#  TEXT UTILITIES
# ══════════════════════════════════════════════════════════════

def _shadow_text(draw, pos, text, font, fill, shadow_color=(0, 0, 0), shadow_offset=3):
    x, y = pos
    for ox in range(-shadow_offset, shadow_offset + 1):
        for oy in range(-shadow_offset, shadow_offset + 1):
            if abs(ox) + abs(oy) >= shadow_offset:
                draw.text((x + ox, y + oy), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)


def _wrap_text(draw, text, font, max_width):
    words, lines, current = text.split(), [], []
    for word in words:
        test = " ".join(current + [word])
        if draw.textbbox((0, 0), test, font=font)[2] > max_width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def _ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def _alpha(color, a):
    a = max(0.0, min(1.0, a))
    return tuple(int(c * a) for c in color[:3])




#  SHORTS — FAST-PACED SLIDESHOW RENDERER
# ══════════════════════════════════════════════════════════════

# How long each image stays on screen (seconds).
# The crossfade overlaps the last CROSSFADE_DURATION seconds of one image
# with the first CROSSFADE_DURATION seconds of the next, so images blend
# rather than pop.  Actual visible time per image = SHORTS_IMG_DURATION.
SHORTS_IMG_DURATION = 2.5   # seconds of visible time per image (before fade)

# Caption styling
CAP_BG        = (0, 0, 0, 180)
CAP_FG        = (255, 255, 255)
CAP_FONT_SIZE = 56           # large for vertical mobile viewing

# Vignette darkness at edges
VIGNETTE_STRENGTH = 0.55

# FIX: Vignette is now built with NumPy (vectorised) instead of a Python
# double-for-loop over millions of pixels — ~100× faster.
_vignette_cache: dict = {}


def _build_vignette(w: int, h: int) -> np.ndarray:
    """Pre-build a vignette mask using NumPy broadcasting (fast)."""
    cx, cy = w / 2, h / 2
    xs = (np.arange(w, dtype=np.float32) - cx) / cx   # -1 … +1
    ys = (np.arange(h, dtype=np.float32) - cy) / cy   # -1 … +1
    xx, yy = np.meshgrid(xs, ys)
    d    = np.sqrt(xx ** 2 + yy ** 2)                 # distance from centre
    mask = 1.0 - np.clip(d, 0.0, 1.0) * VIGNETTE_STRENGTH
    return mask[:, :, np.newaxis].astype(np.float32)   # (H, W, 1) for broadcasting


def _get_vignette():
    key = (W, H)
    if key not in _vignette_cache:
        _vignette_cache[key] = _build_vignette(W, H)
    return _vignette_cache[key]


def _apply_vignette(arr: np.ndarray) -> np.ndarray:
    v = _get_vignette()
    return np.clip(arr.astype(np.float32) * v, 0, 255).astype(np.uint8)


def _zoom_pulse(base: np.ndarray, img_t: float, img_index: int = 0, slot_dur: float = None) -> np.ndarray:
    """
    Alternating Ken Burns punch per shot: even shots push in (1.0 -> 1.09),
    odd shots pull out (1.09 -> 1.0) with opposite horizontal drift for rhythm.
    """
    dur      = slot_dur if slot_dur else SHORTS_IMG_DURATION
    progress = min(img_t / max(dur, 0.001), 1.0)
    if img_index % 2 == 0:
        scale = 1.0 + 0.09 * progress
        pan_x = 0.02 * progress
    else:
        scale = 1.09 - 0.09 * progress
        pan_x = -0.02 * progress

    crop_w = int(W / scale)
    crop_h = int(H / scale)
    x0 = int((W - crop_w) / 2 + pan_x * W)
    y0 = (H - crop_h) // 2
    x0 = max(0, min(x0, W - crop_w))
    y0 = max(0, min(y0, H - crop_h))
    cropped = base[y0: y0 + crop_h, x0: x0 + crop_w]
    return np.array(Image.fromarray(cropped).resize((W, H), Image.LANCZOS), dtype=np.uint8)


def _group_kinetic_chunks(word_timings: list, max_words: int = 3) -> list:
    """Group word timings into tight 2-3 word chunks that bridge small pauses smoothly."""
    chunks = []
    for i in range(0, len(word_timings), max_words):
        grp = word_timings[i : i + max_words]
        c_end = word_timings[i + max_words]["start"] if (i + max_words) < len(word_timings) else grp[-1]["end"] + 0.25
        chunks.append({"start": grp[0]["start"], "end": max(grp[-1]["end"], c_end), "words": grp})
    return chunks


def _draw_kinetic_words(frame_img: Image.Image, chunk: dict, t: float) -> Image.Image:
    """
    Render punchy centered kinetic captions with the active spoken word popped in amber-gold
    and crisp thick black stroke (no bulky translucent box covering visuals).
    """
    words = chunk["words"]
    if not words:
        return frame_img

    active_idx = 0
    for i, w in enumerate(words):
        if w["start"] <= t:
            active_idx = i

    draw      = ImageDraw.Draw(frame_img)
    font_norm = _load_font("bold", 68)
    font_pop  = _load_font("bold", 76)
    space_w   = int(font_norm.getlength(" ") * 1.15)

    # Measure total width of the chunk; split into 2 lines only if wider than safe margin
    items = []
    for i, w in enumerate(words):
        txt  = w["word"].upper()
        fnt  = font_pop if i == active_idx else font_norm
        ww   = int(fnt.getlength(txt))
        items.append((txt, fnt, ww, i == active_idx))

    max_w = W - 240  # Keep 120px margin clear on left and right (safe from Shorts UI icons)
    lines, cur, cur_w = [], [], 0
    for item in items:
        add_w = item[2] if not cur else cur_w + space_w + item[2]
        if cur and add_w > max_w:
            lines.append((cur, cur_w))
            cur, cur_w = [item], item[2]
        else:
            cur.append(item)
            cur_w = add_w
    if cur:
        lines.append((cur, cur_w))

    line_h  = 86
    total_h = len(lines) * line_h
    # EXACT CENTER OF SCREEN (vertically and horizontally centered)
    block_y = (H - total_h) // 2

    for li, (line_items, total_w) in enumerate(lines):
        x = (W - total_w) // 2
        y_base = block_y + li * line_h
        for txt, fnt, ww, is_active in line_items:
            y = y_base - (6 if is_active else 0)
            fill = (255, 225, 0) if is_active else (255, 255, 255)
            draw.text((x, y), txt, font=fnt, fill=fill, stroke_width=7, stroke_fill=(0, 0, 0))
            x += ww + space_w
    return frame_img


def _draw_pill_banner(frame_img: Image.Image, text: str, y: int,
                      bg_rgba=(220, 38, 38, 225), fg_rgb=(255, 255, 255), size: int = 38) -> Image.Image:
    """Draw a sharp high-contrast floating badge centered at y without obstructing captions."""
    if not text:
        return frame_img
    base = frame_img.convert("RGBA")
    ov   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od   = ImageDraw.Draw(ov)
    # Dynamically scale font if text is too wide so pill never overflows screen margins
    max_pill_w = W - 180
    font = _load_font("bold", size)
    while size > 22 and int(font.getlength(text)) > max_pill_w:
        size -= 2
        font = _load_font("bold", size)
    tw   = int(font.getlength(text))
    pad_x, pad_y = 28, 12
    x0   = max(40, (W - tw) // 2 - pad_x)
    x1   = min(W - 40, (W + tw) // 2 + pad_x)
    od.rounded_rectangle([x0, y, x1, y + size + pad_y * 2], radius=14, fill=bg_rgba)
    out  = Image.alpha_composite(base, ov)
    d2   = ImageDraw.Draw(out)
    d2.text(((W - tw) // 2, y + pad_y - 2), text, font=font, fill=fg_rgb,
            stroke_width=3, stroke_fill=(0, 0, 0))
    return out.convert("RGB")


def _draw_shorts_caption(frame_img: Image.Image, text: str) -> Image.Image:
    """
    Burnt-in caption bar: bold text centred in the lower third,
    on a semi-transparent dark pill background.

    FIX: All compositing is done in RGBA throughout; a single .convert("RGB")
    happens at the very end — removes the redundant double-conversion from
    the original code.
    """
    if not text or not text.strip():
        return frame_img

    # Work in RGBA from the start
    base_rgba = frame_img.convert("RGBA")

    # Measure text before drawing
    measure_draw = ImageDraw.Draw(base_rgba)
    font         = _load_font("bold", CAP_FONT_SIZE)
    max_w        = W - 240  # 120px safe margins from screen edges & Shorts action icons
    lines        = _wrap_text(measure_draw, text.upper(), font, max_w)

    line_h  = CAP_FONT_SIZE + 12
    total_h = len(lines) * line_h
    block_y = (H - total_h) // 2  # dead center of screen
    pad     = 20

    # Build pill-background overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od      = ImageDraw.Draw(overlay)
    for i, line in enumerate(lines):
        bbox = measure_draw.textbbox((0, 0), line, font=font)
        lw   = bbox[2] - bbox[0]
        lx   = (W - lw) // 2
        ly   = block_y + i * line_h
        od.rounded_rectangle(
            [lx - pad, ly - 6, lx + lw + pad, ly + line_h - 4],
            radius=10, fill=CAP_BG,
        )

    # Composite pill onto frame (still RGBA)
    composited = Image.alpha_composite(base_rgba, overlay)

    # Draw text directly onto composited RGBA image
    draw2 = ImageDraw.Draw(composited)
    for i, line in enumerate(lines):
        bbox = draw2.textbbox((0, 0), line, font=font)
        lw   = bbox[2] - bbox[0]
        lx   = (W - lw) // 2
        ly   = block_y + i * line_h
        _shadow_text(draw2, (lx, ly), line, font,
                     fill=CAP_FG, shadow_color=(0, 0, 0), shadow_offset=4)

    # Single conversion to RGB at the very end
    return composited.convert("RGB")


def _get_caption_at(captions: list, t_global: float) -> str:
    """Return the caption text active at global time t_global (seconds)."""
    for cap in captions:
        if cap["start"] <= t_global < cap["end"]:
            return cap["text"]
    return ""


def _get_chunk_at(chunks: list, t_global: float) -> dict | None:
    """Return the active kinetic word chunk at global time t_global."""
    for ch in chunks:
        if ch["start"] <= t_global < ch["end"]:
            return ch
    return None


def _build_shorts_clip(all_images: list, total_duration: float,
                       captions: list, word_chunks: list = None,
                       hook_badge: str = "", end_badge: str = "") -> VideoClip:
    """
    Builds a high-retention vertical Shorts clip with rapid 1.25-1.8s visual cuts,
    alternating zoom motion, active word-highlighted kinetic captions, and optional
    scroll-stop hook + end engagement badges.
    """
    n_imgs = len(all_images) if all_images else 0
    if n_imgs > 0 and total_duration > 0:
        slot_dur = max(1.25, min(3.5, total_duration / n_imgs))
    else:
        slot_dur = float(getattr(config, "SHORTS_IMG_DURATION", 2.0))

    xfade_dur = min(0.22, slot_dur * 0.25)

    def make_frame(t):
        if n_imgs > 0:
            slot      = t / slot_dur
            cur_idx   = min(int(slot), n_imgs - 1)
            img_t     = t - (cur_idx * slot_dur)

            cur_slot_start = cur_idx * slot_dur
            cur_kb_t  = t - cur_slot_start

            cur_frame = _get_shot_frame(all_images[cur_idx], cur_kb_t, cur_idx, slot_dur)
            cur_frame = _apply_overlay(cur_frame, opacity=0.36)
            cur_frame = _apply_vignette(cur_frame)

            xfade_start = slot_dur - xfade_dur
            if img_t >= xfade_start and cur_idx < n_imgs - 1:
                raw_alpha = (img_t - xfade_start) / xfade_dur
                alpha = raw_alpha * raw_alpha * (3.0 - 2.0 * raw_alpha)

                next_idx        = cur_idx + 1
                next_slot_start = (cur_idx + 1) * slot_dur
                next_kb_t       = max(0.0, t - next_slot_start)
                nxt_frame       = _get_shot_frame(all_images[next_idx], next_kb_t, next_idx, slot_dur)
                nxt_frame       = _apply_overlay(nxt_frame, opacity=0.36)
                nxt_frame       = _apply_vignette(nxt_frame)

                frame_np = (cur_frame.astype(np.float32) * (1.0 - alpha) +
                            nxt_frame.astype(np.float32) * alpha).astype(np.uint8)
            else:
                frame_np = cur_frame
        else:
            frame_np = _gradient_bg(t)

        frame = Image.fromarray(frame_np)

        # ── Scroll-stop visual hook badge (first 3.0s) ──────────
        # Positioned cleanly in upper safe zone (below top search/music bar, above center captions)
        if hook_badge and t < 3.0:
            frame = _draw_pill_banner(
                frame, hook_badge.upper(), y=210,
                bg_rgba=(220, 38, 38, 225), fg_rgb=(255, 255, 255), size=36,
            )

        # ── Kinetic Captions (word-highlighted if timings exist, dead-center)
        chunk = _get_chunk_at(word_chunks, t) if word_chunks else None
        if chunk:
            frame = _draw_kinetic_words(frame, chunk, t)
        elif not word_chunks:
            cap_text = _get_caption_at(captions, t)
            frame    = _draw_shorts_caption(frame, cap_text)

        # ── End engagement prompt badge (final 3.6s) ───────────
        # Positioned cleanly at y=1310 (above bottom YouTube channel/title interface)
        if end_badge and t >= max(0.0, total_duration - 3.6):
            frame = _draw_pill_banner(
                frame, end_badge, y=1310,
                bg_rgba=(15, 23, 42, 220), fg_rgb=(255, 225, 0), size=36,
            )

        # ── Top brand strip (below phone camera notch) ─────────
        draw = ImageDraw.Draw(frame)
        if config.brand_text():
            font_brand = _load_font("bold", 28)
            brand      = f"@{config.brand_text().upper()}"
            bbox       = draw.textbbox((0, 0), brand, font=font_brand)
            bw         = bbox[2] - bbox[0]
            draw.text(((W - bw) // 2, 120), brand, font=font_brand,
                      fill=(255, 255, 255, 175))

        return np.array(frame)

    return VideoClip(make_frame, duration=total_duration)



# ══════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════

# WATERMARK — disabled for clean studio production
WATERMARK_TEXT    = ""
WATERMARK_OPACITY = 0.0


def _watermark_patch(w: int, h: int):
    """Pre-rendered watermark: (x, y, rgb float array, alpha float array)."""
    from video import fonts
    portrait = h > w
    size = max(18, int((h * 0.017) if portrait else (h * 0.024)))
    font = fonts.get("inter", size, 600)
    pad = size // 2
    tw = int(font.getlength(WATERMARK_TEXT))
    pw, ph = tw + pad * 2, int(size * 1.5) + pad
    patch = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(patch)
    # soft dark halo keeps it legible on bright footage
    halo = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(halo).text((pad, pad // 2), WATERMARK_TEXT, font=font, fill=255,
                              stroke_width=max(2, size // 8), stroke_fill=255)
    halo = halo.filter(ImageFilter.GaussianBlur(max(2, size // 6)))
    patch.paste((0, 0, 0, 255), (0, 0), halo.point(lambda v: int(v * .55)))
    d.text((pad, pad // 2), WATERMARK_TEXT, font=font, fill=(255, 255, 255, 255))

    arr = np.asarray(patch, dtype=np.float32) / 255.0
    rgb, alpha = arr[..., :3] * 255.0, arr[..., 3:4] * WATERMARK_OPACITY
    if portrait:      # top centre, under the channel tag — clear of the Shorts UI
        x, y = (w - pw) // 2, int(h * 0.055)
    else:             # top right corner
        x, y = w - pw - int(w * 0.022), int(h * 0.035)
    return x, y, rgb, alpha


def _apply_watermark(clip, w: int, h: int):
    x, y, rgb, alpha = _watermark_patch(w, h)
    ph, pw = alpha.shape[:2]

    def stamp(frame):
        out = frame.copy()
        region = out[y:y + ph, x:x + pw].astype(np.float32)
        out[y:y + ph, x:x + pw] = (region * (1 - alpha) + rgb * alpha).astype(np.uint8)
        return out

    print(f"   → Watermark: {WATERMARK_TEXT}")
    return clip.fl_image(stamp)




def create_video(script: dict, audio_path: str, output_dir: str,
                 image_map: dict = None, video_type: str = "shorts") -> str:
    """
    Assembles the final 1080x1920 vertical YouTube Short with kinetic captions.
    image_map: {section_id: [path, path, …]}
    """
    global W, H, FPS

    _font_cache.clear()
    _vignette_cache.clear()

    W, H, FPS = config.SHORTS_WIDTH, config.SHORTS_HEIGHT, config.SHORTS_FPS
    print(f"\n   Building Shorts ({W}x{H}, {FPS} fps) ...")

    # Flatten all section image lists into one ordered list
    all_images = []
    for section in script["sections"]:
        sid   = section["id"]
        paths = (image_map or {}).get(sid, [])
        if isinstance(paths, str):
            paths = [paths]
        for p in paths:
            arr = _load_broll_shot(p)
            if arr is not None:
                all_images.append(arr)

    if not all_images:
        print("   (!) No images loaded - using animated gradient")

    srt_path = os.path.join(output_dir, "narration.srt")
    captions = _parse_srt(srt_path)
    if captions:
        print(f"   -> {len(captions)} caption cues loaded")
        last_end = max(c["end"] for c in captions)
        print(f"   -> Caption range: 0.0s -> {last_end:.1f}s")
    else:
        print("   (!) 0 caption cues - Shorts will render WITHOUT captions.")

    word_chunks = None
    words_json  = os.path.join(output_dir, "narration_words.json")
    if os.path.exists(words_json):
        import json
        try:
            raw_words = json.load(open(words_json, encoding="utf-8"))
            if raw_words:
                word_chunks = _group_kinetic_chunks(raw_words, max_words=3)
                print(f"   -> {len(word_chunks)} kinetic word-highlighted chunks loaded")
        except Exception as e:
            print(f"   (!) Word timings fallback to SRT ({e})")

    v_count = sum(1 for s in all_images if isinstance(s, dict) and s.get("type") == "video")
    print(f"   -> {len(all_images)} shots loaded ({v_count} motion videos, {len(all_images)-v_count} photos) for fast rhythmic cuts")

    # Attach audio first to know true duration
    audio     = AudioFileClip(audio_path)
    total_dur = audio.duration
    print(f"   -> Audio duration: {total_dur:.1f}s")

    final = _build_shorts_clip(
        all_images, total_dur, captions,
        word_chunks=word_chunks,
        hook_badge=script.get("hook_badge", ""),
        end_badge=script.get("end_badge", ""),
    )
    final = final.set_audio(audio)
    output_path = os.path.join(output_dir, "final_short.mp4")

    if getattr(config, 'ENABLE_WATERMARK', False):
        final = _apply_watermark(final, W, H)

    total_secs = int(final.duration)
    print(f"\n   -> Rendering {total_secs // 60}m {total_secs % 60}s Short...\n")

    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset=getattr(config, "RENDER_PRESET", "ultrafast"),
        verbose=False,
        logger=None,
    )

    for s in all_images:
        if isinstance(s, dict) and s.get("type") == "video":
            try:
                s["clip"].close()
            except Exception:
                pass

    size_mb = os.path.getsize(output_path) // (1024 * 1024)
    print(f"\n   [+] Short rendered: {output_path} ({size_mb} MB)")
    return output_path
