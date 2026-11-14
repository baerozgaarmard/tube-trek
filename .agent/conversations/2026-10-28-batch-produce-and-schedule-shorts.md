# Session Log: Batch Production & Algorithmic Scheduling of 3 Viral Shorts

- **Date:** 2026-10-28
- **Channel:** [@baerozgaarmard](https://youtube.com/@baerozgaarmard) (`UC9AtNXG-cX2flZJXrQkDv1Q`)
- **Conversation ID:** 13fe73cd-9a68-4cba-830c-3451a17492d5

## 1. Intent
Produce 3 viral space/paradox YouTube Shorts crafted from competitor intelligence (AstroKobi, Zack D. Films, Space Beyond Limits: 8M-66M views) and execute an automated publication/scheduling strategy:
1. Video 1: **"Why Black Holes Kill You With Time"** -> Publish Immediately (Public).
2. Video 2: **"Why Aliens Refuse to Send Radio Signals"** -> Schedule for 5:00 AM IST (2026-10-28T23:30:00Z) tomorrow (peak US prime time).
3. Video 3: **"1 Quantum Rule Proves the Simulation"** -> Schedule for 2:00 PM IST (2026-10-29T08:30:00Z) tomorrow.

## 2. Technical Decisions & Architecture
- **Direct Script Injection (`batch_produce.py`):** Bypassed external LLM API rate-limits/timeouts by directly injecting pre-engineered, 100/100 title scored and 65-word scripts (<28s spoke duration at 150 wpm) for guaranteed execution without stalling.
- **YouTube API Scheduling Integration:** Implemented RFC 3339 timestamp handling (`publish_at`) with mandatory `privacyStatus="private"` requirement for scheduled Shorts via [`uploader/youtube.py`](file:///C:/Users/ayush/.gemini/antigravity/scratch/youtube-agentic-ai-studio/uploader/youtube.py).
- **Full Pipeline Orchestration:**
  - Dynamic Stock Visual Downloader (`video/stock.py`) fetching portrait B-roll from free fallback stack (Pixabay, NASA, Openverse, Pollinations).
  - High-fidelity narration with synchronized SRT word-level timestamps via Microsoft Edge TTS (`en-US-AndrewNeural`).
  - Vertical 1080x1920 video composition with animated captions and high-energy pacing (`video/creator.py`).
  - High-contrast portrait thumbnail rendering (`video/thumbnail.py`).
  - Direct resumable chunked YouTube Data API v3 upload.

## 3. Files Modified
- [`batch_produce.py`](file:///C:/Users/ayush/.gemini/antigravity/scratch/youtube-agentic-ai-studio/batch_produce.py): Built batch pipeline orchestrating production, thumbnail generation, and YouTube upload/scheduling.
- [`agents/scriptwriter.py`](file:///C:/Users/ayush/.gemini/antigravity/scratch/youtube-agentic-ai-studio/agents/scriptwriter.py): Enforced 65-75 word limit and stripped hashtags from titles.
- [`agents/researcher.py`](file:///C:/Users/ayush/.gemini/antigravity/scratch/youtube-agentic-ai-studio/agents/researcher.py): Robust exact bracket parser.
- [`uploader/youtube.py`](file:///C:/Users/ayush/.gemini/antigravity/scratch/youtube-agentic-ai-studio/uploader/youtube.py): Added `publish_at` scheduling support.

## 4. Production & Delivery Verification
All 3 Shorts successfully produced, rendered, and uploaded to YouTube:
- **Video 1 (LIVE NOW - Public):**
  - **Title:** `Why Black Holes Kill You With Time`
  - **URL:** [https://www.youtube.com/watch?v=lB_oW9NiqQY](https://www.youtube.com/watch?v=lB_oW9NiqQY)
  - **Duration:** 24.6s (65 words)
  - **Status:** Public
- **Video 2 (SCHEDULED for 5:00 AM IST Tomorrow):**
  - **Title:** `Why Aliens Refuse to Send Radio Signals`
  - **URL:** [https://www.youtube.com/watch?v=Po3NQdoKi_w](https://www.youtube.com/watch?v=Po3NQdoKi_w)
  - **Duration:** 27.4s (64 words)
  - **Status:** Scheduled (`2026-10-28T23:30:00Z` UTC)
- **Video 3 (SCHEDULED for 2:00 PM IST Tomorrow):**
  - **Title:** `1 Quantum Rule Proves the Simulation`
  - **URL:** [https://www.youtube.com/watch?v=ukQHxoJtTFM](https://www.youtube.com/watch?v=ukQHxoJtTFM)
  - **Duration:** 25.6s (63 words)
  - **Status:** Scheduled (`2026-10-29T08:30:00Z` UTC)

