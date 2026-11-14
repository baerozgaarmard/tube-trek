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

JOB_ID = "watch_the_universe_die"
TITLE = "Inside A Black Hole, You Watch The Universe Die"

SCRIPT = {
    "title": TITLE,
    "description": (
        "According to Einstein's general relativity, extreme gravitational time dilation near a black hole's "
        "event horizon causes external time to accelerate toward infinity. If you looked back out, you would watch "
        "trillions of years of cosmic history—stars dying, galaxies colliding, and the final heat death of the universe—"
        "flash before your eyes in seconds.\n\n"
        "Would you take the one-way trip to witness the end of time? Comment below and subscribe for daily cosmic rabbit holes.\n\n"
        "#BlackHole #TimeDilation #Space #Astronomy #Physics #Einstein #Shorts #YouTubeShorts"
    ),
    "tags": [
        "BlackHole",
        "TimeDilation",
        "Einstein",
        "Space",
        "Universe",
        "Cosmology",
        "Astronomy",
        "Physics",
        "Shorts",
        "YouTubeShorts"
    ],
    "video_type": "shorts",
    "hook_badge": "EINSTEIN'S TIME ACCELERATION",
    "end_badge": "WOULD YOU JUMP? | SUBSCRIBE",
    "sections": [
        {
            "id": 1,
            "section_type": "hook",
            "title": "hook_internal",
            "narration": "If you fall into a supermassive black hole, you watch the entire universe die in seconds.",
            "image_query": "supermassive black hole",
            "image_query_2": "black hole",
            "image_query_3": "spiral galaxy hubble",
            "image_query_4": "universe deep field",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 5,
        },
        {
            "id": 2,
            "section_type": "content",
            "title": "content_internal",
            "narration": (
                "Einstein proved that gravity bends time. Near the event horizon, time outside accelerates toward infinity. "
                "If you turn around and look back, you watch trillions of years flash by: "
                "stars burning out, galaxies colliding, and the final death of the cosmos before you reach the singularity."
            ),
            "image_query": "universe deep field",
            "image_query_2": "supernova star explosion",
            "image_query_3": "colliding galaxies hubble",
            "image_query_4": "nebula hubble",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 15,
        },
        {
            "id": 3,
            "section_type": "cta",
            "title": "cta_internal",
            "narration": "Would you take the one-way trip to see the end of reality? Subscribe to join the crew, and tell me below—because...",
            "image_query": "stars milky way space",
            "image_query_2": "supermassive black hole",
            "image_query_3": "spiral galaxy hubble",
            "image_query_4": "black hole",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 7,
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
    print(f"1. Script loaded: {words} words (approx 27-29s kinetic loop).")

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
        text="YOU WATCH THE *UNIVERSE* DIE",
        bg_path=bg_candidate,
        brand="BAEROZGAARMARD",
        portrait=True,
    )
    print("   ✓ Thumbnail rendered successfully.")

    # Save visual verification frames
    scratch_dir = r"C:\Users\ayush\.gemini\antigravity\brain\13fe73cd-9a68-4cba-830c-3451a17492d5\scratch"
    clip = VideoFileClip(video_path)
    Image.fromarray(clip.get_frame(1.2)).save(os.path.join(scratch_dir, "die_hook.jpg"))
    Image.fromarray(clip.get_frame(12.0)).save(os.path.join(scratch_dir, "die_mid.jpg"))
    Image.fromarray(clip.get_frame(min(24.0, clip.duration - 0.5))).save(os.path.join(scratch_dir, "die_end.jpg"))
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
