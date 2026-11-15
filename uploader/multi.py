"""
Multi-Platform Syndication Dispatcher — Tube Trek
Coordinates simultaneous publishing across YouTube Shorts, TikTok, and Instagram Reels.
"""
from uploader.youtube import upload_to_youtube
from uploader.tiktok import upload_to_tiktok, is_tiktok_configured
from uploader.instagram import upload_to_instagram, is_instagram_configured


def publish_short(script: dict, video_path: str, thumbnail_path: str = None,
                  platforms: list = None, privacy: str = "public",
                  schedule: str = None) -> dict:
    """
    Distribute the generated short to the specified platforms (default: ["youtube"]).
    Supported platforms: 'youtube', 'tiktok', 'instagram'
    """
    target_platforms = [p.lower().strip() for p in (platforms or ["youtube"])]
    results = {}

    print("\n" + "=" * 60)
    print(f"📡 MULTI-PLATFORM SYNDICATION: {', '.join(target_platforms).upper()}")
    print("=" * 60)

    # 1. YouTube Shorts
    if "youtube" in target_platforms:
        print("\n[Platform 1/3] Publishing to YouTube Shorts…")
        try:
            yt_url = upload_to_youtube(
                script=script,
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                publish_at=schedule,
                privacy_status=privacy,
            )
            results["youtube"] = yt_url
            print(f"   ✓ YouTube Shorts Live: {yt_url}")
        except Exception as e:
            results["youtube"] = f"Error: {e}"
            print(f"   ⚠ YouTube upload error: {e}")

    # 2. TikTok
    if "tiktok" in target_platforms:
        print("\n[Platform 2/3] Publishing to TikTok…")
        try:
            tt_url = upload_to_tiktok(
                script=script,
                video_path=video_path,
                privacy_level="PUBLIC_TO_EVERYONE" if privacy == "public" else "SELF_ONLY",
            )
            results["tiktok"] = tt_url or "Skipped (Token unconfigured)"
            if tt_url:
                print(f"   ✓ TikTok Post Live: {tt_url}")
        except Exception as e:
            results["tiktok"] = f"Error: {e}"
            print(f"   ⚠ TikTok upload error: {e}")

    # 3. Instagram Reels
    if "instagram" in target_platforms:
        print("\n[Platform 3/3] Publishing to Instagram Reels…")
        try:
            ig_url = upload_to_instagram(
                script=script,
                video_path=video_path,
            )
            results["instagram"] = ig_url or "Skipped (Token unconfigured)"
            if ig_url:
                print(f"   ✓ Instagram Reel Live: {ig_url}")
        except Exception as e:
            results["instagram"] = f"Error: {e}"
            print(f"   ⚠ Instagram upload error: {e}")

    return results
