import os

# ─────────────────────────────────────────────────────────────────────────────
#  Tube Trek — Autonomous Agentic Shorts Studio · Configuration
#  API keys live in .env (git-ignored) — copy .env.example to .env
#  Scripts are authored directly by your AI coding agent (No LLM API keys needed).
# ─────────────────────────────────────────────────────────────────────────────

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _load_env(path: str = ENV_PATH) -> None:
    """Minimal .env reader (no extra dependency). Real env vars win."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def save_env(values: dict, path: str = ENV_PATH) -> None:
    """Update KEY=value pairs in .env, keeping comments and unrelated keys."""
    lines = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    remaining = dict(values)
    for i, line in enumerate(lines):
        k = line.split("=", 1)[0].strip()
        if "=" in line and not line.lstrip().startswith("#") and k in remaining:
            lines[i] = f"{k}={remaining.pop(k)}"
    lines += [f"{k}={v}" for k, v in remaining.items()]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


_load_env()

# ─────────────────────────────────────────
#  Media & Stock API Keys
# ─────────────────────────────────────────
PEXELS_API_KEY     = os.getenv("PEXELS_API_KEY",     "")   # pexels.com/api
PIXABAY_API_KEY    = os.getenv("PIXABAY_API_KEY",    "")   # pixabay.com/api/docs — more stock images
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")   # optional, unused by default

# Keys supported in .env
ENV_KEYS = [
    "PEXELS_API_KEY", "PIXABAY_API_KEY", "ELEVENLABS_API_KEY",
    "VOICE_ENGINE", "ELEVENLABS_VOICE_ID", "VOICE_ID",
]

# Image sources tried in order:
IMAGE_SOURCES = ['pixabay', 'nasa', 'openverse', 'pollinations']

# ─────────────────────────────────────────
#  Channel Branding
# ─────────────────────────────────────────
CHANNEL_NAME       = 'Baerozgaarmard'
SHOW_CHANNEL_BRAND = True
BRAND_TEXT         = ''
THUMB_STYLE        = 'impact'
CREDIT_TUBE_TREK   = False


def brand_text() -> str:
    """The on-video brand label, or "" when branding is switched off."""
    if not SHOW_CHANNEL_BRAND:
        return ""
    return (BRAND_TEXT or CHANNEL_NAME or "").strip()

# ─────────────────────────────────────────
#  Voice (Edge TTS — free, no API key)
# ─────────────────────────────────────────
VOICE_ENGINE        = os.getenv("VOICE_ENGINE", "edge-tts")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Xb7hH8MSUJpSbSDYk0k2")
ELEVENLABS_MODEL    = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
VOICE_ID            = os.getenv("VOICE_ID", "en-US-AndrewNeural")
VOICE_RATE          = '-5%'     # slow down slightly for narration feel
VOICE_PITCH         = '-3Hz'    # slightly deeper = more cinematic

# ─────────────────────────────────────────
#  YouTube Shorts Canvas (9:16 Vertical)
# ─────────────────────────────────────────
SHORTS_WIDTH  = 1080
SHORTS_HEIGHT = 1920
SHORTS_FPS    = 30

# Visual Pacing
CROSSFADE_DURATION  = 0.7
RENDER_PRESET       = 'ultrafast'
OVERLAY_OPACITY     = 0.62

# Colour palette
COLORS = {
    "background": (10,  10,  20),
    "overlay":    (0,   0,   0),
    "primary":    (99,  102, 241),   # indigo
    "accent":     (167, 139, 250),   # purple
    "highlight":  (251, 191,  36),   # amber
    "white":      (255, 255, 255),
    "light":      (199, 210, 254),   # indigo-200
    "success":    (52,  211, 153),
    "red":        (239,  68,  68),
}

# Fonts
FONT_PATHS = {
    "bold": [
        "C:/Windows/Fonts/Impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "regular": [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "light": [
        "C:/Windows/Fonts/segoeuil.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}

# ─────────────────────────────────────────
#  YouTube Upload
# ─────────────────────────────────────────
YOUTUBE_CLIENT_SECRET = "client_secret.json"
YOUTUBE_SCOPES        = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
VIDEO_CATEGORY_ID     = "27"       # 27 = Education
VIDEO_PRIVACY         = 'public'   # "public" | "unlisted" | "private"

# ─────────────────────────────────────────
#  Background Music
# ─────────────────────────────────────────
MUSIC_ENABLED     = True
MUSIC_VOLUME      = 0.14          # 0.14 = sub-bass ducked bed
MUSIC_LIBRARY_DIR = os.path.join(os.path.dirname(__file__), "music library")

# ─────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────
OUTPUT_DIR = "output"
IMAGES_DIR = "output/images"
