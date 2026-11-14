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

script_path = os.path.join(config.OUTPUT_DIR, "script.json")
video_path = os.path.join(config.OUTPUT_DIR, "final_short.mp4")
thumb_path = os.path.join(config.OUTPUT_DIR, "thumbnail.jpg")

with open(script_path, "r", encoding="utf-8") as f:
    script = json.load(f)

print(f"Uploading Video: {script['title']}")
print(f"File: {video_path} ({os.path.getsize(video_path)} bytes)")

url = upload_to_youtube(script, video_path, thumb_path)
print(f"\nSUCCESS! Video uploaded live at: {url}")
