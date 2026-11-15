#!/usr/bin/env python3
"""
Tube Trek — Unified Viral Shorts Engine
Usage:
    python make_short.py --topic "Why Paper Cuts Hurt More Than A Knife" --upload
    python make_short.py --script path/to/script.json --upload
    python make_short.py --topic "Inside A Black Hole" --voice elevenlabs --schedule "2026-11-15T05:00:00Z"
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from PIL import Image
from moviepy.editor import VideoFileClip
from video.stock import download_images
from video.narrator import generate_narration
from video.music import mix_music_with_narration
from video.creator import create_video
from video.thumbnail import render as render_thumb
from uploader.youtube import upload_to_youtube


def slugify(text: str) -> str:
    """Convert text to safe filesystem folder name."""
    clean = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "_", clean).strip("_")[:50]


def draft_viral_script(topic: str) -> dict:
    """
    Generate an 80-85 word high-retention 3-section script.
    Follows the 30-second cognitive dissonance framework with an infinite replay loop.
    No external API keys required — deterministic template fallback.
    For custom scripts, your AI coding agent drafts script.json directly.
    """
    clean_topic = topic.strip()
    slug = slugify(clean_topic)

    # Check if a script.json was already generated in the current or job dir
    for candidate in [f"{slug}/script.json", os.path.join(config.OUTPUT_DIR, slug, "script.json"), "script.json"]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "sections" in data and len(data["sections"]) >= 2:
                        print(f"[*] Loaded agent-authored script from: {candidate}")
                        return data
            except Exception:
                pass

    print(f"[*] Synthesizing high-retention 30s template for: {clean_topic}...")
    return {
        "title": clean_topic,
        "description": f"The mind-bending truth behind {clean_topic}. Subscribe for daily scientific reality checks!\n\n#Science #Shorts #Physics #Curiosity",
        "tags": ["Science", "Shorts", "Physics", "MindBlown", "YouTubeShorts"],
        "video_type": "shorts",
        "hook_badge": "REALITY CHECK",
        "end_badge": "WOULD YOU AGREE? | SUBSCRIBE",
        "sections": [
            {
                "id": 1,
                "section_type": "hook",
                "title": "hook",
                "narration": f"Almost everything you've been told about {clean_topic} is completely backwards. And modern science proves why.",
                "image_query": clean_topic.split()[0] if clean_topic else "science",
                "image_query_2": "laboratory",
                "image_query_3": "space",
                "duration_seconds": 5,
            },
            {
                "id": 2,
                "section_type": "content",
                "title": "content",
                "narration": f"When researchers examined the underlying physics of {clean_topic}, they discovered an astonishing reality. Instead of standard rules, quantum interactions and structural forces behave in ways that defy common intuition, leaving scientists stunned.",
                "image_query": "microscope",
                "image_query_2": "quantum",
                "image_query_3": "nebula",
                "duration_seconds": 18,
            },
            {
                "id": 3,
                "section_type": "cta",
                "title": "cta",
                "narration": "Did this shatter your perception? Subscribe for daily reality checks, and tell me below—because...",
                "image_query": "cosmos",
                "image_query_2": "laboratory",
                "duration_seconds": 6,
            },
        ],
    }


def produce_short(
    topic: str = None,
    script_file: str = None,
    voice_engine: str = None,
    voice_id: str = None,
    music_volume: float = 0.14,
    upload: bool = False,
    privacy: str = "public",
    schedule: str = None,
    thumb_text: str = None,
    job_id: str = None,
) -> dict:
    # 1. Determine script
    if script_file and os.path.exists(script_file):
        with open(script_file, encoding="utf-8") as f:
            script = json.load(f)
    elif topic:
        script = draft_viral_script(topic)
    else:
        raise ValueError("Must provide either --topic or --script-file.")

    job_name = job_id or slugify(script.get("title", "viral_short"))
    job_dir = os.path.join(config.OUTPUT_DIR, job_name)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, "images"), exist_ok=True)

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"🎬 TUBE TREK VIRAL ENGINE: {script['title']}")
    print("=" * 60)

    # 2. Configure Voice
    if voice_engine:
        config.VOICE_ENGINE = voice_engine
    if voice_id:
        if config.VOICE_ENGINE == "elevenlabs":
            config.ELEVENLABS_VOICE_ID = voice_id
        else:
            config.VOICE_ID = voice_id

    # 3. Download Curated B-Roll
    print("\n[1/5] Ingesting visual B-roll with zero-loop pacing...")
    image_map = download_images(script, job_dir)

    # 4. Synthesize Audio & Kinetic Timestamps
    print("\n[2/5] Synthesizing voiceover narration & word-level timing...")
    audio_path = generate_narration(script, job_dir)

    # 5. Mix Audio Bed
    print(f"\n[3/5] Mixing tension sub-bass audio bed (volume: {int(music_volume * 100)}%)...")
    mixed_audio_path = os.path.join(job_dir, "narration_mixed.mp3")
    final_audio = mix_music_with_narration(
        narration_path=audio_path,
        output_path=mixed_audio_path,
        music_volume=music_volume,
        library_dir=config.MUSIC_LIBRARY_DIR,
    )

    # 6. Composite 1080x1920 Short
    print("\n[4/5] Compositing 1080x1920 vertical Short with kinetic subtitles...")
    video_path = create_video(script, final_audio, job_dir, image_map, video_type="shorts")

    # 7. Render Portrait Thumbnail
    print("\n[5/5] Designing high-contrast 9:16 portrait thumbnail...")
    thumb_path = os.path.join(job_dir, "thumbnail.jpg")
    bg_candidate = next(
        (imgs[0] if isinstance(imgs, list) and imgs else imgs for imgs in image_map.values() if imgs),
        None,
    )
    title_words = script.get("title", "VIRAL SHORT").upper().split()
    headline = thumb_text or " ".join(title_words[:5])
    render_thumb(
        style="impact",
        out_path=thumb_path,
        text=headline,
        bg_path=bg_candidate,
        brand=config.brand_text() or "TUBE TREK",
        portrait=True,
    )

    # 8. QA Frame Checks
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    print(f"   ✓ Video rendered successfully: {video_path} ({duration:.1f}s)")

    # 9. Upload
    yt_url = None
    if upload:
        print("\n🚀 Uploading to YouTube with IPv4 resilience & chunked retry...")
        yt_url = upload_to_youtube(
            script=script,
            video_path=video_path,
            thumbnail_path=thumb_path if os.path.exists(thumb_path) else None,
            publish_at=schedule,
            privacy_status=privacy,
        )
        print(f"\n🎉 LIVE ON YOUTUBE: {yt_url}\n")

    return {
        "title": script["title"],
        "video_path": video_path,
        "thumbnail_path": thumb_path,
        "duration": duration,
        "youtube_url": yt_url,
    }


def main():
    parser = argparse.ArgumentParser(description="Tube Trek — Automated Viral YouTube Shorts Pipeline")
    parser.add_argument("--topic", type=str, help="Topic or title for the Short")
    parser.add_argument("--script", type=str, help="Path to custom script.json")
    parser.add_argument("--voice", type=str, choices=["elevenlabs", "edge-tts"], default=None, help="Voice engine")
    parser.add_argument("--voice-id", type=str, default=None, help="Specific Voice ID")
    parser.add_argument("--music-volume", type=float, default=0.14, help="Background music volume (0.0 to 1.0)")
    parser.add_argument("--upload", action="store_true", help="Upload immediately to YouTube")
    parser.add_argument("--privacy", type=str, choices=["public", "private", "unlisted"], default="public", help="Upload privacy")
    parser.add_argument("--schedule", type=str, default=None, help="RFC 3339 publish timestamp (e.g. 2026-11-15T05:00:00Z)")
    parser.add_argument("--thumb-text", type=str, default=None, help="Custom thumbnail headline text")
    parser.add_argument("--job-id", type=str, default=None, help="Custom output directory name")

    args = parser.parse_args()

    if not args.topic and not args.script:
        parser.error("You must specify either --topic or --script")

    produce_short(
        topic=args.topic,
        script_file=args.script,
        voice_engine=args.voice,
        voice_id=args.voice_id,
        music_volume=args.music_volume,
        upload=args.upload,
        privacy=args.privacy,
        schedule=args.schedule,
        thumb_text=args.thumb_text,
        job_id=args.job_id,
    )


if __name__ == "__main__":
    main()
