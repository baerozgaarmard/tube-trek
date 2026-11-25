"""
Stock Image Downloader — Pexels first, then the free fallback chain in
apis/images.py (Pixabay → NASA → Openverse → Pollinations AI), so videos get
real B-roll even without a Pexels key.

For normal videos : up to 3 images per section (mid-section B-roll cuts)
For Shorts        : 1 image per query, up to 4 per section (fast slideshow)
Images saved to output/images/section_NN_imgMM.jpg
Credits saved to output/credits.json (used for the description's attribution).
"""
import glob
import json
import os
import random
import re
import requests
import config
from apis import images as image_apis

PEXELS_SEARCH = "https://api.pexels.com/v1/search"
PEXELS_VIDEOS_SEARCH = "https://api.pexels.com/videos/search"
PIXABAY_VIDEOS_SEARCH = "https://pixabay.com/api/videos/"

FALLBACK_QUERIES = [
    "deep space stars galaxy nebula",
    "universe cosmic explosion supernova",
    "quantum physics abstract particles dark",
    "earth atmosphere orbit view aerial",
    "astronomy telescope celestial sky night",
    "science laboratory futuristic technology",
    "alien planet surface landscape dramatic",
    "black hole event horizon spacetime",
    "futuristic neon digital network glowing",
    "deep ocean dark mystery abyss",
]

# Every image downloaded this run → credits.json
_credits: list = []

REGISTRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "used_media_registry.json")


def _load_used_urls() -> set:
    """Load persistent set of all media URLs ever used across all runs to guarantee zero repeats."""
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("used_urls", []))
        except Exception:
            pass
    return set()


def _record_used_url(url: str):
    """Persist newly downloaded media URL to disk registry immediately."""
    if not url:
        return
    current = _load_used_urls()
    current.add(url)
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump({"used_urls": sorted(list(current))}, f, indent=2)
    except Exception:
        pass


_used_urls: set = _load_used_urls()


def _pexels_ready() -> bool:
    key = getattr(config, "PEXELS_API_KEY", "") or ""
    return bool(key) and not key.upper().startswith("YOUR_")


def _pexels(query: str, orientation: str, count: int) -> list:
    """Pexels candidates in the same shape as apis.images providers."""
    per_page = min(max(count * 3, 15), 40)
    # Randomise page so repeated runs don't fetch the exact same top photos
    page = random.randint(1, 3)
    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "page": page, "orientation": orientation}
    r = requests.get(PEXELS_SEARCH, headers=headers, params=params, timeout=15)
    if r.status_code == 401:
        print("   ⚠ Pexels API key invalid — using free fallback sources")
        config.PEXELS_API_KEY = ""
        return []
    r.raise_for_status()
    photos = r.json().get("photos", [])
    # If a random page returned nothing, retry page 1
    if not photos and page > 1:
        params["page"] = 1
        r2 = requests.get(PEXELS_SEARCH, headers=headers, params=params, timeout=15)
        photos = r2.json().get("photos", []) if r2.ok else []

    photos.sort(key=lambda p: p["width"] * p["height"], reverse=True)
    # Shuffle within top pool so each run picks different images
    pool = photos[:max(count * 2, 6)]
    random.shuffle(pool)
    return [{
        "url": p["src"].get("large2x") or p["src"]["original"],
        "credit": {"source": "Pexels", "author": p.get("photographer", ""),
                   "license": "Pexels License", "link": p.get("url", "")},
    } for p in pool]


def _pexels_videos(query: str, orientation: str, count: int) -> list:
    """Fetch free HD vertical video clips from Pexels Video API."""
    if not _pexels_ready():
        return []
    try:
        headers = {"Authorization": config.PEXELS_API_KEY}
        params = {"query": query, "per_page": min(max(count * 3, 10), 30), "orientation": orientation}
        r = requests.get(PEXELS_VIDEOS_SEARCH, headers=headers, params=params, timeout=15)
        if not r.ok:
            return []
        videos = r.json().get("videos", [])
        candidates = []
        for v in videos:
            vfiles = v.get("video_files", [])
            hd_files = [f for f in vfiles if f.get("width") and f.get("height") and f.get("link")]
            if not hd_files:
                continue
            hd_files.sort(key=lambda f: f.get("width", 0) * f.get("height", 0), reverse=True)
            chosen = hd_files[0]
            candidates.append({
                "url": chosen["link"],
                "is_video": True,
                "credit": {"source": "Pexels Video", "author": v.get("user", {}).get("name", "Pexels Creator"),
                           "license": "Pexels License", "link": v.get("url", "")}
            })
        if candidates:
            random.shuffle(candidates)
        return candidates[:count]
    except Exception as e:
        return []


def _pixabay_videos(query: str, count: int) -> list:
    """Fetch free vertical video clips from Pixabay Videos API."""
    key = getattr(config, "PIXABAY_API_KEY", "")
    if not key:
        return []
    try:
        clean_words = [w for w in re.findall(r"\w+", query) if len(w) > 2]
        q_clean = " ".join(clean_words[:3]) if clean_words else query[:40]
        params = {"key": key, "q": q_clean, "video_type": "film", "per_page": max(10, count * 3)}
        r = requests.get(PIXABAY_VIDEOS_SEARCH, params=params, timeout=15)
        if not r.ok:
            return []
        hits = r.json().get("hits", [])
        candidates = []
        for h in hits:
            vdata = h.get("videos", {})
            vobj = vdata.get("large") or vdata.get("medium") or vdata.get("small")
            if vobj and vobj.get("url"):
                candidates.append({
                    "url": vobj["url"],
                    "is_video": True,
                    "credit": {"source": "Pixabay Video", "author": h.get("user", "Pixabay Creator"),
                               "license": "Pixabay Content License", "link": h.get("pageURL", "")}
                })
        if candidates:
            random.shuffle(candidates)
        return candidates[:count]
    except Exception as e:
        return []


def _normalize_video(raw_path: str, out_mp4: str, orientation: str, seek_start: int = 1) -> bool:
    """Trim/crop-scale a downloaded video clip into a fast 4s 30fps all-keyframe MP4."""
    import subprocess
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return False

    w, h = (1080, 1920) if orientation == "portrait" else (1920, 1080)
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30"

    for seek in (["-ss", str(seek_start)], []):
        cmd = [
            ffmpeg, "-y", *seek, "-i", raw_path, "-t", "4", "-an",
            "-vf", vf, "-c:v", "libx264", "-g", "1", "-preset", "ultrafast", "-crf", "23",
            "-pix_fmt", "yuv420p", out_mp4,
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=45)
            if r.returncode == 0 and os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 20_000:
                if raw_path != out_mp4 and os.path.exists(raw_path):
                    os.remove(raw_path)
                return True
        except Exception:
            pass
    for p in (raw_path, out_mp4):
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass
    return False


def _candidates(query: str, orientation: str, count: int, allow_video: bool = True) -> list:
    if allow_video and orientation == "portrait":
        vids = _pexels_videos(query, orientation, count) or _pixabay_videos(query, count)
        if not vids:
            vids = image_apis.search_videos(query, count=1, exclude_urls=_used_urls)
        c = [x for x in vids if x["url"] not in _used_urls and x.get("credit", {}).get("link") not in _used_urls]
        if c:
            return c
    if _pexels_ready():
        try:
            c = [x for x in _pexels(query, orientation, count) if x["url"] not in _used_urls and x.get("credit", {}).get("link") not in _used_urls]
            if c:
                return c
        except Exception as e:
            print(f"   ⚠ Pexels search failed for '{query}': {e}")
    return image_apis.search(query, orientation, count, exclude_urls=_used_urls) or []


def _fetch_images(query: str, section_index: int, images_dir: str,
                  count: int = 1, orientation: str = "landscape",
                  img_num_start: int = 0, topic_hint: str = "",
                  allow_video: bool = True) -> list:
    """
    Downloads `count` distinct media assets (motion B-roll + stills) with diverse fallbacks.
    """
    saved = []
    rotated_fallbacks = [FALLBACK_QUERIES[(section_index + i) % len(FALLBACK_QUERIES)] for i in range(len(FALLBACK_QUERIES))]

    clean_words = [w for w in re.findall(r"\w+", query) if len(w) > 2 and w.lower() not in (
        "dramatic", "cinematic", "photograph", "concept", "shot", "view", "ultra", "realistic"
    )]
    clean_q = " ".join(clean_words[:4]) if clean_words else query
    search_query = f"{topic_hint} {clean_q}" if (topic_hint and topic_hint.lower() not in clean_q.lower()) else clean_q

    for idx_attempt, attempt_query in enumerate([clean_q, search_query] + rotated_fallbacks[:3]):
        needed = count - len(saved)
        if needed <= 0:
            break
        # Only pull 1 video clip per query so we combine real motion clips + diverse photos cleanly
        use_vid = allow_video and idx_attempt < 2 and not any(p.endswith(".mp4") for p in saved)
        for cand in _candidates(attempt_query, orientation, needed, allow_video=use_vid):
            is_vid = bool(cand.get("is_video"))
            slot_num = img_num_start + len(saved) + 1
            if is_vid:
                raw_path = os.path.join(images_dir, f"section_{section_index:02d}_raw{slot_num:02d}.bin")
                final_path = os.path.join(images_dir, f"section_{section_index:02d}_broll{slot_num:02d}.mp4")
                ok = image_apis.fetch(cand, raw_path) and _normalize_video(
                    raw_path, final_path, orientation, seek_start=int(cand.get("seek_start", 1))
                )
            else:
                final_path = os.path.join(images_dir, f"section_{section_index:02d}_img{slot_num:02d}.jpg")
                ok = image_apis.fetch(cand, final_path)

            if ok:
                saved.append(final_path)
                _used_urls.add(cand["url"])
                _record_used_url(cand["url"])
                link = cand.get("credit", {}).get("link")
                if link:
                    _used_urls.add(link)
                    _record_used_url(link)
                _credits.append({"file": os.path.basename(final_path), "query": attempt_query, **cand["credit"]})
            if len(saved) >= count:
                return saved

    # Guaranteed fallback: if stock APIs yielded fewer shots than needed, generate via Pollinations AI
    needed = count - len(saved)
    if needed > 0:
        for cand in (image_apis.PROVIDERS["pollinations"](query, orientation, needed) or []):
            fname = f"section_{section_index:02d}_img{img_num_start + len(saved) + 1:02d}.jpg"
            path = os.path.join(images_dir, fname)
            if image_apis.fetch(cand, path):
                saved.append(path)
                _used_urls.add(cand["url"])
                _record_used_url(cand["url"])
                _credits.append({"file": fname, "query": query, **cand["credit"]})
            if len(saved) >= count:
                break
    return saved


def section_images(images_dir: str, section_id: int) -> list:
    """Images already on disk for a section (used when the Images step is skipped)."""
    return sorted(glob.glob(os.path.join(images_dir, f"section_{section_id:02d}_*")))


def download_images(script: dict, output_dir: str) -> dict:
    """
    Downloads stock motion clips and images for every section.
    Shorts: returns list of paths per section_id (for dynamic visual montage).
    """
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    for old in glob.glob(os.path.join(images_dir, "section_*.*")):
        try:
            os.remove(old)
        except OSError:
            pass
    _credits.clear()
    global _used_urls
    _used_urls = _load_used_urls()

    if not _pexels_ready():
        img_ord = " → ".join(getattr(config, "IMAGE_SOURCES", []))
        vid_ord = " → ".join(getattr(config, "VIDEO_SOURCES", []))
        print(f"   → No Pexels key — using keyless video ({vid_ord}) + image ({img_ord})")

    is_shorts        = script.get("video_type") == "shorts"
    orientation      = "portrait" if is_shorts else "landscape"

    raw_title = script.get("title", "")
    _stop = {"you", "are", "is", "was", "in", "inside", "a", "an", "the", "if", "what",
             "why", "how", "right", "now", "we", "to", "of", "for", "on", "from", "with"}
    topic_words = [w for w in re.findall(r"[A-Za-z0-9]+", raw_title) if w.lower() not in _stop]
    topic_hint  = " ".join(topic_words[:3]) if topic_words else ""

    image_map = {}
    for section in script.get("sections", []):
        sid   = section["id"]
        queries = [section.get("image_query", "science universe space")]
        for extra_key in ("image_query_2", "image_query_3", "image_query_4", "image_query_5"):
            q = section.get(extra_key, "").strip()
            if q:
                queries.append(q)

        count_per_q = 2 if is_shorts else (2 if len(queries) < 3 else 1)
        use = queries if is_shorts else queries[:5]
        print(f"   → [{sid}] {len(use)} queries × {count_per_q} shot(s) each")
        paths = []
        for qi, q in enumerate(use):
            paths.extend(_fetch_images(q, sid, images_dir,
                                       count=count_per_q, orientation=orientation,
                                       img_num_start=len(paths), topic_hint=topic_hint,
                                       allow_video=(qi == 0)))
        image_map[sid] = paths if (paths or is_shorts) else None
        print(f"         saved {len(paths)} shots")

    with open(os.path.join(output_dir, "credits.json"), "w", encoding="utf-8") as f:
        json.dump(_credits, f, indent=2)
    by_source = {}
    for c in _credits:
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1
    if by_source:
        print("   → Media sources: " + ", ".join(f"{k} ×{v}" for k, v in by_source.items()))
    return image_map
