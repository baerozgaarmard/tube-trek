"""
Public channel stats via the YouTube Data API v3 or keyless public RSS fallback.
Accepts a channel ID (UC…) or @handle.
"""
import json
import re
import xml.etree.ElementTree as ET
import requests

import config
from apis.http import get_json, ttl_cache

_API = "https://www.googleapis.com/youtube/v3"


def configured() -> bool:
    """Return True if an API key is configured or a channel identifier is available."""
    ident = getattr(config, "YOUTUBE_CHANNEL_ID", "").strip() or "@baerozgaarmard"
    return bool(getattr(config, "YOUTUBE_API_KEY", "")) or bool(ident)


def _channel_stats_keyless(ident: str) -> dict:
    """Keyless channel statistics extractor via official YouTube RSS & page metadata."""
    handle = ident if ident.startswith("@") else f"@{ident}" if not ident.startswith("UC") else None
    url = f"https://www.youtube.com/{handle}" if handle else f"https://www.youtube.com/channel/{ident}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    r = requests.get(url, headers=headers, timeout=10)
    html = r.text

    title = ident
    subscribers = 0
    videos_count = 0
    total_views = 0
    channel_id = ident if ident.startswith("UC") else None

    if not channel_id:
        cid_match = re.search(r"https://www.youtube.com/channel/(UC[\w-]+)", html)
        if cid_match:
            channel_id = cid_match.group(1)

    m = re.search(r"ytInitialData\s*=\s*({.+?});</script>", html)
    if m:
        try:
            data = json.loads(m.group(1))
            header = data.get("header", {}).get("pageHeaderRenderer", {})
            meta = header.get("content", {}).get("pageHeaderViewModel", {})
            t = meta.get("title", {}).get("dynamicTextViewModel", {}).get("text", {}).get("content")
            if t:
                title = t
            rows = meta.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", [])
            for row in rows:
                for part in row.get("metadataParts", []):
                    c = part.get("text", {}).get("content", "")
                    if "subscriber" in c.lower():
                        num_str = c.split()[0].replace(",", "")
                        mult = 1
                        if num_str.endswith("K") or num_str.endswith("k"):
                            mult = 1000
                            num_str = num_str[:-1]
                        elif num_str.endswith("M") or num_str.endswith("m"):
                            mult = 1000000
                            num_str = num_str[:-1]
                        try:
                            subscribers = int(float(num_str) * mult)
                        except Exception:
                            pass
                    elif "video" in c.lower():
                        try:
                            videos_count = int(c.split()[0].replace(",", ""))
                        except Exception:
                            pass
        except Exception:
            pass

    # Fetch exact total channel views from the /about page
    try:
        about_url = f"https://www.youtube.com/{handle}/about" if handle else f"https://www.youtube.com/channel/{channel_id}/about"
        about_resp = requests.get(about_url, headers=headers, timeout=10)
        vm = re.search(r'"viewCountText":"([\d,]+)\s*views"', about_resp.text)
        if vm:
            total_views = int(vm.group(1).replace(",", ""))
    except Exception:
        pass

    recent = []
    fallback_views = 0
    if channel_id:
        try:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            rss_resp = requests.get(rss_url, headers=headers, timeout=10)
            if rss_resp.ok:
                root = ET.fromstring(rss_resp.content)
                ns = {
                    "atom": "http://www.w3.org/2005/Atom",
                    "media": "http://search.yahoo.com/mrss/",
                    "yt": "http://www.youtube.com/xml/schemas/2015",
                }
                for entry in root.findall("atom:entry", ns)[:24]:
                    v_title = entry.find("atom:title", ns).text
                    vid = entry.find("yt:videoId", ns).text
                    pub = entry.find("atom:published", ns).text
                    stat = entry.find("media:group/media:community/media:statistics", ns)
                    vc = int(stat.attrib.get("views", 0)) if stat is not None else 0
                    fallback_views += vc
                    recent.append({
                        "id": vid,
                        "title": v_title,
                        "published": pub,
                        "views": vc,
                        "likes": 0,
                    })
        except Exception:
            pass

    return {
        "title": title,
        "thumbnail": "",
        "subscribers": subscribers,
        "views": total_views or fallback_views,
        "videos": videos_count or len(recent),
        "recent": sorted(recent, key=lambda v: v["published"]),
    }


import os

def _channel_stats_oauth() -> dict | None:
    token_file = "youtube_token.pickle"
    if not os.path.exists(token_file):
        return None
    try:
        import pickle
        from googleapiclient.discovery import build
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
        if not creds or not creds.valid:
            return None
        yt = build("youtube", "v3", credentials=creds)
        ch_res = yt.channels().list(mine=True, part="snippet,statistics,contentDetails").execute()
        if not ch_res.get("items"):
            return None
        ch = ch_res["items"][0]
        st = ch.get("statistics", {})
        uploads = ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        recent = []
        if uploads:
            pl = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=24).execute()
            ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
            if ids:
                vids = yt.videos().list(part="snippet,statistics", id=",".join(ids)).execute()
                for v in vids.get("items", []):
                    recent.append({
                        "id": v["id"],
                        "title": v["snippet"]["title"],
                        "published": v["snippet"]["publishedAt"],
                        "views": int(v["statistics"].get("viewCount", 0)),
                        "likes": int(v["statistics"].get("likeCount", 0)),
                    })
        return {
            "title": ch["snippet"]["title"],
            "thumbnail": ch["snippet"].get("thumbnails", {}).get("default", {}).get("url", ""),
            "subscribers": int(st.get("subscriberCount", 0)),
            "views": int(st.get("viewCount", 0)),
            "videos": int(st.get("videoCount", 0)),
            "recent": sorted(recent, key=lambda v: v["published"], reverse=True),
        }
    except Exception:
        return None


def channel_analytics(days: int = 28) -> dict | None:
    token_file = "youtube_token.pickle"
    if not os.path.exists(token_file):
        return None
    try:
        import pickle, datetime
        from googleapiclient.discovery import build
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
        if not creds or not creds.valid:
            return None
        yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        res = yt_analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost"
        ).execute()
        rows = res.get("rows", [[]])
        if rows and len(rows[0]) >= 5:
            r = rows[0]
            return {
                "period_days": days,
                "views": r[0],
                "watch_time_minutes": r[1],
                "avg_view_duration_seconds": r[2],
                "subscribers_gained": r[3],
                "subscribers_lost": r[4],
            }
        return None
    except Exception:
        return None


@ttl_cache(30)
def channel_stats() -> dict:
    oauth_data = _channel_stats_oauth()
    if oauth_data:
        return oauth_data

    key = getattr(config, "YOUTUBE_API_KEY", "")
    ident = (getattr(config, "YOUTUBE_CHANNEL_ID", "") or "@baerozgaarmard").strip()

    if not key:
        return _channel_stats_keyless(ident)

    params = {"part": "snippet,statistics,contentDetails", "key": key}
    if ident.startswith("@"):
        params["forHandle"] = ident
    else:
        params["id"] = ident

    try:
        d = get_json(f"{_API}/channels", params=params)
        if not d.get("items"):
            return _channel_stats_keyless(ident)
        ch = d["items"][0]
        st = ch.get("statistics", {})
        uploads = ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

        recent = []
        if uploads:
            pl = get_json(f"{_API}/playlistItems", params={
                "part": "contentDetails", "playlistId": uploads, "maxResults": 24, "key": key})
            ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
            if ids:
                vids = get_json(f"{_API}/videos", params={
                    "part": "snippet,statistics", "id": ",".join(ids), "key": key})
                for v in vids.get("items", []):
                    recent.append({
                        "id":        v["id"],
                        "title":     v["snippet"]["title"],
                        "published": v["snippet"]["publishedAt"],
                        "views":     int(v["statistics"].get("viewCount", 0)),
                        "likes":     int(v["statistics"].get("likeCount", 0)),
                    })
        return {
            "title":       ch["snippet"]["title"],
            "thumbnail":   ch["snippet"].get("thumbnails", {}).get("default", {}).get("url", ""),
            "subscribers": int(st.get("subscriberCount", 0)),
            "views":       int(st.get("viewCount", 0)),
            "videos":      int(st.get("videoCount", 0)),
            "recent":      sorted(recent, key=lambda v: v["published"]),
        }
    except Exception:
        return _channel_stats_keyless(ident)
