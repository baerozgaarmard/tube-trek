# 🛠️ Setup Guide

Complete setup instructions for **Tube Trek — Autonomous Agentic Shorts Studio**.

> **No LLM API Keys Required:** Scripts are drafted directly by your AI coding assistant (Cursor, Claude Code, Antigravity, Gemini CLI).

---

## Prerequisites

- **Python 3.10 or newer** — [python.org/downloads](https://www.python.org/downloads/)
- **FFmpeg** installed and on your PATH (see [Step 1b](#1b-install-ffmpeg))
- Free Pexels / Pixabay account (for stock images)
- Google account (optional, only if using automated YouTube upload)

---

## Step 1 — Clone and Install

### 1a. Clone the repository

```bash
git clone https://github.com/baerozgaarmard/tube-trek.git
cd tube-trek
```

### 1b. Install FFmpeg

| OS | Command |
|---|---|
| **Windows** | `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html) |
| **macOS** | `brew install ffmpeg` |
| **Ubuntu/Debian** | `sudo apt install ffmpeg` |

Verify: `ffmpeg -version` prints version info.

### 1c. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2 — Configure Environment

Copy the sample environment file:

```bash
cp .env.example .env
```

Add your free stock image API key in `.env`:

```ini
# Free stock images (pexels.com/api)
PEXELS_API_KEY=your_pexels_api_key

# Voiceover engine: "edge-tts" (100% free, default) or "elevenlabs"
VOICE_ENGINE=edge-tts
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

## Step 4 — Producing YouTube Shorts

Instruct your AI coding agent:
> *"Create a YouTube Short about <Topic> and upload it"*

The agent will synthesize the viral script JSON and run:

```bash
# Render and upload immediately:
python make_short.py --script script.json --upload

# Local render without uploading:
python make_short.py --script script.json
```
