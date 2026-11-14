# Tube Trek — Agent Architecture & Operational Manual

> **Tube Trek** is an autonomous agentic video production studio engineered for high-retention vertical YouTube Shorts (9:16) and long-form visual explainers.

---

## ⚡ Primary Agent Command

When instructed to create, render, or publish a Short, run:

```bash
# 1. Automatic Topic Generation + Full Render + Immediate YouTube Upload:
python make_short.py --topic "<Topic Title>" --upload

# 2. Render from pre-drafted script:
python make_short.py --script path/to/script.json --upload

# 3. Schedule for future release:
python make_short.py --topic "<Topic Title>" --upload --schedule "2026-11-15T05:00:00Z"
```

---

## 🎬 Viral Shorts Engineering Principles (The 30-Second Rule)

Every vertical Short must adhere strictly to the **High-Retention Algorithmic Framework**:

1. **Word Count & Duration:**
   - **Target:** Exactly **75–85 spoken words** (~30–33 seconds duration).
   - *Why:* Anything over 45s incurs severe swipe-away penalty. 30s maximizes completion rate and triggers >100% Average Percentage Viewed (APV).
2. **The 2-Second Cognitive Hook (0–5s):**
   - Must present a paradox, shocking physical reality, or counter-intuitive fact.
   - Display top hook pill badge (e.g., `MICROSCOPIC CHAINSAW`, `REALITY CHECK`).
3. **Core Explanation (5–25s):**
   - Zero filler or generic greeting. High visual velocity.
   - Dynamic zero-loop B-roll: every image displays once, transitioning smoothly without ever repeating.
4. **Infinite Audio Loop CTA (25–30s):**
   - Bottom conversion badge: `HAPPENED TO YOU? | SUBSCRIBE`.
   - The final narration must end on an unfinished conjunction (e.g., *"...tell me below—because..."*) so when the player loops back to the start, the sentence completes seamlessly into the opening hook.

---

## 🛠️ Stack & Subsystems

- **Compositor:** MoviePy + FFmpeg (`libx264`, 1080×1920, 30 FPS).
- **Subtitles:** Centered 3-word kinetic subtitles with amber-gold pop on the active spoken word.
- **Voiceover Engines:**
  - `elevenlabs` (Default cinematic: George `JBFqnCBsd6RMkjVDRZzb` or Alice).
  - `edge-tts` (100% free fallback: `en-US-AndrewNeural`, `en-GB-RyanNeural`).
- **Sound Design:** Cinematic sub-bass bed (`dark_cosmos_pulse.wav`) dynamically ducked to **14% volume** beneath speech.
- **Stock Sourcing:** Pixabay, Openverse, NASA Public Archive, Pexels.
- **Publishing:** Resumable chunked upload with Windows IPv4 monkey-patch and 5-retry connection fault tolerance.

---

## 🔒 Security & Secrets Hygiene

- **NEVER** commit or stage:
  - `.env`
  - `client_secret.json`
  - `youtube_token.pickle`
  - `output/` video artifacts or binaries.
