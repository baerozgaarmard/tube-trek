# Conversation Record: Eliminating Visual Repetition in Videos & Shorts

- **Date**: 2026-10-27
- **Associated Project**: `C:\Users\Ayush\.gemini\antigravity\scratch\youtube-agentic-ai-studio`
- **Codebase Memory Project**: `yaas-youtube-agentic-ai-studio`

## Intent
Diagnose and eliminate repeating images and B-roll in rendered YouTube Shorts and Normal videos.

## Root Causes Identified
1. **Hardcoded Slot Duration & Modulo Wrapping**:
   - `video/creator.py` hardcoded `SHORTS_IMG_DURATION = 2.5s` and used `cur_idx = int(slot) % n_imgs`. A 55-second Short with 10 images would loop through the entire slideshow twice, repeating every image after second 25.
   - Normal video sections used `cur_idx = int(slot) % n_imgs` with fixed `BROLL_INTERVAL = 10s`, causing sections with 1-2 images to loop within the section.
2. **Under-Fetching Images**:
   - `video/stock.py` only downloaded 1 image per query, resulting in only 8-11 images total for an entire video.
   - `img_num_start = qi` caused potential filename collisions.
3. **Pixabay Search Misses on Overly Descriptive Prompts**:
   - Prompts with filler words like *"dramatic wide establishing shot"* returned 0 hits on Pixabay, forcing multiple sections into the exact same fallback query (`"space universe stars galaxy"`).
   - Pixabay search lacked pagination randomization, returning the same top 10 photos across sections.

## Fixes Implemented
1. **Adaptive Duration Pacing (Zero Wrapping)**:
   - In `_build_shorts_clip()`, `slot_dur = max(2.8, min(6.0, total_duration / n_imgs))` dynamically adapts so images are evenly paced across the entire video.
   - Replaced modulo wrapping with clamped indices (`cur_idx = min(int(slot), n_imgs - 1)`). Images play sequentially without ever looping back to the beginning.
   - Applied identical pacing to Normal video section B-roll in `_make_clip()`.
2. **Multi-Image Ingestion & Collision Prevention**:
   - In `video/stock.py`, Shorts now download 2 images per query (yielding 18–24 distinct images per video).
   - Set `img_num_start = len(paths)` to guarantee unique filenames.
3. **Query Sanitization & Page Randomization**:
   - In `apis/images.py`, `_pixabay()` cleans descriptive filler words and randomizes `page = random.randint(1, 3)` with page 1 fallback.
4. **Diversified Fallback Rotation**:
   - Rotates through 10 distinct cosmic/scientific fallback topics across sections instead of repeating a single query.
5. **Testing**:
   - Verified 43/43 tests pass.
   - Refreshed GUI server at `http://localhost:7070`.

## Files Modified
- `apis/images.py`
- `video/stock.py`
- `video/creator.py`
