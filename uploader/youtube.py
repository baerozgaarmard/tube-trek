"""
YouTube Uploader
Authenticates with the YouTube Data API v3 and uploads the final video.
"""
import os
import pickle
import socket
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import config

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Force IPv4 socket resolution on Windows to prevent IPv6 upload/thumbnail timeouts with fallback
try:
    _orig_getaddrinfo = socket.getaddrinfo
    def _getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        try:
            return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        except Exception:
            return _orig_getaddrinfo(host, port, family, type, proto, flags)
    socket.getaddrinfo = _getaddrinfo_ipv4
except Exception:
    pass


TOKEN_FILE = "youtube_token.pickle"


def _get_service():
    """Return an authenticated YouTube service object."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if creds and not creds.valid and creds.expired and creds.refresh_token:
        try:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
        except Exception:
            pass

    if not creds or not creds.valid:
        if not os.path.exists(config.YOUTUBE_CLIENT_SECRET):
            raise FileNotFoundError(
                f"YouTube OAuth file not found: {config.YOUTUBE_CLIENT_SECRET}\n"
                "Follow the setup guide to create it in Google Cloud Console."
            )
        flow = InstalledAppFlow.from_client_secrets_file(
            config.YOUTUBE_CLIENT_SECRET, config.YOUTUBE_SCOPES
        )
        print("[*] Opening browser for YouTube Upload authorization...")
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def build_description(script: dict) -> str:
    """Standardized YouTube description with optional branding and tags."""
    desc = script.get("description", "").strip()
    parts = [desc] if desc else []
    if getattr(config, "CREDIT_TUBE_TREK", False):
        parts.append("Created autonomously with Tube Trek.")
    tags = " ".join(f"#{t}" for t in script.get("tags", []))
    if tags:
        parts.append(tags)
    return "\n\n".join(parts)


def upload_to_youtube(script: dict, video_path: str, thumbnail_path: str = None, publish_at: str = None, privacy_status: str = None) -> str:
    """
    Uploads the video with auto-generated title, description, tags, and thumbnail.
    publish_at: RFC 3339 datetime string (e.g. "2026-10-29T05:00:00Z") for scheduled publishing.
    Returns the public YouTube URL.
    """
    youtube = _get_service()

    description = build_description(script)

    status_data = {
        "privacyStatus":            privacy_status or config.VIDEO_PRIVACY,
        "selfDeclaredMadeForKids":  False,
    }
    if publish_at:
        status_data["privacyStatus"] = "private"
        status_data["publishAt"] = publish_at

    body = {
        "snippet": {
            "title":       script["title"],
            "description": description,
            "tags":        script.get("tags", []),
            "categoryId":  config.VIDEO_CATEGORY_ID,
        },
        "status": status_data,
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=5 * 1024 * 1024,   # 5 MB chunks
    )

    insert_req = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    print("   → Uploading…")
    response = None
    retry_count = 0
    while response is None:
        try:
            status, response = insert_req.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"   → {pct}% uploaded", end="\r")
            retry_count = 0
        except Exception as e:
            retry_count += 1
            if retry_count > 5:
                raise
            print(f"\n   ⚠ Transient network glitch ({e}); resuming chunk ({retry_count}/5)...")
            import time
            time.sleep(2)

    print()
    video_id = response["id"]

    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print("   → Uploading custom thumbnail…")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg", resumable=False),
            ).execute()
            print("   ✓ Thumbnail set successfully")
        except Exception as e:
            print(f"   ⚠ Thumbnail upload warning: {e}")

    # Post engagement discussion comment if provided in script
    pinned_comment = script.get("pinned_comment")
    if pinned_comment:
        try:
            print("   → Posting discussion trigger comment…")
            youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": pinned_comment
                            }
                        }
                    }
                }
            ).execute()
            print("   ✓ Discussion trigger comment posted successfully")
        except Exception as e:
            print(f"   ⚠ Comment posting warning: {e}")

    return f"https://www.youtube.com/watch?v={video_id}"
