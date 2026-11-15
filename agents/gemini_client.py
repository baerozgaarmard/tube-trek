"""
LLM Client ? shared across all agents.

1. Gemini / Gemma: tries models in order if config.GEMINI_API_KEY is present.
2. Otherwise hands over to Groq and OpenRouter:
   Groq (openai/gpt-oss-120b) ? OpenRouter (nvidia/nemotron-3.5-lightning:free)
"""
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import config

# Supported models
_ALL_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemma-4-31b-it",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemma-3-27b-it",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro-001",
]

# Which provider answered the last call
last_provider = "Groq / OpenRouter"


def build_chain(starting_model: str | None = None) -> list:
    preferred = (starting_model or "").strip()
    if preferred and preferred in _ALL_MODELS:
        idx = _ALL_MODELS.index(preferred)
        return _ALL_MODELS[idx:] + _ALL_MODELS[:idx]
    return list(_ALL_MODELS)


_client = None
_client_key = None


def gemini_configured() -> bool:
    key = getattr(config, "GEMINI_API_KEY", "") or ""
    return bool(key) and not key.upper().startswith("YOUR_")


def _get_client():
    global _client, _client_key
    if _client is None or _client_key != config.GEMINI_API_KEY:
        from google import genai
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
        _client_key = config.GEMINI_API_KEY
    return _client


def _is_gone(err: Exception) -> bool:
    msg = str(err)
    return any(k in msg for k in ["404", "NOT_FOUND", "not found", "is not supported"])


def _should_switch_model(err: Exception) -> bool:
    msg = str(err)
    return _is_gone(err) or any(k in msg for k in [
        "429", "RESOURCE_EXHAUSTED", "quota", "rate limit",
        "503", "UNAVAILABLE", "overloaded", "high demand",
        "500", "INTERNAL",
        "10053", "10054", "Connection aborted", "Connection reset", "ConnectError",
        "RemoteDisconnected", "timed out", "Timeout", "Temporary failure", "NameResolution",
    ])


def _generate_gemini(prompt: str, starting_model: str | None) -> str:
    global last_provider
    from google.genai import types
    client = _get_client()
    chain  = build_chain(starting_model or getattr(config, "GEMINI_MODEL", None))

    for model in chain:
        for attempt in range(3):
            try:
                print(f"   ? Using Gemini ({model})?")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.9),
                )
                last_provider = f"Gemini ({model})"
                return response.text.strip()
            except Exception as e:
                if _is_gone(e):
                    break
                if _should_switch_model(e):
                    if attempt < 2:
                        time.sleep(10 * (attempt + 1))
                else:
                    raise
    raise RuntimeError("Direct Gemini models busy")


def generate(prompt: str, starting_model: str | None = None) -> str:
    global last_provider
    from apis import llm

    gemini_err = None
    if gemini_configured():
        try:
            return _generate_gemini(prompt, starting_model)
        except Exception as e:
            gemini_err = e
            if not llm.providers():
                raise
            print(f"   ? Gemini unavailable ({str(e)[:80]}) ? switching to Groq / OpenRouter fallback?")
    else:
        print("   ? Routing to Groq / OpenRouter?")

    try:
        text = llm.chat(prompt)
        last_provider = getattr(llm, "last_provider", "Groq / OpenRouter")
        return text
    except Exception as e:
        if gemini_err:
            raise RuntimeError(f"Gemini failed: {gemini_err}\nGroq/OpenRouter failed: {e}") from e
        raise RuntimeError(f"Groq/OpenRouter generation failed: {e}") from e
