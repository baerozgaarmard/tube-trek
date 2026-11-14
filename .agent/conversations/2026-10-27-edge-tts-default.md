# Conversation Record: Microsoft Edge TTS Set as Default Voice Engine

- **Date**: 2026-10-27
- **Associated Project**: `C:\Users\Ayush\.gemini\antigravity\scratch\youtube-agentic-ai-studio`
- **Codebase Memory Project**: `yaas-youtube-agentic-ai-studio`

## Intent
Configure Microsoft Edge TTS (`en-US-AndrewNeural`) as the primary default voiceover engine across the video generation pipeline while keeping ElevenLabs voices seamlessly accessible via the Studio dropdown.

## Key Decisions Made
1. **Engine Default**:
   - Updated `config.py` to default `VOICE_ENGINE` to `"edge-tts"` and `VOICE_ID` to `"en-US-AndrewNeural"`.
   - Updated `.env` with `VOICE_ENGINE=edge-tts` and `VOICE_ID=en-US-AndrewNeural`.
2. **Dynamic Engine Selection in Narrator**:
   - Refactored `video/narrator.py` `generate_narration()`:
     - If the chosen `VOICE_ID` is an Edge TTS voice (e.g. `en-US-AndrewNeural`, `en-GB-LibbyNeural`), Edge TTS is used directly without consuming ElevenLabs quota.
     - If the user selects an ElevenLabs voice in Settings (Alice, George, etc.), ElevenLabs is activated automatically.
     - Sanitized terminal log print statements to safe ASCII (`->`, `[!]`, `[OK]`) to eliminate cp1252 `UnicodeEncodeError` exceptions in Windows consoles.
3. **Studio GUI & Settings**:
   - Reordered Narrator dropdown in `gui_templates/index.html` to highlight Edge TTS voices first as `(Default)`.
   - Updated checklist indicator on the Home dashboard to dynamically reflect Edge TTS as the default voiceover.
4. **Verification**:
   - Live synthesis test confirmed Edge TTS audio generation (21 KB MP3, 3.6s) and 100% synchronized SRT captions.
   - All 43 test cases in `pytest tests` pass.
   - Restarted GUI server daemon on port 7070.

## Files Modified
- `config.py`
- `.env`
- `video/narrator.py`
- `gui_templates/index.html`
