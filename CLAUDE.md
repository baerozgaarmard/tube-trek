# Tube Trek — Agent Architecture & Operational Manual

> **Tube Trek** is a 100% headless, agent-native AI video studio engineered exclusively for viral YouTube Shorts (9:16 vertical).
> **Zero LLM API Keys Required:** As an AI coding agent, **YOU** are the scriptwriter and hook architect. Do not call external LLM APIs (Gemini/Groq/etc.) — you draft the high-retention script JSON directly!

---

## ⚡ Primary Agent Workflow

When the user asks you to create, render, or publish a YouTube Short about `<Topic>`:

### Step 1: Draft the Viral Script JSON
Write a clean `script.json` following the **30-Second Algorithmic Framework**:
- **Spoken length:** Strictly **75–85 words** (~30–33 seconds audio).
- **0–5s Hook:** Shocking physical reality or paradox. Top hook pill badge.
- **5–25s Core:** High visual velocity, zero filler.
- **25–30s Infinite Loop CTA:** Spoken CTA ending on an unfinished conjunction (e.g. *"...tell me below—because..."*) that seamlessly loops back into the opening hook on repeat!

**Schema (`script.json`):**
```json
{
  "title": "<Topic Title>",
  "description": "Engaging description with #Shorts #Science tags",
  "tags": ["Shorts", "Science", "Viral", "MindBlown"],
  "video_type": "shorts",
  "hook_badge": "SHOCKING TRUTH",
  "end_badge": "SUBSCRIBE FOR DAILY TRUTH",
  "sections": [
    {
      "id": 1,
      "section_type": "hook",
      "title": "hook",
      "narration": "First 15-20 words hook...",
      "image_query": "keyword1",
      "image_query_2": "keyword2",
      "duration_seconds": 5
    },
    {
      "id": 2,
      "section_type": "content",
      "title": "content",
      "narration": "Core explanation around 45 words...",
      "image_query": "keyword3",
      "image_query_2": "keyword4",
      "duration_seconds": 18
    },
    {
      "id": 3,
      "section_type": "cta",
      "title": "cta",
      "narration": "Final 15 words ending on an unfinished loop conjunction like 'and tell me below—because...'",
      "image_query": "keyword5",
      "image_query_2": "keyword6",
      "duration_seconds": 7
    }
  ]
}
```

### Step 2: Execute the Production Command
```bash
# 1. Render and upload immediately to YouTube:
python make_short.py --script script.json --upload

# 2. Render locally without uploading:
python make_short.py --script script.json

# 3. ElevenLabs voice + scheduled release:
python make_short.py --script script.json --voice elevenlabs --schedule "2026-11-16T12:00:00Z" --upload
```

*(Note: If `--script` is omitted, `make_short.py --topic "<Topic>"` uses an internal deterministic template, but custom agent-authored scripts are always preferred.)*

---

## 🛠️ Compositor & Media Subsystems

- **Compositor:** MoviePy + FFmpeg (1080×1920 vertical canvas, 30 FPS, `libx264`).
- **Kinetic Subtitles:** Centered 3-word popping window with amber-gold highlights on spoken words.
- **Voiceover Engines:**
  - `edge-tts` (100% free neural TTS: `en-US-AndrewNeural`, `en-GB-RyanNeural`).
  - `elevenlabs` (Optional cinematic voiceover).
- **Sound Design:** Tension sub-bass bed (`dark_cosmos_pulse.wav`) dynamically ducked to **14% volume** beneath speech.
- **Stock Sourcing:** Pexels, Pixabay, Openverse, NASA Public Archive (Zero-loop: every image appears once).
- **Publishing:** YouTube Data API v3 with Windows IPv4 monkey-patch and 5-retry resumable chunk uploads.

---

## 🔒 Secrets Hygiene

- **NEVER** commit or stage:
  - `.env`
  - `client_secret.json`
  - `youtube_token.pickle`
  - `output/` video binaries.
