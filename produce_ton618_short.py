import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\ayush\.gemini\antigravity\scratch\youtube-agentic-ai-studio"
os.chdir(BASE_DIR)
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

JOB_ID = "ton_618_biggest_black_hole"
TITLE = "The Black Hole That Swallowed 66 Billion Suns"

SCRIPT = {
    "title": TITLE,
    "description": (
        "TON 618 is the largest supermassive black hole ever discovered, weighing 66 billion times the mass of our Sun. "
        "Its event horizon spans nearly 400 billion kilometers—making our entire solar system look like a microscopic speck of dust.\n\n"
        "#BlackHole #TON618 #Space #Universe #Astronomy #Physics #Shorts #YouTubeShorts"
    ),
    "tags": [
        "TON618",
        "BlackHole",
        "Space",
        "Universe",
        "Astronomy",
        "Cosmology",
        "Physics",
        "Shorts",
        "YouTubeShorts"
    ],
    "video_type": "shorts",
    "hook_badge": "BIGGEST OBJECT IN THE UNIVERSE",
    "end_badge": "COMMENT BELOW | SUBSCRIBE",
    "sections": [
        {
            "id": 1,
            "section_type": "hook",
            "title": "hook_internal",
            "narration": "This single black hole makes our entire solar system look like a speck of dust.",
            "image_query": "supermassive black hole",
            "image_query_2": "black hole",
            "image_query_3": "universe deep field",
            "image_query_4": "spiral galaxy hubble",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 4,
        },
        {
            "id": 2,
            "section_type": "content",
            "title": "content_internal",
            "narration": (
                "Meet TON 618. It weighs sixty-six billion times more than our Sun. "
                "Its event horizon spans nearly four hundred billion kilometers. "
                "If you dropped it where our Sun is, it would swallow Pluto eleven times over. "
                "Light itself takes weeks just to crawl across its shadow."
            ),
            "image_query": "solar system planets",
            "image_query_2": "pluto planet",
            "image_query_3": "nebula hubble",
            "image_query_4": "supermassive black hole",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 15,
        },
        {
            "id": 3,
            "section_type": "cta",
            "title": "cta_internal",
            "narration": "Does infinite scale terrify you? Comment below, because right now...",
            "image_query": "universe deep field",
            "image_query_2": "supernova",
            "image_query_3": "spiral galaxy hubble",
            "image_query_4": "black hole",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 6,
        },
    ],
}


def main():
    job_dir = os.path.join(config.OUTPUT_DIR, JOB_ID)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, "images"), exist_ok=True)

    print("=" * 65)
    print(f"PRODUCING VIRAL SHORT: {TITLE}")
    print("=" * 65)

    words = len(" ".join(s["narration"] for s in SCRIPT["sections"]).split())
    print(f"1. Script loaded: {words} words (approx 26-28s kinetic loop).")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(SCRIPT, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading high-contrast NASA cosmic B-roll...")
    image_map = download_images(SCRIPT, job_dir)

    print("\n3. Synthesizing voiceover narration (ElevenLabs George)...")
    config.VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
    audio_path = generate_narration(SCRIPT, job_dir)

    print("\n4. Mixing dark cosmic sub-bass pulse bed (16% volume)...")
    mixed_audio_path = os.path.join(job_dir, "narration_mixed.mp3")
    final_audio = mix_music_with_narration(
        narration_path=audio_path,
        output_path=mixed_audio_path,
        music_volume=0.16,
        library_dir=config.MUSIC_LIBRARY_DIR,
    )

    print("\n5. Compositing vertical 1080x1920 Short with kinetic captions...")
    video_path = create_video(SCRIPT, final_audio, job_dir, image_map, video_type="shorts")

    print("\n6. Designing high-contrast portrait thumbnail...")
    thumb_path = os.path.join(job_dir, "thumbnail.jpg")
    bg_candidate = next(
        (imgs[0] if isinstance(imgs, list) and imgs else imgs for imgs in image_map.values() if imgs),
        None,
    )
    render_thumb(
        style="impact",
        out_path=thumb_path,
        text="SWALLOWED *66 BILLION* SUNS",
        bg_path=bg_candidate,
        brand="BAEROZGAARMARD",
        portrait=True,
    )
    print("   ✓ Thumbnail rendered successfully.")

    # Save visual verification frames
    scratch_dir = r"C:\Users\ayush\.gemini\antigravity\brain\13fe73cd-9a68-4cba-830c-3451a17492d5\scratch"
    clip = VideoFileClip(video_path)
    Image.fromarray(clip.get_frame(1.2)).save(os.path.join(scratch_dir, "ton_hook.jpg"))
    Image.fromarray(clip.get_frame(12.0)).save(os.path.join(scratch_dir, "ton_mid.jpg"))
    Image.fromarray(clip.get_frame(min(24.0, clip.duration - 0.5))).save(os.path.join(scratch_dir, "ton_end.jpg"))
    clip.close()
    print("   ✓ Visual verification frames extracted.")

    print("\n7. Uploading directly to YouTube (Public, Live Now)...")
    yt_url = upload_to_youtube(
        script=SCRIPT,
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
    main()
