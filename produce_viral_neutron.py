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
    "id": "neutron_star_destruction",
    "title": "1 Spoon Of A Neutron Star Destroys Earth",
    "script": {
        "title": "1 Spoon Of A Neutron Star Destroys Earth",
        "description": "If you dropped just 1 teaspoon of a neutron star on Earth, you wouldn't survive the first second. Here is the terrifying physics of what happens next.",
        "tags": ["NeutronStar", "Space", "Physics", "Science", "Shorts", "YouTubeShorts"],
        "video_type": "shorts",
        "sections": [
            {
                "id": 1,
                "section_type": "hook",
                "title": "hook_internal",
                "narration": "If you dropped 1 spoon of a neutron star on Earth, nobody survives the first second.",
                "image_query": "neutron star pulsar cosmic glow",
                "image_query_2": "planet earth from space dark cosmos",
                "image_query_3": "dense magnetic star explosion universe",
                "image_query_4": "supernova core collapse nuclear physics",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 5,
            },
            {
                "id": 2,
                "section_type": "content",
                "title": "content_internal",
                "narration": "That tiny spoonful weighs 1 billion tons—the exact weight of Mount Everest compressed into a sugar cube. The moment you let go, Earth's crust can't hold it. It punches through bedrock like a bullet into water, vaporizing the planet into superheated plasma.",
                "image_query": "mount everest mountain peak snow dramatic",
                "image_query_2": "molten magma earth core lava plasma",
                "image_query_3": "laser beam puncture ground explosion destruction",
                "image_query_4": "cosmic explosion shockwave galaxy blast",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 13,
            },
            {
                "id": 3,
                "section_type": "cta",
                "title": "cta_internal",
                "narration": "Releasing energy equal to 10 million atomic bombs... which proves...",
                "image_query": "atomic bomb nuclear fireball shockwave apocalyptic",
                "image_query_2": "glowing nuclear fireball destruction cinematic",
                "image_query_3": "neutron star collision gravity shockwave",
                "image_query_4": "dark void universe space stars",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 4,
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
    print(f"PRODUCING ULTRA-RETENTION SHORT: {JOB['title']}")
    print("=" * 65)

    script = JOB["script"]
    words = len(" ".join(s["narration"] for s in script["sections"]).split())
    print(f"1. Script loaded: {words} words across {len(script['sections'])} sections (approx 22s spoken).")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading high-impact visual B-roll...")
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
