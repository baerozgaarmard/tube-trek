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
_used_urls: set = set()


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


def _candidates(query: str, orientation: str, count: int, allow_video: bool = True) -> list:
    if allow_video and orientation == "portrait":
        vids = _pexels_videos(query, orientation, count) or _pixabay_videos(query, count)
        c = [x for x in vids if x["url"] not in _used_urls]
        if c:
            return c
    if _pexels_ready():
        try:
            c = [x for x in _pexels(query, orientation, count) if x["url"] not in _used_urls]
            if c:
                return c
        except Exception as e:
            print(f"   ⚠ Pexels search failed for '{query}': {e}")
    return image_apis.search(query, orientation, count, exclude_urls=_used_urls)


def _fetch_images(query: str, section_index: int, images_dir: str,
                  count: int = 1, orientation: str = "landscape",
                  img_num_start: int = 0, topic_hint: str = "") -> list:
    """
    Downloads `count` distinct images for a given query with diverse fallbacks.
    """
    import re
    saved = []
    rotated_fallbacks = [FALLBACK_QUERIES[(section_index + i) % len(FALLBACK_QUERIES)] for i in range(len(FALLBACK_QUERIES))]

    clean_words = [w for w in re.findall(r"\w+", query) if len(w) > 2 and w.lower() not in (
        "dramatic", "cinematic", "photograph", "concept", "shot", "view", "ultra", "realistic"
    )]
    clean_q = " ".join(clean_words[:4]) if clean_words else query
    search_query = f"{topic_hint} {clean_q}" if (topic_hint and topic_hint.lower() not in clean_q.lower()) else clean_q

    for attempt_query in [clean_q, search_query] + rotated_fallbacks:
        needed = count - len(saved)
        if needed <= 0:
            break
        for cand in _candidates(attempt_query, orientation, needed):
            is_vid = bool(cand.get("is_video"))
            ext = ".mp4" if is_vid else ".jpg"
            prefix = "broll" if is_vid else "img"
            fname = f"section_{section_index:02d}_{prefix}{img_num_start + len(saved) + 1:02d}{ext}"
            path = os.path.join(images_dir, fname)
            if image_apis.fetch(cand, path):
                saved.append(path)
                _used_urls.add(cand["url"])
                _credits.append({"file": fname, "query": attempt_query, **cand["credit"]})
            if len(saved) >= count:
                return saved
        if saved:
            break
    return saved


def section_images(images_dir: str, section_id: int) -> list:
    """Images already on disk for a section (used when the Images step is skipped)."""
    return sorted(glob.glob(os.path.join(images_dir, f"section_{section_id:02d}_img*.jpg")))


def download_images(script: dict, output_dir: str) -> dict:
    """
    Downloads stock images for every section.
    Shorts: returns list of paths per section_id (for slideshow).
    Normal: returns list of paths (or None) per section_id.
    """
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    # Clear the previous run's images so stale B-roll never leaks into this video
    for old in glob.glob(os.path.join(images_dir, "section_*.*")):
        try:
            os.remove(old)
        except OSError:
            pass
    _credits.clear()
    _used_urls.clear()

    if not _pexels_ready():
        order = " → ".join(getattr(config, "IMAGE_SOURCES", []))
        print(f"   → No Pexels key — using free sources: {order}")

    is_shorts        = script.get("video_type") == "shorts"
    orientation      = "portrait" if is_shorts else "landscape"

    # Extract meaningful topic keywords (skip stopwords like "You Are Inside A")
    raw_title = script.get("title", "")
    _stop = {"you", "are", "is", "was", "in", "inside", "a", "an", "the", "if", "what",
             "why", "how", "right", "now", "we", "to", "of", "for", "on", "from", "with"}
    topic_words = [w for w in re.findall(r"[A-Za-z0-9]+", raw_title) if w.lower() not in _stop]
    topic_hint  = " ".join(topic_words[:3]) if topic_words else ""

    image_map = {}
    for section in script.get("sections", []):
        sid   = section["id"]
        # Collect all image queries defined for this section
        queries = [section.get("image_query", "science universe space")]
        for extra_key in ("image_query_2", "image_query_3", "image_query_4"):
            q = section.get(extra_key, "").strip()
            if q:
                queries.append(q)

        # Shorts: one image per query; normal: first 3 queries for B-roll cuts
        count_per_q = 2 if is_shorts else (2 if len(queries) < 3 else 1)
        use = queries if is_shorts else queries[:5]
        print(f"   → [{sid}] {len(use)} queries × {count_per_q} image(s) each")
        paths = []
        for qi, q in enumerate(use):
            paths.extend(_fetch_images(q, sid, images_dir,
                                       count=count_per_q, orientation=orientation,
                                       img_num_start=qi, topic_hint=topic_hint))
        image_map[sid] = paths if (paths or is_shorts) else None
        print(f"         saved {len(paths)} images")

    with open(os.path.join(output_dir, "credits.json"), "w", encoding="utf-8") as f:
        json.dump(_credits, f, indent=2)
    by_source = {}
    for c in _credits:
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1
    if by_source:
        print("   → Image sources: " + ", ".join(f"{k} ×{v}" for k, v in by_source.items()))
    return image_map
