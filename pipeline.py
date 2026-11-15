#!/usr/bin/env python3
"""
Tube Trek — Autonomous Video Pipeline (CLI)
Uses: Gemini · Edge TTS · Pexels · MoviePy · YouTube Data API

Run:  python pipeline.py [--topic "..."] [--upload]
"""
import argparse
import os
import json
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import config
from agents.researcher   import research_topic
from agents.scriptwriter import write_script
from video.narrator      import generate_narration
from video.stock         import download_images
from video.creator       import create_video
from uploader.youtube    import upload_to_youtube


def banner(text: str):
    print("\n" + "─" * 62)
    print(f"  {text}")
    print("─" * 62)


def run(topic: str = None, upload: bool = False, voice: str = None):
    Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
    Path(config.IMAGES_DIR).mkdir(exist_ok=True)

    if voice:
        config.VOICE_ENGINE = voice

    print("\n🎬  Tube Trek  ·  Autonomous Video Pipeline\n")

    # ── 1. Research ───────────────────────────────────────────
    banner("1 / 5  ·  Researching topic  [Gemini]")
    if topic:
        research = {
            "topic": topic,
            "video_title": topic,
            "hook_question": f"What if {topic} changed everything we know?",
            "key_points": [topic],
            "grounding": {"facts": "", "sources": []},
        }
        print(f"\n  ✅  Topic : {topic}")
    else:
        research = research_topic(config.CHANNEL_DESCRIPTION)
        print(f"\n  ✅  Topic : {research['topic']}")
        print(f"      Title : {research['video_title']}")
        print(f"      Hook  : {research.get('hook_question', '')[:90]}")

    with open(f"{config.OUTPUT_DIR}/research.json", "w", encoding="utf-8") as f:
        json.dump(research, f, indent=2)

    # ── 2. Script ─────────────────────────────────────────────
    banner("2 / 5  ·  Writing script  [Gemini]")
    script = write_script(research)
    print(f"\n  ✅  {len(script['sections'])} sections written")
    for s in script["sections"]:
        words = len(s.get("narration", "").split())
        title = s.get("title", "Untitled")
        print(f"      [{s.get('id', 9):02d}] {title:<42} {words:3d} words")
    with open(f"{config.OUTPUT_DIR}/script.json", "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2)

    # ── 3. Stock Images ───────────────────────────────────────
    banner("3 / 5  ·  Downloading visual assets  [Pexels / Pixabay]")
    image_map = download_images(script, config.OUTPUT_DIR)
    found = sum(1 for v in image_map.values() if v)
    print(f"\n  ✅  {found}/{len(image_map)} images downloaded")

    # ── 4. Narration ──────────────────────────────────────────
    banner("4 / 5  ·  Generating voiceover  [Neural TTS]")
    audio_path = generate_narration(script, config.OUTPUT_DIR)
    print(f"\n  ✅  Audio: {audio_path}")

    # ── 5. Video ──────────────────────────────────────────────
    banner("5 / 5  ·  Building cinematic video  [MoviePy]")
    video_path = create_video(script, audio_path, config.OUTPUT_DIR, image_map)
    print(f"\n  ✅  Video rendered: {video_path}")

    review_data = {
        "research": research,
        "script": script,
        "video_path": video_path,
    }
    with open(f"{config.OUTPUT_DIR}/review_data.json", "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)

    # ── Upload or Save ────────────────────────────────────────
    if upload:
        banner("🚀  Uploading to YouTube")
        url = upload_to_youtube(script, video_path)
        print(f"\n  🎉  Video live: {url}\n")
        return {"video_path": video_path, "youtube_url": url}
    else:
        print("\n  💡  Video ready locally in output/ directory.")
        print("      To upload, re-run with --upload flag.\n")
        return {"video_path": video_path, "youtube_url": None}


def main():
    parser = argparse.ArgumentParser(description="Tube Trek — Autonomous Video Pipeline")
    parser.add_argument("--topic", type=str, default=None, help="Video topic or title")
    parser.add_argument("--upload", action="store_true", help="Publish directly to YouTube")
    parser.add_argument("--voice", type=str, choices=["elevenlabs", "edge-tts"], default=None, help="Voice engine")
    args = parser.parse_args()

    run(topic=args.topic, upload=args.upload, voice=args.voice)


if __name__ == "__main__":
    main()
