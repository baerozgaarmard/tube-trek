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
    }, timeout=25)
    return [{
        "url": r.get("url"),
        "credit": {"source": "Openverse", "author": r.get("creator") or "Unknown",
                   "license": f"CC {(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip(),
                   "link": r.get("foreign_landing_url") or r.get("url")},
    } for r in d.get("results", []) if r.get("url")]


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
            "timeout": 120,
            "credit": {"source": "Pollinations AI", "author": "AI-generated",
                       "license": "Pollinations terms", "link": "https://pollinations.ai"},
        })
    return out


PROVIDERS = {
    "pixabay":      _pixabay,
    "nasa":         _nasa,
    "openverse":    _openverse,
    "pollinations": _pollinations,
}


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
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            if "pollinations" in url:
                strip_pollinations_logo(path)
            return True
        except Exception:
            continue
    return False
