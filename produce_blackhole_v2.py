import json
import os
import shutil
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
from video.creator import create_video
from video.thumbnail import render as render_thumb

SRC_DIR = os.path.join(config.OUTPUT_DIR, "inside_a_black_hole_universe")
JOB_ID = "living_inside_black_hole"
TITLE = "Are We Living Inside A Black Hole?"

SCRIPT = {
    "title": TITLE,
    "description": (
        "If you plug the observable universe's mass into Einstein's black hole "
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
            "image_query": "black hole",
            "image_query_2": "black hole space",
            "image_query_3": "supernova",
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
            "image_query_2": "nebula hubble",
            "image_query_3": "galaxy stars",
            "image_query_4": "space telescope stars",
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
            "image_query": "supernova explosion star",
            "image_query_2": "neutron star space",
            "image_query_3": "deep space cosmos",
            "image_query_4": "black hole galaxy",
            "bullet_points": [],
            "caption_text": "",
            "duration_seconds": 8,
        },
    ],
}


def main():
    job_dir = os.path.join(config.OUTPUT_DIR, JOB_ID)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, "images"), exist_ok=True)

    # Reuse synthesized ElevenLabs audio, word timings, and mixed music bed
    for fname in ("narration.mp3", "narration.srt", "narration_words.json", "narration_mixed.mp3"):
        src = os.path.join(SRC_DIR, fname)
        dst = os.path.join(job_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(SCRIPT, f, indent=2, ensure_ascii=False)

    print("1. Downloading verified NASA cosmic visuals...")
    image_map = download_images(SCRIPT, job_dir)

    print("\n2. Rendering v2 1080x1920 vertical video...")
    final_audio = os.path.join(job_dir, "narration_mixed.mp3")
    video_path = create_video(SCRIPT, final_audio, job_dir, image_map, video_type="shorts")

    print("\n3. Rendering Impact thumbnail over real NASA black hole imagery...")
    thumb_path = os.path.join(job_dir, "thumbnail.jpg")
    bg_candidate = next(
        (imgs[0] if isinstance(imgs, list) and imgs else imgs for imgs in image_map.values() if imgs),
        None,
    )
    render_thumb(
        style="impact",
        out_path=thumb_path,
        text="LIVING *INSIDE* A BLACK HOLE?",
        bg_path=bg_candidate,
        brand="BAEROZGAARMARD",
        portrait=True,
    )

    # Save visual verification frames before upload
    scratch_dir = r"C:\Users\ayush\.gemini\antigravity\brain\13fe73cd-9a68-4cba-830c-3451a17492d5\scratch"
    clip = VideoFileClip(video_path)
    Image.fromarray(clip.get_frame(1.2)).save(os.path.join(scratch_dir, "v2_hook.jpg"))
    Image.fromarray(clip.get_frame(14.0)).save(os.path.join(scratch_dir, "v2_mid.jpg"))
    Image.fromarray(clip.get_frame(min(25.2, clip.duration - 0.5))).save(os.path.join(scratch_dir, "v2_end.jpg"))
    clip.close()
    print("✓ Render + verification frames complete:", video_path)


if __name__ == "__main__":
    main()
