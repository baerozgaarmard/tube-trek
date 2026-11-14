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
    "id": "hubble_deep_field",
    "title": "NASA Pointed Hubble At Nothing For 10 Days",
    "script": {
        "title": "NASA Pointed Hubble At Nothing For 10 Days",
        "description": "In 1995, NASA aimed the Hubble Space Telescope at a completely pitch-black patch of space for 10 straight days. What it found changed our understanding of the universe forever.",
        "tags": ["Hubble", "NASA", "Space", "Universe", "Astronomy", "Shorts", "YouTubeShorts"],
        "video_type": "shorts",
        "sections": [
            {
                "id": 1,
                "section_type": "hook",
                "title": "hook_internal",
                "narration": "In 1995, NASA pointed the Hubble telescope at a completely pitch-black patch of space for ten straight days. Everyone called it a massive waste of time... until the image arrived.",
                "image_query": "hubble space telescope earth orbit dark void",
                "image_query_2": "pitch black dark space stars void empty",
                "image_query_3": "astronomer scientist observatory computer telescope",
                "image_query_4": "satellite dish deep space observatory",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 8,
            },
            {
                "id": 2,
                "section_type": "content",
                "title": "content_internal",
                "narration": "That tiny patch of sky was no larger than a grain of sand held at arm's length. Yet inside that empty darkness, Hubble revealed over ten thousand entire galaxies—each holding hundreds of billions of stars and trillions of worlds. There is no empty space.",
                "image_query": "grain of sand fingers hand human scale close up",
                "image_query_2": "hubble deep field galaxies colourful stars universe",
                "image_query_3": "spiral galaxy nebula cosmic dust glowing",
                "image_query_4": "thousands of distant galaxies space telescope deep field",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 13,
            },
            {
                "id": 3,
                "section_type": "cta",
                "title": "cta_internal",
                "narration": "You are looking at the edge of infinity. If this blew your mind, hit subscribe and ring the bell so you never miss another reality check — tell me: are we alone?",
                "image_query": "infinite universe stars deep cosmos portal",
                "image_query_2": "milky way galaxy night sky starry cosmos",
                "image_query_3": "space telescope looking at colorful nebula",
                "image_query_4": "earth glowing blue planet dark universe",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 6,
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
    print(f"PRODUCING MILLION-BENCHMARK SHORT: {JOB['title']}")
    print("=" * 65)

    script = JOB["script"]
    words = len(" ".join(s["narration"] for s in script["sections"]).split())
    print(f"1. Script loaded: {words} words across {len(script['sections'])} sections (approx 26-28s spoken).")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading high-contrast visual B-roll...")
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
