# Session Log: Scheduled Cleanup, Keyless Video B-Roll Integration & Pipeline Fixes

- **Date**: 2026-11-26 (02:10 IST)
- **Channel**: `@baerozgaarmard` (`95` subs, `27,979` views)

## 1. Actions Taken
1. **Cancelled Scheduled Queue**: Permanently deleted all **14 upcoming scheduled private Shorts** (`DJt1ULQMAUw` through `MKBMVk4wFxE`) via YouTube Data API v3 (`deleted=14, still_present=0`).
2. **Eliminated Pexels/Pixabay API Key Dependency (`apis/images.py`, `config.py`, `video/stock.py`)**:
   - Added keyless video providers: `NASA Video Library` (`media_type=video`, skipping `0–6s` logo cards and talk-show clips) and `Wikimedia Commons Video` (`filetype:video`, filtering size/resolution and diagrams/foreign text).
   - Added keyless `Wikimedia Commons` photo provider (`filetype:bitmap`, excluding diagrams/scanned book illustrations and capping images at 8 MB).
   - Added FFmpeg normalization (`_normalize_video`: center crop-scale to `1080x1920`, `30fps`, `4s`, intra-frame `-g 1`, muted H.264 MP4).
3. **Root-Cause Bugfixes**:
   - Fixed `video/stock.py` filename collision bug (`img_num_start=len(paths)` instead of `qi`) that had been overwriting up to ~30% of section assets.
   - Enforced `script.setdefault("video_type", "shorts")` in `make_short.py` so batch scripts no longer defaulted to landscape search and skipped portrait video retrieval.
   - Added `clen` stream-size guard (`8 MB` image / `25 MB` video) in `apis/images.py`.
   - Switched per-frame Ken Burns zoom in `video/creator.py` to `Image.BILINEAR` + added safe loop boundary `max(vclip.duration - 0.08, 0.05)`.
   - Guarded `uploader/youtube.py` comment insertion so it only fires when publishing immediately as `public` (preventing `403` errors on private scheduled uploads).

## 2. Verification & QA Observations
- End-to-end local test render (`test_keyless_broll_dipole_repeller`): rendered `33.7s` Short (`35 MB`, `16` unique shots: `2` motion videos + `14` photos, `BrianMultilingualNeural`).
- Frame inspection caught one French interferometer diagram and one non-English Wikimedia asset during the test, prompting addition of `_BAD_VIDEO_WORDS` / `_BAD_PHOTO_WORDS` regex filters with underscore normalization (`title.replace("_", " ")`), verified afterward via API search test.
