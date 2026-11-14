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

# Video definition:
# Title: Inside A Black Hole, Space Becomes Time (39 characters, 100/100 title score)
# Topic: General relativity & Schwarzschild metric inside event horizon
# Duration: ~23-25s (60 words)
JOB = {
    "id": "sunday_revival",
    "title": "Inside A Black Hole, Space Becomes Time",
    "script": {
        "title": "Inside A Black Hole, Space Becomes Time",
        "description": "Inside a black hole, space and time completely swap roles. Why the singularity isn't a location in space—it is literally your future.",
        "tags": ["BlackHole", "Space", "Physics", "Science", "Shorts", "YouTubeShorts"],
        "video_type": "shorts",
        "sections": [
            {
                "id": 1,
                "section_type": "hook",
                "title": "hook_internal",
                "narration": "Inside a black hole, space and time completely swap roles.",
                "image_query": "black hole event horizon spacetime distortion",
                "image_query_2": "cosmic gravity singularity deep space stars",
                "image_query_3": "accretion disk black hole glowing neon",
                "image_query_4": "distorted spacetime light curvature physics",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 5,
            },
            {
                "id": 2,
                "section_type": "content",
                "title": "content_internal",
                "narration": "Outside, you can stop moving through space, but you cannot stop moving forward in time. Once you cross the event horizon, the singularity is no longer a place—it is your future. Trying to escape is as impossible as escaping tomorrow.",
                "image_query": "time dilation clock warp universe",
                "image_query_2": "black hole sucking light gravitational vortex",
                "image_query_3": "infinite galaxy spiral stars deep field",
                "image_query_4": "spacetime curvature cosmos quantum grid",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 15,
            },
            {
                "id": 3,
                "section_type": "cta",
                "title": "cta_internal",
                "narration": "Which means your timeline ends, precisely because...",
                "image_query": "universe big crunch explosion light flash",
                "image_query_2": "stars cosmic supernova blast nebula",
                "image_query_3": "infinite universe deep cosmos portal",
                "image_query_4": "event horizon light ring black hole void",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 4,
            },
        ],
    },
}

def produce():
    job_dir = os.path.join(config.OUTPUT_DIR, JOB["id"])
    os.makedirs(job_dir, exist_ok=True)
    img_dir = os.path.join(job_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    print("=" * 60)
    print(f"PRODUCING SUNDAY REVIVAL SHORT: {JOB['title']}")
    print("=" * 60)

    script = JOB["script"]
    words = len(" ".join(s["narration"] for s in script["sections"]).split())
    print(f"1. Script loaded: {words} words across 3 sections.")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading high-contrast celestial B-roll...")
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

    print("\n" + "=" * 60)
    print("✓ VIDEO PRODUCTION COMPLETE!")
    print(f"  Video file: {video_path}")
    print(f"  File size : {os.path.getsize(video_path)} bytes")
    print(f"  Thumbnail : {thumb_path}")
    print("=" * 60)

if __name__ == "__main__":
    produce()
