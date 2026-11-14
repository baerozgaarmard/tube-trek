"""
LLM fallback chain — used when Gemini has no key or every Gemini model is
out of quota. All three speak the OpenAI chat-completions format.

  groq          free key   · very fast Llama models
  openrouter    free key   · ":free" community models
  pollinations  keyless    · last resort so the pipeline never dead-ends
"""
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config
from apis.http import post_json

# Free models to attempt on OpenRouter if primary is unavailable/retired
_OPENROUTER_FALLBACKS = [
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
    "google/gemma-4-26b-a4b-it:free",
]


def _real_key(value: str) -> bool:
    return bool(value) and not value.upper().startswith("YOUR_")


def providers() -> list:
    """(name, url, model, headers) for each usable fallback, in order."""
    out = []
    groq = getattr(config, "GROQ_API_KEY", "")
    if _real_key(groq):
        out.append(("groq", "https://api.groq.com/openai/v1/chat/completions",
                    getattr(config, "GROQ_MODEL", "llama-3.3-70b-versatile"),
                    {"Authorization": f"Bearer {groq}"}))
    orouter = getattr(config, "OPENROUTER_API_KEY", "")
    if _real_key(orouter):
        primary = getattr(config, "OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")
        models = [primary] + [m for m in _OPENROUTER_FALLBACKS if m != primary]
        for m in models:
            out.append(("openrouter", "https://openrouter.ai/api/v1/chat/completions",
                        m,
                        {"Authorization": f"Bearer {orouter}",
                         "HTTP-Referer": "https://github.com/baerozgaarmard/tube-trek",
                         "X-Title": "Tube Trek"}))
    if getattr(config, "KEYLESS_LLM_FALLBACK", True):
        out.append(("pollinations", "https://text.pollinations.ai/openai", "openai", {}))
    return out


last_provider = None


def chat(prompt, temperature: float = 0.9) -> str:
    messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": str(prompt)}]
    errors = []
    for name, url, model, headers in providers():
        for attempt in range(3):
            try:
                print(f"   → Fallback LLM: {name} ({model})…")
                d = post_json(url, {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                }, timeout=180, headers=headers)
                text = (d["choices"][0]["message"].get("content") or "").strip()
                if text:
                    global last_provider
                    last_provider = f"{name.title()} ({model})"
                    return text
                errors.append(f"{name} ({model}): empty response")
                break
            except Exception as e:
                msg = str(e)
                # Free tiers rate-limit bursts (Pollinations answers 402/429) — back off and retry
                if attempt < 2 and any(c in msg for c in ("402", "429", "503", "Max retries",
                                                           "NameResolution", "timed out", "Connection")):
                    wait = 20 * (attempt + 1)
                    print(f"   ⚠ {name} is rate-limiting — retrying in {wait}s…")
                    time.sleep(wait)
                    continue
                print(f"   ⚠ {name} ({model}) failed: {msg[:160]}")
                errors.append(f"{name} ({model}): {msg[:160]}")
                break
    raise RuntimeError("All fallback LLMs failed — " + " | ".join(errors or ["none configured"]))
