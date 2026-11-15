"""
Instagram Reels Meta Graph API Client — Tube Trek
Allows direct publishing of 9:16 vertical Reels via Meta Graph API v19.0+.
API Docs: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/
"""
import os
import time
import requests
import config

GRAPH_API_VERSION = "v19.0"
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def is_instagram_configured() -> bool:
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
    acc_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()
    return bool(token) and bool(acc_id) and not token.upper().startswith("YOUR_")


def upload_to_instagram(script: dict, video_path: str, caption_suffix: str = "") -> str | None:
    """
    Publish a 1080x1920 Reel to Instagram via Meta Graph API.
    Returns Instagram media ID or permalink on success.
    """
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()

    if not is_instagram_configured():
        print("   ℹ Instagram tokens not set (set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env) — skipping Instagram upload.")
        return None

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size = os.path.getsize(video_path)
    title = script.get("title", "Autonomous Viral Reel")
    tags = " ".join(f"#{t}" for t in script.get("tags", ["Reels", "Explore"]))
    caption = f"{title}\n\n{tags} {caption_suffix}"[:2200]

    # Step 1: Create Resumable Upload Session
    print("   → Creating Instagram Reels container…")
    init_url = f"{GRAPH_BASE_URL}/{account_id}/media"
    init_params = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "caption": caption,
        "access_token": token,
    }

    try:
        r = requests.post(init_url, params=init_params, timeout=20)
        r.raise_for_status()
        init_data = r.json()
        container_id = init_data.get("id")
        upload_uri = init_data.get("uri")

        if not upload_uri:
            print("   ⚠ Instagram did not return a resumable upload URI.")
            return None

        # Step 2: Upload Video Bytes
        print("   → Streaming video bytes to Instagram server…")
        with open(video_path, "rb") as f:
            video_bytes = f.read()

        up_headers = {
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(file_size),
        }
        up_resp = requests.post(upload_uri, headers=up_headers, data=video_bytes, timeout=120)
        up_resp.raise_for_status()

        # Step 3: Wait for video processing
        print("   → Waiting for Instagram video processing…")
        status_url = f"{GRAPH_BASE_URL}/{container_id}"
        for attempt in range(12):
            time.sleep(5)
            chk = requests.get(status_url, params={"fields": "status_code", "access_token": token}, timeout=15)
            if chk.ok:
                status_code = chk.json().get("status_code")
                if status_code == "FINISHED":
                    break
                elif status_code == "ERROR":
                    print("   ⚠ Instagram video processing returned ERROR status.")
                    return None

        # Step 4: Publish Container
        print("   → Publishing Reel to profile…")
        publish_url = f"{GRAPH_BASE_URL}/{account_id}/media_publish"
        pub_resp = requests.post(publish_url, params={"creation_id": container_id, "access_token": token}, timeout=20)
        pub_resp.raise_for_status()
        media_id = pub_resp.json().get("id")

        print(f"   ✓ Reel successfully published on Instagram (media_id: {media_id})")
        return f"https://www.instagram.com/reel/{media_id}/"

    except Exception as e:
        print(f"   ⚠ Instagram Reels upload failed: {e}")
        return None
