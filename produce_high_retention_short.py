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
from video.music import mix_music_with_narration
from video.creator import create_video
from video.thumbnail import render as render_thumb
from uploader.youtube import upload_to_youtube

# Use ElevenLabs captivating deep storyteller voice for studio-grade delivery + exact word alignment
config.VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

JOB = {
    "id": "inside_a_black_hole_universe",
    "title": "You Are Inside A Black Hole Right Now",
    "hook_badge": "EINSTEIN'S SCARIEST EQUATION",
    "end_badge": "COMMENT 1 OR 2  |  SUBSCRIBE",
    "script": {
        "title": "You Are Inside A Black Hole Right Now",
        "description": (
            "If you plug the entire observable universe's mass into Einstein's black hole "
            "equation, the Schwarzschild radius matches our cosmic horizon at 14 billion light-years. "
            "Are we living inside the event horizon of another universe's black hole? "
            "Comment 1 for YES or 2 for COINCIDENCE.\n\n"
            "#BlackHole #Cosmology #Physics #Space #Shorts #YouTubeShorts"
        ),
        "tags": ["BlackHole", "Cosmology", "Einstein", "Physics", "Space", "Astrophysics", "Shorts", "YouTubeShorts"],
        "video_type": "shorts",
        "hook_badge": "EINSTEIN'S SCARIEST EQUATION",
        "end_badge": "COMMENT 1 OR 2  |  SUBSCRIBE",
        "sections": [
            {
                "id": 1,
                "section_type": "hook",
                "title": "hook_internal",
                "narration": "You are probably trapped inside a giant black hole.",
                "image_query": "black hole space",
                "image_query_2": "universe stars",
                "image_query_3": "dark cosmos",
                "image_query_4": "galaxy nebula",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 4,
            },
            {
                "id": 2,
                "section_type": "content",
                "title": "content_internal",
                "narration": (
                    "Plug the entire observable universe's mass into Einstein's black hole equation. "
                    "Its event horizon lands at fourteen billion light-years, matching our exact cosmic horizon. "
                    "Beyond that border, galaxies flee faster than light, sealing us in forever."
                ),
                "image_query": "spiral galaxy",
                "image_query_2": "deep space nebula",
                "image_query_3": "space stars night",
                "image_query_4": "solar eclipse",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 13,
            },
            {
                "id": 3,
                "section_type": "cta",
                "title": "cta_internal",
                "narration": (
                    "Did our Big Bang happen inside a collapsing cosmic star? "
                    "Comment 1 if yes, 2 if it's coincidence—because right now..."
                ),
                "image_query": "supernova space",
                "image_query_2": "milky way night",
                "image_query_3": "cosmos portal",
                "image_query_4": "black hole galaxy",
                "bullet_points": [],
                "caption_text": "",
                "duration_seconds": 8,
            },
        ],
    },
}


def run_production():
    job_dir = os.path.join(config.OUTPUT_DIR, JOB["id"])
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, "images"), exist_ok=True)

    print("=" * 65)
    print(f"PRODUCING HIGH-RETENTION SHORT: {JOB['title']}")
    print("=" * 65)

    script = JOB["script"]
    words = len(" ".join(s["narration"] for s in script["sections"]).split())
    print(f"1. Script loaded: {words} words (target 24-26s kinetic loop).")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading high-contrast cosmic visuals (for 1.25s cuts)...")
    image_map = download_images(script, job_dir)

    print("\n3. Synthesizing voiceover + exact word timings...")
    audio_path = generate_narration(script, job_dir)

    print("\n4. Mixing dark cosmic sub-bass pulse underscore...")
    mixed_path = os.path.join(job_dir, "narration_mixed.mp3")
    final_audio = mix_music_with_narration(
        narration_path=audio_path,
        output_path=mixed_path,
        music_volume=0.16,
        library_dir=config.MUSIC_LIBRARY_DIR,
    )

    print("\n5. Compositing 1080x1920 vertical Short (word-highlighted kinetic captions)...")
    video_path = create_video(script, final_audio, job_dir, image_map, video_type="shorts")

    print("\n6. Rendering high-contrast portrait Impact thumbnail...")
    thumb_path = os.path.join(job_dir, "thumbnail.jpg")
    bg_candidate = next(
        (imgs[0] if isinstance(imgs, list) and imgs else imgs for imgs in image_map.values() if imgs),
        None,
    )
    try:
        render_thumb(
            style="impact",
            out_path=thumb_path,
            text="YOU ARE *INSIDE* A BLACK HOLE",
            bg_path=bg_candidate,
            brand="BAEROZGAARMARD",
            portrait=True,
        )
        print("   ✓ Thumbnail rendered successfully.")
    except Exception as e:
        print(f"   ⚠ Thumbnail rendering fallback: {e}")

    print("\n7. Uploading LIVE (Public) to YouTube...")
    yt_url = upload_to_youtube(
        script=script,
        video_path=video_path,
        thumbnail_path=thumb_path if os.path.exists(thumb_path) else None,
        publish_at=None,
        privacy_status="public",
    )

    result = {"title": JOB["title"], "url": yt_url, "words": words, "video_path": video_path}
    with open(os.path.join(job_dir, "upload_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 65)
    print(f"🚀 LIVE ON YOUTUBE: {yt_url}")
    print("=" * 65)


if __name__ == "__main__":
    run_production()
