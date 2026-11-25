"""
Image sources beyond Pexels. Tried in the order set by config.IMAGE_SOURCES
until one returns results, so videos still get B-roll with no Pexels key.

  pixabay       Pixabay API (free key)               — Pixabay Content License
  nasa          NASA Image & Video Library (keyless)  — public domain, space topics only
  openverse     Openverse / WordPress (keyless)       — CC licences, attribution kept
  pollinations  Pollinations.ai (keyless)             — AI-generated, last resort

Each candidate carries a `credit` dict; stock.py writes them to credits.json
and the description builder turns them into an attribution block.
"""
import random
import re
from urllib.parse import quote

import config
from apis.http import get, get_json

_SPACE_WORDS = re.compile(
    r"\b(space|galax|star|planet|nebula|black hole|moon|mars|jupiter|saturn|"
    r"astronaut|rocket|cosm|universe|orbit|solar|sun\b|telescope|nasa|comet|"
    r"asteroid|earth from|supernova|eclipse|satellite)", re.I)


def _pixabay(query: str, orientation: str, count: int) -> list:
    key = getattr(config, "PIXABAY_API_KEY", "")
    if not key:
        return []
    # Clean filler words that break Pixabay exact-match search
    clean_words = [w for w in re.findall(r"\w+", query) if len(w) > 2 and w.lower() not in (
        "dramatic", "cinematic", "photograph", "concept", "shot", "view", "ultra", "realistic",
        "detailed", "rendering", "style", "illustration", "image", "background"
    )]
    q_clean = " ".join(clean_words[:4]) if clean_words else query[:60]
    page = random.randint(1, 3)
    params = {
        "key": key, "q": q_clean, "image_type": "photo", "safesearch": "true",
        "orientation": "vertical" if orientation == "portrait" else "horizontal",
        "per_page": max(15, count * 4), "page": page,
        ("min_height" if orientation == "portrait" else "min_width"): 1080 if orientation == "portrait" else 1280,
    }
    d = get_json("https://pixabay.com/api/", params=params)
    hits = d.get("hits", [])
    if not hits and page > 1:
        params["page"] = 1
        d = get_json("https://pixabay.com/api/", params=params)
        hits = d.get("hits", [])
    if _SPACE_WORDS.search(query):
        bad = re.compile(r"\b(makeup|lipstick|cosmetic|door|skull|romance|couple|solar-panel|wedding|fashion|flower)\b", re.I)
        hits = [h for h in hits if not bad.search(f"{h.get('tags', '')} {h.get('pageURL', '')}")]
    if hits:
        random.shuffle(hits)
    return [{
        "url": h.get("largeImageURL") or h.get("webformatURL"),
        "credit": {"source": "Pixabay", "author": h.get("user", ""),
                   "license": "Pixabay Content License", "link": h.get("pageURL", "")},
    } for h in hits]


def _nasa(query: str, orientation: str, count: int) -> list:
    if not _SPACE_WORDS.search(query):
        return []          # NASA's library is superb for space, useless otherwise
    d = get_json("https://images-api.nasa.gov/search", params={
        "q": query, "media_type": "image", "page_size": max(25, count * 5),
    })
    out = []
    items = d.get("collection", {}).get("items", [])
    if items:
        random.shuffle(items)
    for item in items:
        links = item.get("links") or []
        data = (item.get("data") or [{}])[0]
        if not links:
            continue
        meta_text = f"{data.get('title', '')} {data.get('nasa_id', '')} {' '.join(data.get('keywords') or [])}"
        if _BAD_PHOTO_WORDS.search(meta_text.replace("_", " ")):
            continue
        href = links[0].get("href", "")
        # Prefer original / large resolution
        orig_href = re.sub(r"~(thumb|small|medium)\.", "~orig.", href)
        large_href = re.sub(r"~(thumb|small|medium)\.", "~large.", href)
        out.append({
            "url": large_href,
            "fallback_url": href,
            "credit": {"source": "NASA", "author": data.get("center") or "NASA",
                       "license": "Public domain",
                       "link": f"https://images.nasa.gov/details/{data.get('nasa_id', '')}"},
        })
    return out


def _openverse(query: str, orientation: str, count: int) -> list:
    d = get_json("https://api.openverse.org/v1/images/", params={
        "q": query, "page_size": max(10, count * 3),
        "license_type": "commercial,modification",
        "aspect_ratio": "tall" if orientation == "portrait" else "wide",
        "size": "large", "mature": "false",
    }, timeout=12)
    return [{
        "url": r.get("url"),
        "credit": {"source": "Openverse", "author": r.get("creator") or "Unknown",
                   "license": f"CC {(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip(),
                   "link": r.get("foreign_landing_url") or r.get("url")},
    } for r in (d or {}).get("results", []) if r.get("url")]


_BAD_VIDEO_WORDS = re.compile(
    r"\b(this week|what's up|whats up|interview|briefing|press|conference|panel|podcast|lecture|"
    r"logo|award|ceremony|remarks|speech|town hall|webinar|french|german|spanish|"
    r"russian|diagram|chart|interferometer|schema|slike|slice|subtitle|subtitles|captioned)\b", re.I
)
_BAD_PHOTO_WORDS = re.compile(
    r"\b(book images|diagram|chart|graph|map|plate|illustration|drawing|sketch|"
    r"manuscript|engraving|woodcut|table|equation|formula|slice|specimen|bayer|"
    r"rawpixel|vintage|where to find|screenshot|patch|insignia|crest|emblem|sticker|badge|decal|sts-)\b", re.I
)


def _query_tokens(query: str) -> list:
    return [w.lower() for w in re.findall(r"[A-Za-z0-9]{3,}", query)]


def _wikimedia(query: str, orientation: str, count: int) -> list:
    """Keyless Wikimedia Commons raster photo search (curated photos, skips diagrams/scanned books)."""
    tokens = _query_tokens(query)
    d = get_json("https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": max(15, count * 5),
        "prop": "imageinfo", "iiprop": "url|mime|size|dimensions|extmetadata", "format": "json",
    }, timeout=12)
    pages = list((d or {}).get("query", {}).get("pages", {}).values())
    random.shuffle(pages)
    out = []
    for p in pages:
        title = p.get("title", "")
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("url", "")
        mime = ii.get("mime", "")
        w, h = ii.get("width") or 0, ii.get("height") or 0
        size = ii.get("size") or 0
        meta = ii.get("extmetadata") or {}
        artist = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "")).strip() or "Wikimedia Commons"
        if not url or mime not in ("image/jpeg", "image/png", "image/webp") or w < 640 or h < 480 or size > 8_000_000:
            continue
        if _BAD_PHOTO_WORDS.search(f"{title.replace('_', ' ')} {artist}"):
            continue
        if tokens and not any(t in title.lower() for t in tokens):
            continue
        lic = (meta.get("LicenseShortName") or {}).get("value", "CC/Public Domain")
        out.append({
            "url": url,
            "credit": {"source": "Wikimedia", "author": artist[:50],
                       "license": lic, "link": ii.get("descriptionurl") or url},
        })
    return out


def _nasa_videos(query: str, count: int) -> list:
    """Keyless NASA MP4 motion B-roll (visualizations & footage only, skips talk shows)."""
    if not _SPACE_WORDS.search(query):
        return []
    d = get_json("https://images-api.nasa.gov/search", params={
        "q": query, "media_type": "video", "page_size": max(12, count * 6),
    }, timeout=12)
    items = (d or {}).get("collection", {}).get("items", [])
    if items:
        random.shuffle(items)
    out = []
    for item in items:
        href = item.get("href", "")
        data = (item.get("data") or [{}])[0]
        title = data.get("title", "")
        if not href or _BAD_VIDEO_WORDS.search(title):
            continue
        try:
            assets = get_json(href, timeout=10)
        except Exception:
            continue
        mp4s = [u for u in (assets or []) if isinstance(u, str) and u.lower().endswith(".mp4")]
        chosen = next((u for u in mp4s if "~medium." in u or "~mobile." in u), None) or (mp4s[0] if mp4s else None)
        if not chosen:
            continue
        out.append({
            "url": chosen.replace("http://", "https://"),
            "is_video": True,
            "seek_start": 6,  # Skip NASA intro logo card (typically 0-5s)
            "timeout": 45,
            "credit": {"source": "NASA Video", "author": data.get("center") or "NASA",
                       "license": "Public domain",
                       "link": f"https://images.nasa.gov/details/{data.get('nasa_id', '')}"},
        })
        if len(out) >= count * 2:
            break
    return out


def _wikimedia_videos(query: str, count: int) -> list:
    """Keyless Wikimedia Commons HD scientific/historical video clips (.webm/.mp4 under 25 MB)."""
    tokens = _query_tokens(query)
    d = get_json("https://commons.wikimedia.org/w/api.php", params={
        "action": "query", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": f"{query} filetype:video", "gsrlimit": max(12, count * 5),
        "prop": "imageinfo", "iiprop": "url|mime|size|dimensions|extmetadata", "format": "json",
    }, timeout=12)
    pages = list((d or {}).get("query", {}).get("pages", {}).values())
    random.shuffle(pages)
    out = []
    for p in pages:
        title = p.get("title", "")
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("url", "")
        mime = ii.get("mime", "")
        size = ii.get("size") or 0
        w, h = ii.get("width") or 0, ii.get("height") or 0
        if not url or mime not in ("video/webm", "video/mp4") or size < 80_000 or size > 25_000_000:
            continue
        if w < 640 or h < 480 or _BAD_VIDEO_WORDS.search(title.replace("_", " ")):
            continue
        if tokens and not any(t in title.lower() for t in tokens):
            continue
        meta = ii.get("extmetadata") or {}
        artist = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "")).strip() or "Wikimedia Commons"
        lic = (meta.get("LicenseShortName") or {}).get("value", "CC/Public Domain")
        out.append({
            "url": url,
            "is_video": True,
            "seek_start": 1,
            "timeout": 45,
            "credit": {"source": "Wikimedia Video", "author": artist[:50],
                       "license": lic, "link": ii.get("descriptionurl") or url},
        })
    return out


def pollinations_url(prompt: str, width: int = 1080, height: int = 1920,
                     seed: int | None = None) -> str:
    seed = seed if seed is not None else random.randint(1000000, 999999999)
    return (f"https://image.pollinations.ai/prompt/{quote(prompt[:400], safe='')}"
            f"?width={width}&height={height}&nologo=true&seed={seed}&enhance=true")


def _pollinations(query: str, orientation: str, count: int) -> list:
    w, h = (1080, 1920) if orientation == "portrait" else (1920, 1080)
    out = []
    for _ in range(count):
        s = random.randint(1000000, 999999999)
        prompt = f"hyperrealistic award winning 8k, {query}, cinematic volumetric lighting, IMAX quality, photorealistic, 35mm lens, high contrast, no text"
        out.append({
            "url": pollinations_url(prompt, w, h, seed=s),
            "timeout": 90,
            "credit": {"source": "Pollinations AI", "author": "AI-generated",
                       "license": "Pollinations terms", "link": "https://pollinations.ai"},
        })
    return out


PROVIDERS = {
    "pixabay":      _pixabay,
    "nasa":         _nasa,
    "wikimedia":    _wikimedia,
    "openverse":    _openverse,
    "pollinations": _pollinations,
}

VIDEO_PROVIDERS = {
    "nasa":      _nasa_videos,
    "wikimedia": _wikimedia_videos,
}


def search_videos(query: str, count: int = 1, exclude_urls: set | None = None) -> list:
    """Search keyless motion B-roll video sources in configured priority order."""
    order = [s for s in getattr(config, "VIDEO_SOURCES", list(VIDEO_PROVIDERS)) if s in VIDEO_PROVIDERS]
    exclude_urls = exclude_urls or set()
    for name in order:
        try:
            cands = [c for c in VIDEO_PROVIDERS[name](query, count)
                     if c.get("url") and c["url"] not in exclude_urls
                     and c.get("credit", {}).get("link") not in exclude_urls]
        except Exception:
            continue
        if cands:
            return cands[:count * 2]
    return []


def search(query: str, orientation: str = "landscape", count: int = 1,
           exclude_urls: set | None = None) -> list:
    """First provider (in config order, Pexels excluded) that returns results."""
    order = [s for s in getattr(config, "IMAGE_SOURCES", list(PROVIDERS)) if s in PROVIDERS]
    if _SPACE_WORDS.search(query) and "nasa" in order:
        order = ["nasa"] + [s for s in order if s != "nasa"]
    exclude_urls = exclude_urls or set()
    for name in order:
        try:
            cands = [c for c in PROVIDERS[name](query, orientation, count)
                     if c.get("url") and c["url"] not in exclude_urls
                     and c.get("credit", {}).get("link") not in exclude_urls]
        except Exception as e:
            print(f"   ⚠ {name} image search failed for '{query[:40]}': {e}")
            continue
        if cands:
            pool = cands[:max(count * 2, 6)]
            if name != "pollinations":
                random.shuffle(pool)
            return pool[:count]
    return []


def strip_pollinations_logo(path: str) -> None:
    """Pollinations' free tier stamps a logo in the bottom-right corner even with
    nologo=true. Crop the bottom strip off so it never reaches a video."""
    from PIL import Image
    try:
        with Image.open(path) as im:
            w, h = im.size
            cropped = im.convert("RGB").crop((0, 0, w, int(h * 0.93)))
        cropped.save(path, "JPEG", quality=94)
    except Exception as e:
        print(f"   ⚠ Could not clean AI image {path}: {e}")


def fetch(candidate: dict, path: str) -> bool:
    """Download a candidate, trying its fallback URL if the large size is missing."""
    for url in (candidate.get("url"), candidate.get("fallback_url")):
        if not url:
            continue
        try:
            r = get(url, timeout=candidate.get("timeout", 30), stream=True)
            ctype = r.headers.get("Content-Type", "")
            if "image" not in ctype and "octet-stream" not in ctype and "video" not in ctype and "mp4" not in ctype:
                continue
            clen = int(r.headers.get("Content-Length") or 0)
            max_bytes = 25_000_000 if candidate.get("is_video") else 8_000_000
            if clen > max_bytes:
                continue
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            if "pollinations" in url:
                strip_pollinations_logo(path)
            return True
        except Exception:
            continue
    return False
