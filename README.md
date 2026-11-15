<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:ff6a00&height=220&section=header&text=Tube%20Trek&fontSize=72&fontColor=ffffff&fontAlignY=35&desc=Autonomous%20Agentic%20AI%20Video%20Pipeline&descSize=18&descAlignY=55&animation=fadeIn" width="100%" />

<br/>

<p>
<a href="https://github.com/baerozgaarmard/tube-trek/releases/latest"><img src="https://img.shields.io/badge/Release-v1.0.0-blueviolet?style=for-the-badge&logo=github" alt="Release"/></a>&nbsp;
<a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=ffd43b" alt="Python"/></a>&nbsp;
<a href="https://ffmpeg.org"><img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg"/></a>&nbsp;
<a href="https://elevenlabs.io"><img src="https://img.shields.io/badge/ElevenLabs-000000?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB4PSI5IiB5PSIzIiB3aWR0aD0iMiIgaGVpZ2h0PSIxOCIgcng9IjEiIGZpbGw9IndoaXRlIi8+PHJlY3QgeD0iMTMiIHk9IjMiIHdpZHRoPSIyIiBoZWlnaHQ9IjE4IiByeD0iMSIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="ElevenLabs"/></a>&nbsp;
<a href="https://developers.google.com/youtube/v3"><img src="https://img.shields.io/badge/YouTube%20API%20v3-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube"/></a>&nbsp;
<a href="LICENSE"><img src="https://img.shields.io/badge/Proprietary-Closed%20Source-ff6a00?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHJlY3QgeD0iMyIgeT0iMTEiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxMSIgcng9IjIiIHJ5PSIyIi8+PHBhdGggZD0iTTcgMTFWN2E1IDUgMCAwIDEgMTAgMHY0Ii8+PC9zdmc+&logoColor=white" alt="License"/></a>
</p>

<br/>

<table>
<tr>
<td width="600">

**Production-grade multi-agent AI studio** that autonomously produces high-retention YouTube Shorts — from topic ideation to published video — in a single command.

Zero-repeat dynamic B-roll · Kinetic word-level captions · Sub-bass audio ducking · Fault-tolerant resumable uploads

</td>
</tr>
</table>

<br/>

[Architecture](#-system-architecture) · [Features](#-key-features) · [Quickstart](#-quickstart) · [CLI](#-cli-usage) · [Benchmark](#-benchmark) · [License](#-license--ip)

<br/>

</div>

<!-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ -->

## 🏗️ System Architecture

```mermaid
flowchart LR
    subgraph INPUT["🎯 Input"]
        A["Topic or Concept"]
    end

    subgraph SCRIPT["✍️ Script Engine"]
        B["Hook Engineering"]
        C["80-85 Word Script"]
        D["Loop Conjunction"]
    end

    subgraph MEDIA["🎬 Parallel Pipeline"]
        direction TB
        E["Neural Voice\nElevenLabs / Edge TTS"]
        F["Word-Level SRT"]
        G["Sub-Bass Mixing\n14% Volume"]
        H["Multi-Source B-Roll\nPixabay / Openverse / NASA"]
        I["Zero-Repeat Pool"]
    end

    subgraph RENDER["🖼️ Compositor"]
        J["1080x1920 Vertical\nMoviePy + FFmpeg"]
        K["Kinetic Captions\nAmber-Gold Pop"]
        L["Hook Badge +\nCTA Pill"]
        M["Portrait Thumbnail"]
    end

    subgraph PUBLISH["🚀 Publishing"]
        N["IPv4 Socket Layer"]
        O["5MB Chunked Upload\n5-Retry Loop"]
        P["YouTube Data API v3"]
    end

    A --> B --> C --> D
    C --> E --> F
    E --> G
    C --> H --> I
    F & G & I --> J
    J --> K & L & M
    J & M --> N --> O --> P

    style INPUT fill:#1a1a2e,stroke:#ff6a00,color:#fff
    style SCRIPT fill:#16213e,stroke:#0f3460,color:#fff
    style MEDIA fill:#1a1a2e,stroke:#e94560,color:#fff
    style RENDER fill:#16213e,stroke:#0f3460,color:#fff
    style PUBLISH fill:#1a1a2e,stroke:#ff6a00,color:#fff
```

<details>
<summary><b>📋 ASCII Fallback</b> (click to expand)</summary>

```
  ┌─────────────────┐       ┌──────────────────────────┐
  │  Topic / Concept │──────▶│  Hook + 80-85w Script    │
  └─────────────────┘       │  + Loop Conjunction Tail  │
                            └────────────┬─────────────┘
                     ┌───────────────────┼───────────────────┐
                     ▼                                       ▼
          ┌─────────────────────┐                 ┌─────────────────────┐
          │  AUDIO PIPELINE     │                 │  VISUAL PIPELINE    │
          │  ├─ Neural Voice    │                 │  ├─ Pixabay         │
          │  ├─ Word-Level SRT  │                 │  ├─ Openverse       │
          │  └─ Sub-Bass 14%    │                 │  └─ NASA Archive    │
          └──────────┬──────────┘                 └──────────┬──────────┘
                     └───────────────────┬───────────────────┘
                                         ▼
          ┌──────────────────────────────────────────────────────────┐
          │  COMPOSITOR  ·  1080×1920  ·  MoviePy + FFmpeg          │
          │  ├─ Kinetic 3-Word Captions (Amber-Gold Syllable Pop)   │
          │  ├─ Top Hook Badge  ·  Bottom CTA Pill                  │
          │  └─ 9:16 Portrait Thumbnail (Impact Layout)             │
          └────────────────────────┬─────────────────────────────────┘
                                   ▼
          ┌──────────────────────────────────────────────────────────┐
          │  RESILIENT PUBLISHER  ·  YouTube Data API v3            │
          │  ├─ IPv4 Socket Monkey-Patch (Anti-SSL EOF)             │
          │  ├─ 5 MB Chunked Resumable Upload  ·  5-Retry           │
          │  └─ Public / Scheduled (RFC 3339)                       │
          └──────────────────────────────────────────────────────────┘
```

</details>

---

## ✨ Key Features

<table>
<tr>
<td width="50%" valign="top">

### ⏱️ 30-Second Retention Engine
- **75–85 words** calibrated for maximum Average Percentage Viewed
- **Cognitive Hook (0–5s)** — counter-intuitive paradox with pill badge
- **Infinite Loop** — unfinished conjunction links to opening hook on replay

### 🎨 Kinetic Word-Level Subtitles
- Millisecond word-boundary synchronization
- Clean 3-word reading window at **58% eye-line**
- Active syllable highlighted in **amber-gold**

### 🎙️ Dual Voice + Sub-Bass Ducking
- **Primary:** ElevenLabs `George` — deep, authoritative
- **Fallback:** Edge TTS (`AndrewNeural` / `RyanNeural`) — zero cost
- **Sound Bed:** Cinematic sub-bass at 14%–16% volume

</td>
<td width="50%" valign="top">

### 🔄 Zero-Repeat B-Roll Scheduling
Every asset appears exactly **once** — no visual loops, no repeated frames.

$$\text{Slot} = \max\!\Big(2.8\text{s},\;\min\!\Big(6.0\text{s},\;\frac{\text{Duration}}{N_{\text{images}}}\Big)\Big)$$

Smooth Ken Burns transitions without snapping back.

### 🛡️ Network Resilience
- **IPv4 Monkey-Patch** — forces `AF_INET` to prevent Windows SSL EOF
- **5-Retry Chunk Loop** — 5 MB resumable uploads with automatic backoff

### 🤖 Agent-Native
First-class manifests for AI coding assistants:
- **`CLAUDE.md`** → Claude Code
- **`.cursorrules`** → Cursor IDE

> *"Create a Short about the Fermi Paradox and schedule it for 5 PM."*

</td>
</tr>
</table>

---

## 🚀 Quickstart

### 1 · Clone & Install

```bash
git clone https://github.com/baerozgaarmard/tube-trek.git
cd tube-trek
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2 · FFmpeg

```bash
winget install Gyan.FFmpeg          # Windows
brew install ffmpeg                 # macOS
sudo apt install ffmpeg             # Ubuntu/Debian
```

### 3 · Configure `.env`

```bash
cp .env.example .env
```

```ini
PIXABAY_API_KEY=your_key            # Stock imagery
PEXELS_API_KEY=your_key
VOICE_ENGINE=edge-tts               # or "elevenlabs"
ELEVENLABS_API_KEY=your_key
YOUTUBE_CHANNEL_ID=your_id          # Place client_secret.json in root
```

---

## 💻 CLI Usage

```bash
# Generate + publish in one shot
python make_short.py --topic "Why Paper Cuts Hurt More Than A Knife" --upload

# From a pre-written script
python make_short.py --script output/custom_script.json --upload

# ElevenLabs voice + scheduled release
python make_short.py \
  --topic "Inside A Black Hole You Watch The Universe Die" \
  --voice elevenlabs --upload --schedule "2026-11-15T05:00:00Z"
```

<details>
<summary><b>🔧 All Flags</b></summary>

| Flag | Description | Default |
|:---|:---|:---|
| `--topic` | Video concept or title | — |
| `--script` | Path to pre-generated JSON script | — |
| `--voice` | Engine: `elevenlabs` or `edge-tts` | `edge-tts` |
| `--music-volume` | Background music level | `0.14` |
| `--upload` | Publish to YouTube after render | `false` |
| `--privacy` | `public` · `private` · `unlisted` | `public` |
| `--schedule` | RFC 3339 timestamp for release | — |
| `--thumb-text` | Custom thumbnail headline | — |

</details>

---

## 📊 Benchmark

<table>
<tr>
<th width="30%">Capability</th>
<th width="35%">Standard AI Video Tools</th>
<th width="35%">Tube Trek</th>
</tr>
<tr><td><b>Duration Control</b></td><td>❌ Unpredictable 45s–90s</td><td>✅ Strictly 30–33s</td></tr>
<tr><td><b>Visual Looping</b></td><td>❌ Same 3–4 images repeat</td><td>✅ Zero-loop — 100% unique</td></tr>
<tr><td><b>Kinetic Captions</b></td><td>❌ Static centered blocks</td><td>✅ 3-word amber pop window</td></tr>
<tr><td><b>Replay Hook</b></td><td>❌ Abrupt ending</td><td>✅ Infinite conjunction loop</td></tr>
<tr><td><b>Audio Balance</b></td><td>❌ Music drowns voice</td><td>✅ 14% dynamic ducking</td></tr>
<tr><td><b>Upload Resilience</b></td><td>❌ Fails on network drop</td><td>✅ Chunked 5-retry engine</td></tr>
</table>

---

## 👥 Collaborators

<div align="center">
<table>
<tr>
<td align="center" width="200">
<a href="https://github.com/baerozgaarmard">
<img src="https://github.com/baerozgaarmard.png" width="80" style="border-radius:50%;" alt="Ayush Bhatt"/><br/>
<b>Ayush Bhatt</b></a><br/>
<sub>Creator & Lead Architect</sub><br/>
<a href="https://github.com/baerozgaarmard"><img src="https://img.shields.io/badge/-baerozgaarmard-181717?style=flat-square&logo=github" alt="GitHub"/></a>
</td>
<td align="center" width="200">
<a href="https://github.com/tanisha162">
<img src="https://github.com/tanisha162.png" width="80" style="border-radius:50%;" alt="Tanisha Gupta"/><br/>
<b>Tanisha Gupta</b></a><br/>
<sub>Core Engineer & Collaborator</sub><br/>
<a href="https://github.com/tanisha162"><img src="https://img.shields.io/badge/-tanisha162-181717?style=flat-square&logo=github" alt="GitHub"/></a>
</td>
</tr>
</table>
</div>

---

## 🔒 License & IP

**Proprietary and Confidential.** All Rights Reserved.
Copyright © 2026 **Ayush Bhatt** and **Tanisha Gupta**.

This repository is **Closed Source**. No license or right is granted to copy, distribute, modify, reverse-engineer, or commercially exploit this software without express written permission from the authors. See [LICENSE](LICENSE) for full legal terms.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:ff6a00&height=100&section=footer" width="100%" />

<sub>Engineered with precision by <a href="https://github.com/baerozgaarmard">@baerozgaarmard</a> and <a href="https://github.com/tanisha162">@tanisha162</a></sub>

</div>
