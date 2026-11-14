import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\ayush\.gemini\antigravity\scratch\youtube-agentic-ai-studio"
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import config
from video.stock import download_images
from video.narrator import generate_narration
from video.creator import create_video
from video.thumbnail import render as render_thumb
from uploader.youtube import upload_to_youtube

JOB = {
    "id": "falling_into_jupiter",
    "title": "If You Fall Into Jupiter, You Never Hit Ground",
    "script": {
        "title": "If You Fall Into Jupiter, You Never Hit Ground",
        "description": "If you fell into Jupiter, you would never hit a solid surface. Here is the terrifying physics of what happens as you sink into the gas giant.",
        "tags": ["Jupiter", "Space", "Astronomy", "Physics", "Science", "Shorts", "YouTubeShorts"],
        "video_type": "shorts",
        "sections": [
            {
                "id": 1,
                "section_type": "hook",
                "title": "hook_internal",
                "narration": "If you fell into Jupiter, you would never hit the ground. Because Jupiter doesn't have one.",
                "image_query": "jupiter planet great red spot dark cosmos",
                "image_query_2": "jupiter storm clouds swirling atmosphere space",
                "image_query_3": "space gas giant planet darkness",
                "image_query_4": "astronaut falling in deep space planet",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 6,
            },
            {
                "id": 2,
                "section_type": "content",
                "title": "content_internal",
                "narration": "Plunging through ammonia storms at one hundred thousand miles per hour, you sink into pitch-black darkness. Forty thousand miles down, crushing pressure turns hydrogen gas into a boiling ocean of liquid metal hotter than the sun.",
                "image_query": "hurricane storm lightning cosmic dark sky",
                "image_query_2": "molten liquid glowing metal boiling magma",
                "image_query_3": "pitch black underwater deep pressure abyss",
                "image_query_4": "glowing core plasma nuclear physics sun",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 14,
            },
            {
                "id": 3,
                "section_type": "cta",
                "title": "cta_internal",
                "narration": "You don't crash—you dissolve into pure molecules. If this broke your brain, subscribe and hit the bell for daily cosmic rabbit holes — tell me: which planet terrifies you most?",
                "image_query": "infinite cosmic explosion stars universe",
                "image_query_2": "space nebula colorful glowing dust galaxy",
                "image_query_3": "jupiter glowing from dark space atmosphere",
                "image_query_4": "deep space stars milky way night sky",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 7,
            },
        ],
    },
}

def run_production_and_upload():
    job_dir = os.path.join(config.OUTPUT_DIR, JOB["id"])
    os.makedirs(job_dir, exist_ok=True)
    img_dir = os.path.join(job_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    print("=" * 65)
    print(f"PRODUCING TODAY'S SHORT: {JOB['title']}")
    print("=" * 65)

    script = JOB["script"]
    words = len(" ".join(s["narration"] for s in script["sections"]).split())
    print(f"1. Script loaded: {words} words across {len(script['sections'])} sections (approx 26s spoken).")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading high-impact Jupiter visuals...")
    image_map = download_images(script, job_dir)

    print("\n3. Synthesizing voiceover narration (Edge TTS)...")
    audio_path = generate_narration(script, job_dir)

    print("\n4. Compositing vertical 1080x1920 video with kinetic captions (MoviePy)...")
    video_path = create_video(script, audio_path, job_dir, image_map, video_type="shorts")

    print("\n5. Rendering cinematic portrait thumbnail...")
    thumb_path = os.path.join(job_dir, "thumbnail.jpg")
    bg_candidate = None
    for imgs in image_map.values():
        if isinstance(imgs, list) and imgs:
            bg_candidate = imgs[0]
            break
        elif isinstance(imgs, str) and imgs:
            bg_candidate = imgs
            break

    try:
        render_thumb(
            style="cinematic",
            out_path=thumb_path,
            text=JOB["title"],
            bg_path=bg_candidate,
            brand="BAEROZGAARMARD",
            portrait=True,
        )
        print("   ✓ Thumbnail rendered successfully.")
    except Exception as e:
        print(f"   ⚠ Thumbnail rendering fallback: {e}")

    print("\n6. Uploading directly to YouTube (Public, Live Now)...")
    yt_url = upload_to_youtube(
        script=script,
        video_path=video_path,
        thumbnail_path=thumb_path if os.path.exists(thumb_path) else None,
        publish_at=None,
        privacy_status="public",
    )

    print("\n" + "=" * 65)
    print(f"🚀 SUCCESS! Video uploaded live to YouTube: {yt_url}")
    print("=" * 65)
    return yt_url

if __name__ == "__main__":
    run_production_and_upload()
