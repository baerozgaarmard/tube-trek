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

JOBS = [
    {
        "id": "earth_stops_spinning",
        "title": "What If Earth Stopped Spinning For 1 Second?",
        "publish_at": None,
        "privacy": "public",
        "schedule_label": "LIVE NOW (Public)",
        "script": {
            "title": "What If Earth Stopped Spinning For 1 Second?",
            "description": "If the Earth stopped spinning for just 1 second, the physical consequences would instantly end civilization. Here is the terrifying physics.",
            "tags": ["Earth", "Space", "Physics", "Science", "Shorts", "YouTubeShorts"],
            "video_type": "shorts",
            "sections": [
                {
                    "id": 1,
                    "section_type": "hook",
                    "title": "hook_internal",
                    "narration": "If the Earth stopped spinning for just one second, nobody survives to see second number two.",
                    "image_query": "planet earth rotating in space atmosphere",
                    "image_query_2": "earth from space dark blue globe stars",
                    "image_query_3": "supersonic shockwave blast sky clouds",
                    "image_query_4": "apocalyptic destruction earth disaster cinematic",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
                {
                    "id": 2,
                    "section_type": "content",
                    "title": "content_internal",
                    "narration": "At the equator, the planet spins at one thousand miles per hour. If it suddenly halted, everything not bolted down—cities, oceans, and entire continents—would violently launch eastward at supersonic speed, ripped apart by supersonic shockwaves.",
                    "image_query": "skyscrapers collapsing supersonic shockwave city",
                    "image_query_2": "megatsunami massive ocean wave swallowing city",
                    "image_query_3": "earthquake earth crust cracking magma lava",
                    "image_query_4": "destroyed apocalyptic city ruins landscape",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 14,
                },
                {
                    "id": 3,
                    "section_type": "cta",
                    "title": "cta_internal",
                    "narration": "Miles-high tsunamis would drown the globe before gravity pulled the wreckage back together. If this broke your brain, subscribe and hit the bell for daily cosmic rabbit holes — tell me: where would you hide?",
                    "image_query": "planet earth water flood oceans space",
                    "image_query_2": "space nebula cosmic universe stars deep",
                    "image_query_3": "infinite universe deep cosmos portal",
                    "image_query_4": "night sky milky way stars galaxy",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 7,
                },
            ],
        },
    },
    {
        "id": "light_never_experiences_time",
        "title": "Why Light Never Experiences Time",
        "publish_at": "2026-11-10T23:30:00Z",  # 5:00 AM IST on Nov 11
        "privacy": "private",
        "schedule_label": "SCHEDULED for 5:00 AM IST (Tomorrow)",
        "script": {
            "title": "Why Light Never Experiences Time",
            "description": "According to Einstein's special relativity, light experiences zero time. From the perspective of a photon, the Big Bang and right now are the exact same instant.",
            "tags": ["SpeedOfLight", "TimeTravel", "Einstein", "Physics", "Science", "Shorts", "YouTubeShorts"],
            "video_type": "shorts",
            "sections": [
                {
                    "id": 1,
                    "section_type": "hook",
                    "title": "hook_internal",
                    "narration": "If light had eyes, the entire universe would begin and end in zero seconds.",
                    "image_query": "laser beam light traveling through dark space",
                    "image_query_2": "speed of light warp speed stars hyperspace",
                    "image_query_3": "glowing photon quantum particle physics neon",
                    "image_query_4": "einstein relativity spacetime curvature",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 5,
                },
                {
                    "id": 2,
                    "section_type": "content",
                    "title": "content_internal",
                    "narration": "Einstein proved that the faster you move through space, the slower you move through time. At the speed of light, time stops completely. A photon created in the Big Bang thirteen billion years ago experiences its birth and its collision with your eye at the exact same instant.",
                    "image_query": "clock melting time dilation warp physics",
                    "image_query_2": "big bang cosmic microwave background universe explosion",
                    "image_query_3": "human eye pupil macro close up iris reflection",
                    "image_query_4": "infinite cosmos galaxy stars glowing abstract",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 15,
                },
                {
                    "id": 3,
                    "section_type": "cta",
                    "title": "cta_internal",
                    "narration": "From light's perspective, our universe has already ended. If this blew your mind, hit subscribe and ring the bell — tell me: does time even exist?",
                    "image_query": "deep space portal light glowing infinite universe",
                    "image_query_2": "black hole event horizon time stopping",
                    "image_query_3": "stars cosmic galaxy milky way night sky",
                    "image_query_4": "quantum mechanics digital matrix reality code",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
            ],
        },
    },
]

def run_batch():
    results = []
    print("\n" + "=" * 65)
    print("  BATCH PRODUCTION: 2 VIRAL BLUEPRINT SHORTS")
    print("=" * 65 + "\n")

    for idx, job in enumerate(JOBS, start=1):
        job_dir = os.path.join(config.OUTPUT_DIR, job["id"])
        os.makedirs(job_dir, exist_ok=True)
        img_dir = os.path.join(job_dir, "images")
        os.makedirs(img_dir, exist_ok=True)

        print(f"\n[{idx}/2] >>> PRODUCING: {job['title']} <<<")
        print(f"      Schedule: {job['schedule_label']}")

        script = job["script"]
        words = len(" ".join(s["narration"] for s in script["sections"]).split())
        print(f"  1. Script loaded: {words} words across {len(script['sections'])} sections.")

        with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)

        # 2. Stock images
        print("  2. Downloading visual B-roll...")
        image_map = download_images(script, job_dir)

        # 3. Narration voiceover
        print("  3. Synthesizing voiceover narration (Edge TTS)...")
        audio_path = generate_narration(script, job_dir)

        # 4. Composite vertical 1080x1920 video
        print("  4. Compositing vertical video with kinetic captions (MoviePy)...")
        video_path = create_video(script, audio_path, job_dir, image_map, video_type="shorts")

        # 5. Render Thumbnail
        print("  5. Designing high-contrast portrait thumbnail...")
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
                text=job["title"],
                bg_path=bg_candidate,
                brand="BAEROZGAARMARD",
                portrait=True,
            )
            print("     ✓ Thumbnail rendered successfully.")
        except Exception as e:
            print(f"     ⚠ Thumbnail rendering fallback: {e}")

        # 6. Upload to YouTube
        print(f"  6. Uploading to YouTube ({job['schedule_label']})...")
        yt_url = upload_to_youtube(
            script=script,
            video_path=video_path,
            thumbnail_path=thumb_path if os.path.exists(thumb_path) else None,
            publish_at=job["publish_at"],
            privacy_status=job["privacy"],
        )

        res_entry = {
            "title": job["title"],
            "url": yt_url,
            "schedule": job["schedule_label"],
            "publish_at": job["publish_at"],
            "words": words,
            "video_path": video_path,
        }
        results.append(res_entry)
        print(f"\n  ✓ COMPLETED [{idx}/2]: {yt_url}\n")

    # Save summary
    out_summary = os.path.join(config.OUTPUT_DIR, "batch_two_results.json")
    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 65)
    print("  ALL 2 VIDEOS SUCCESSFULLY PRODUCED & UPLOADED/SCHEDULED!")
    print("=" * 65)
    for r in results:
        print(f"  * {r['title']} -> {r['url']} ({r['schedule']})")

if __name__ == "__main__":
    run_batch()
