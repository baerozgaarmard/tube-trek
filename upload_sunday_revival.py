import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\ayush\.gemini\antigravity\scratch\youtube-agentic-ai-studio"
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import config
from uploader.youtube import upload_to_youtube

JOB_DIR = os.path.join(config.OUTPUT_DIR, "sunday_revival")
video_path = os.path.join(JOB_DIR, "final_short.mp4")
thumb_path = os.path.join(JOB_DIR, "thumbnail.jpg")
script_path = os.path.join(JOB_DIR, "script.json")

with open(script_path, "r", encoding="utf-8") as f:
    script = json.load(f)

print("=" * 60)
print(f"UPLOADING SUNDAY REVIVAL SHORT: {script['title']}")
print(f"File: {video_path} ({os.path.getsize(video_path)} bytes)")
print("=" * 60)

# Delete expired pickle so InstalledAppFlow launches a fresh browser authentication
pickle_path = os.path.join(BASE_DIR, "youtube_token.pickle")
if os.path.exists(pickle_path):
    try:
        import pickle
        with open(pickle_path, "rb") as pf:
            c = pickle.load(pf)
        if not c.valid and c.expired:
            print("[*] Removing expired 7-day test token to trigger fresh Google sign-in...")
            os.remove(pickle_path)
    except Exception:
        pass

print("[*] Launching YouTube Upload (Public, Live Now)...")
url = upload_to_youtube(
    script=script,
    video_path=video_path,
    thumbnail_path=thumb_path if os.path.exists(thumb_path) else None,
    publish_at=None,
    privacy_status="public",
)

print("\n" + "=" * 60)
print(f"🚀 SUCCESS! Video uploaded live to YouTube: {url}")
print("=" * 60)
