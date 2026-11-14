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

JOB_ID = "why_paper_cuts_hurt"
TITLE = "Why Paper Cuts Hurt More Than A Knife"

SCRIPT = {
    "title": TITLE,
    "description": (
        "Why does a tiny, bloodless paper cut cause agonizing, burning pain compared to a clean razor cut? "
        "Under a scanning electron microscope, paper is not a sharp blade—it is a microscopic jagged saw that tears "
        "flesh instead of slicing it. Combined with the highest nerve density in your fingertips and exposed chemical bleaches, "
        "here is the terrifying science of paper cuts.\n\n"
        "Subscribe for daily science deep-dives and tell us your worst paper cut story below!\n\n"
        "#Science #Biology #HumanBody #Physics #Microscope #Shorts #YouTubeShorts"
    ),
    "tags": [
        "Science",
        "Biology",
        "HumanBody",
        "Microscope",
        "PaperCut",
        "Physics",
        "Medicine",
        "Shorts",
        "YouTubeShorts"
    ],
    "video_type": "shorts",
    "hook_badge": "MICROSCOPIC CHAINSAW",
    "end_badge": "HAPPENED TO YOU? | SUBSCRIBE",
    "sections": [
        {
            "id": 1,
            "section_type": "hook",
            "title": "hook_internal",
            "narration": "A tiny paper cut hurts ten times worse than a razor blade. And your microscope proves why.",
            "image_query": "microscope",
            "image_query_2": "knife",
            "image_query_3": "paper",
            "image_query_4": "laboratory",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 5,
        },
        {
            "id": 2,
            "section_type": "content",
            "title": "content_internal",
            "narration": (
                "Under a scanning electron microscope, paper isn't a blade—it's a microscopic jagged saw. "
                "Instead of slicing cleanly like steel, paper shreds your skin cells. "
                "Because paper cuts rarely bleed, your fingertip's dense nerve endings stay exposed to air and chemical bleaches, "
                "firing agonizing pain signals for hours."
            ),
            "image_query": "skin",
            "image_query_2": "microscope",
            "image_query_3": "blade",
            "image_query_4": "paper",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 15,
        },
        {
            "id": 3,
            "section_type": "cta",
            "title": "cta_internal",
            "narration": "Have you ever had a cut worse than paper? Subscribe for daily reality checks, and tell me below—because...",
            "image_query": "laboratory",
            "image_query_2": "paper",
            "image_query_3": "knife",
            "image_query_4": "microscope",
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
    print(f"1. Script loaded: {words} words (approx 27-29s kinetic loop).")

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(SCRIPT, f, indent=2, ensure_ascii=False)

    print("\n2. Downloading visual B-roll...")
    image_map = download_images(SCRIPT, job_dir)

    print("\n3. Synthesizing voiceover narration (ElevenLabs George)...")
    config.VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
    audio_path = generate_narration(SCRIPT, job_dir)

    print("\n4. Mixing subtle tension underscore (14% volume)...")
    mixed_audio_path = os.path.join(job_dir, "narration_mixed.mp3")
    final_audio = mix_music_with_narration(
        narration_path=audio_path,
        output_path=mixed_audio_path,
        music_volume=0.14,
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
        text="WHY PAPER CUTS *HURT* MORE",
        bg_path=bg_candidate,
        brand="BAEROZGAARMARD",
        portrait=True,
    )
    print("   ✓ Thumbnail rendered successfully.")

    # Save visual verification frames
    scratch_dir = r"C:\Users\ayush\.gemini\antigravity\brain\13fe73cd-9a68-4cba-830c-3451a17492d5\scratch"
    clip = VideoFileClip(video_path)
    Image.fromarray(clip.get_frame(1.2)).save(os.path.join(scratch_dir, "paper_hook.jpg"))
    Image.fromarray(clip.get_frame(12.0)).save(os.path.join(scratch_dir, "paper_mid.jpg"))
    Image.fromarray(clip.get_frame(min(24.0, clip.duration - 0.5))).save(os.path.join(scratch_dir, "paper_end.jpg"))
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
