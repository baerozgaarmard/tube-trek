import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import config
from uploader.youtube import upload_to_youtube
from video.creator import create_video
from video.narrator import generate_narration
from video.stock import download_images
from video.thumbnail import render as render_thumb

JOBS = [
    {
        "id": "video_1",
        "title": "Why Black Holes Kill You With Time",
        "publish_at": None,
        "privacy": "public",
        "schedule_label": "LIVE NOW (Public)",
        "script": {
            "title": "Why Black Holes Kill You With Time",
            "description": "If you fall into a black hole, you don't die of gravity. Spacetime stretches your timeline until reality rips in half.",
            "tags": ["Space", "BlackHole", "Physics", "Science", "Shorts", "YouTubeShorts"],
            "video_type": "shorts",
            "sections": [
                {
                    "id": 1,
                    "section_type": "hook",
                    "title": "hook_internal",
                    "narration": "If you fall into a black hole, you don't die of gravity. You die of time.",
                    "image_query": "black hole event horizon spacetime",
                    "image_query_2": "cosmic gravity deep space stars",
                    "image_query_3": "accretion disk black hole glowing",
                    "image_query_4": "distorted spacetime light gravitational lens",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
                {
                    "id": 2,
                    "section_type": "content",
                    "title": "content_internal",
                    "narration": "Gravitational time dilation is so extreme at the event horizon that your feet experience tomorrow while your head is stuck in yesterday. Spacetime stretches your timeline until reality rips in half.",
                    "image_query": "time dilation clock warp physics",
                    "image_query_2": "black hole sucking matter space",
                    "image_query_3": "galaxy spiral stars deep field",
                    "image_query_4": "spacetime curvature cosmos nebula",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 15,
                },
                {
                    "id": 3,
                    "section_type": "cta",
                    "title": "cta_internal",
                    "narration": "Before you hit the center, you witness the entire future of the universe end in a single flash.",
                    "image_query": "universe big crunch explosion light",
                    "image_query_2": "stars cosmic supernova blast",
                    "image_query_3": "infinite universe deep cosmos",
                    "image_query_4": "event horizon light ring black hole",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
            ],
        },
    },
    {
        "id": "video_2",
        "title": "Why Aliens Refuse to Send Radio Signals",
        "publish_at": "2026-10-28T23:30:00Z",  # 5:00 AM IST on 2026-10-29
        "privacy": "private",
        "schedule_label": "SCHEDULED for 5:00 AM IST (Tomorrow)",
        "script": {
            "title": "Why Aliens Refuse to Send Radio Signals",
            "description": "The scariest answer to the Fermi paradox isn't that aliens are dead — it's that they are terrified. Dark Forest Theory explained.",
            "tags": ["FermiParadox", "Aliens", "DarkForest", "Space", "Science", "Shorts", "YouTubeShorts"],
            "video_type": "shorts",
            "sections": [
                {
                    "id": 1,
                    "section_type": "hook",
                    "title": "hook_internal",
                    "narration": "The scariest answer to the Fermi paradox isn't that aliens are dead — it's that they are terrified.",
                    "image_query": "deep space radio telescope galaxy",
                    "image_query_2": "alien dark forest universe",
                    "image_query_3": "mysterious cosmic silence stars",
                    "image_query_4": "observatory dish night sky",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
                {
                    "id": 2,
                    "section_type": "content",
                    "title": "content_internal",
                    "narration": "Under the Dark Forest theory, the universe is a silent jungle filled with apex predators. Any civilization foolish enough to broadcast its location is instantly eliminated by weapons moving at lightspeed.",
                    "image_query": "dark jungle forest universe cosmic",
                    "image_query_2": "stealth spaceship alien fleet",
                    "image_query_3": "laser weapon supernova blast galaxy",
                    "image_query_4": "destroyed alien planet ruins",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 15,
                },
                {
                    "id": 3,
                    "section_type": "cta",
                    "title": "cta_internal",
                    "narration": "Every telescope in space finds total silence because everyone knows: never shout in the dark.",
                    "image_query": "radio telescope dish stars milky way",
                    "image_query_2": "deep space silent galaxy",
                    "image_query_3": "earth satellite broadcasting signals",
                    "image_query_4": "cosmic horizon dark stars",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
            ],
        },
    },
    {
        "id": "video_3",
        "title": "1 Quantum Rule Proves the Simulation",
        "publish_at": "2026-10-29T08:30:00Z",  # 2:00 PM IST on 2026-10-29
        "privacy": "private",
        "schedule_label": "SCHEDULED for 2:00 PM IST (Tomorrow)",
        "script": {
            "title": "1 Quantum Rule Proves the Simulation",
            "description": "There is 1 rule in quantum physics that only makes sense if reality is conserving RAM. Wave-particle duality and observer effect explained.",
            "tags": ["SimulationTheory", "QuantumPhysics", "Matrix", "Science", "Shorts", "YouTubeShorts"],
            "video_type": "shorts",
            "sections": [
                {
                    "id": 1,
                    "section_type": "hook",
                    "title": "hook_internal",
                    "narration": "There is 1 rule in quantum physics that only makes sense if reality is conserving RAM.",
                    "image_query": "quantum physics wave particles glowing",
                    "image_query_2": "computer matrix code numbers falling",
                    "image_query_3": "abstract simulation reality digital",
                    "image_query_4": "neon quantum mechanics laboratory",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 6,
                },
                {
                    "id": 2,
                    "section_type": "content",
                    "title": "content_internal",
                    "narration": "In the double-slit experiment, particles only choose a physical state when a detector is watching. The moment you look away, reality dissolves back into mathematical probability — exactly like video game rendering.",
                    "image_query": "double slit experiment physics light wave",
                    "image_query_2": "particles quantum interference pattern",
                    "image_query_3": "video game rendering wireframe mesh 3d",
                    "image_query_4": "matrix glitch code reality breaking",
                    "bullet_points": [],
                    "caption_text": "",
                    "duration_seconds": 15,
                },
                {
                    "id": 3,
                    "section_type": "cta",
                    "title": "cta_internal",
                    "narration": "The universe never renders what nobody is looking at... to keep the simulation from crashing.",
                    "image_query": "virtual reality simulation matrix world",
                    "image_query_2": "digital universe code simulation grid",
                    "image_query_3": "quantum observer eye light ray",
                    "image_query_4": "infinite void black cyber space",
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
    print(f"\n{'='*65}\n  STARTING BATCH PRODUCTION: 3 VIRAL SHORTS\n{'='*65}\n")

    for idx, job in enumerate(JOBS, start=1):
        job_dir = os.path.join(config.OUTPUT_DIR, job["id"])
        os.makedirs(job_dir, exist_ok=True)
        img_dir = os.path.join(job_dir, "images")
        os.makedirs(img_dir, exist_ok=True)

        print(f"\n[{idx}/3] >>> PRODUCING: {job['title']} <<<")
        print(f"      Schedule: {job['schedule_label']}")

        script = job["script"]
        words = len(" ".join(s["narration"] for s in script["sections"]).split())
        print(f"  1. Script loaded: {words} words across {len(script['sections'])} sections")

        with open(os.path.join(job_dir, "script.json"), "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)

        # 2. Stock images
        print("  2. Downloading visual B-roll...")
        image_map = download_images(script, job_dir)

        # 3. Narration voiceover
        print("  3. Synthesizing voiceover narration (Edge TTS)...")
        audio_path = generate_narration(script, job_dir)

        # 4. Composite vertical 1080x1920 video
        print("  4. Compositing video with animated captions (MoviePy)...")
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
            print("     ✓ Thumbnail rendered successfully")
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
        print(f"\n  ✓ COMPLETED [{idx}/3]: {yt_url}\n")

    # Save summary
    out_summary = os.path.join(config.OUTPUT_DIR, "batch_results.json")
    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 65)
    print("  ALL 3 VIDEOS SUCCESSFULLY PRODUCED & UPLOADED/SCHEDULED!")
    print("=" * 65)
    for r in results:
        print(f"  * {r['title']} -> {r['url']} ({r['schedule']})")


if __name__ == "__main__":
    run_batch()
