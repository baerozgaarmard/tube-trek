"""
TikTok Content Posting API (v2) Client — Tube Trek
Allows direct, autonomous video posting to TikTok via official TikTok Open API.
API Specs: https://developers.tiktok.com/doc/content-posting-api-get-started/
"""
import json
import math
import os
import requests
import config

TIKTOK_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"


def is_tiktok_configured() -> bool:
    token = os.getenv("TIKTOK_ACCESS_TOKEN", "").strip()
    return bool(token) and not token.upper().startswith("YOUR_")


def upload_to_tiktok(script: dict, video_path: str, privacy_level: str = "PUBLIC_TO_EVERYONE",
                     disable_duet: bool = False, disable_stitch: bool = False,
                     disable_comment: bool = False) -> str | None:
    """
    Publish a 1080x1920 Short directly to TikTok.
    Returns the TikTok publish_id or None if unconfigured.
    """
    token = os.getenv("TIKTOK_ACCESS_TOKEN", "").strip()
    if not is_tiktok_configured():
        print("   ℹ TikTok token not set (set TIKTOK_ACCESS_TOKEN in .env) — skipping TikTok upload.")
        return None

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size = os.path.getsize(video_path)
    title = script.get("title", "Autonomous Viral Short")
    tags = " ".join(f"#{t}" for t in script.get("tags", ["Shorts", "Viral"]))
    caption = f"{title}\n\n{tags}"[:2200]

    # Max chunk size 10 MB, min chunk size 5 MB
    chunk_size = min(file_size, 10 * 1024 * 1024)
    total_chunk_count = math.ceil(file_size / chunk_size)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    payload = {
        "post_info": {
            "title": caption,
            "privacy_level": privacy_level,
            "disable_duet": disable_duet,
            "disable_stitch": disable_stitch,
            "disable_comment": disable_comment,
            "video_cover_timestamp_ms": 1000,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count,
        },
    }

    print("   → Initializing TikTok post…")
    try:
        r = requests.post(TIKTOK_INIT_URL, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        error = data.get("error", {})
        if error.get("code") != "ok":
            print(f"   ⚠ TikTok init error: {error.get('message', 'Unknown error')}")
            return None

        publish_id = data.get("data", {}).get("publish_id")
        upload_url = data.get("data", {}).get("upload_url")
        if not upload_url:
            print("   ⚠ TikTok did not return an upload URL.")
            return None

        # Upload video in chunks
        print("   → Uploading video chunks to TikTok…")
        with open(video_path, "rb") as f:
            for idx in range(total_chunk_count):
                chunk_data = f.read(chunk_size)
                start_byte = idx * chunk_size
                end_byte = start_byte + len(chunk_data) - 1
                chunk_headers = {
                    "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                    "Content-Type": "video/mp4",
                }
                up_resp = requests.put(upload_url, headers=chunk_headers, data=chunk_data, timeout=60)
                up_resp.raise_for_status()

        print(f"   ✓ Video successfully submitted to TikTok (publish_id: {publish_id})")
        return f"https://www.tiktok.com/publish/{publish_id}"

    except Exception as e:
        print(f"   ⚠ TikTok upload failed: {e}")
        return None
