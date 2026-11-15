# 🛠️ Setup Guide

Complete step-by-step setup instructions for **Tube Trek — Autonomous Agentic AI Video Pipeline**.

> **Time required:** ~5 minutes

---

## Prerequisites

- **Python 3.10 or newer** — [python.org/downloads](https://www.python.org/downloads/)
- **FFmpeg** installed and on your PATH (see [Step 1b](#1b-install-ffmpeg))
- A Google account (for Gemini AI + YouTube Data API)
- A Pexels API account (free stock imagery)

---

## Step 1 — Clone and Install

### 1a. Clone the repository

```bash
git clone https://github.com/baerozgaarmard/tube-trek.git
cd tube-trek
```

### 1b. Install FFmpeg

FFmpeg is required by MoviePy for video compositing and audio mixing.

| OS | Command |
|---|---|
| **Windows** | `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html) |
| **macOS** | `brew install ffmpeg` |
| **Ubuntu/Debian** | `sudo apt install ffmpeg` |

Verify: `ffmpeg -version` should print version info.

### 1c. Install Python dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Do not upgrade** `moviepy` or `numpy` — they are pinned to ensure video compositing stability.

---

## Step 2 — Configure Environment & API Keys

Copy the sample environment file:

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```ini
# Required for AI research & scriptwriting (Free at aistudio.google.com/apikey)
GEMINI_API_KEY=your_gemini_api_key

# Required for stock B-roll images (Free at pexels.com/api)
PEXELS_API_KEY=your_pexels_api_key

# Optional: Extra stock images (Free at pixabay.com/api/docs)
PIXABAY_API_KEY=your_pixabay_api_key

# Voiceover engine: "edge-tts" (100% free, default) or "elevenlabs"
VOICE_ENGINE=edge-tts
ELEVENLABS_API_KEY=your_elevenlabs_key_if_using_elevenlabs
```

---

## Step 3 — Set Up YouTube Upload (Optional)

Skip this step if you only want to generate videos locally without auto-uploading.

1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project and enable **YouTube Data API v3**.
3. Under **APIs & Services → Credentials**, create an **OAuth client ID** (Application type: **Desktop app**).
4. Download the JSON, rename it to `client_secret.json`, and place it in the project root.
5. On your first upload, a one-time Google OAuth browser consent screen will open. The authenticated token will save locally as `youtube_token.pickle`.

---

## Step 4 — Running the Video Engine

Tube Trek is fully headless and designed to be commanded directly by you or any AI coding agent (Claude Code, Cursor, Antigravity, Gemini CLI):

### 1. Viral YouTube Shorts (9:16 Vertical — 30 Seconds)

```bash
# Generate from topic and publish immediately:
python make_short.py --topic "Why Paper Cuts Hurt More Than A Knife" --upload

# Generate locally without uploading:
python make_short.py --topic "What If The Moon Disappeared"

# High-tier ElevenLabs voice + scheduled release:
python make_short.py --topic "Inside A Black Hole" --voice elevenlabs --schedule "2026-11-16T12:00:00Z" --upload
```

### 2. Full Explainer Video Pipeline (16:9 Landscape)

```bash
# Autonomous ideation, scripting, voiceover, stock B-roll, and render:
python pipeline.py --topic "The Fermi Paradox"

# Run end-to-end and publish:
python pipeline.py --topic "Quantum Computing Explained" --upload
```

---

## Step 5 — Adding Custom Background Music

Drop any `.mp3` or `.wav` tracks into the `music library/` folder. Tube Trek automatically selects, loops, and mixes background music under narration with cinematic sub-bass ducking.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'moviepy'` | Run `pip install -r requirements.txt` |
| `ffmpeg not found` | Install FFmpeg and verify `ffmpeg -version` works in your terminal |
| `RESOURCE_EXHAUSTED` / 429 | Gemini quota hit — Tube Trek automatically fails over to Groq/OpenRouter if configured, or retry after quota reset |
| `youtube_token.pickle` expired | Delete `youtube_token.pickle` and rerun to trigger fresh OAuth authentication |
| Subtitles out of sync | Ensure `VOICE_ID` uses a word-sync-compatible model (e.g. `en-US-AndrewNeural`, `en-GB-RyanNeural`) |
