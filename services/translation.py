import json
import os
from functools import lru_cache

import requests
from config import Config


@lru_cache(maxsize=1)
def load_phrases():
    path = Config.PHRASES_PATH
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(text: str) -> str:
    return text.strip().lower().rstrip(".!?।")


def find_phrase(text: str, source_lang: str = "en"):
    n = _normalize(text)
    for p in load_phrases():
        if source_lang == "en" and _normalize(p.get("english", "")) == n:
            return p
        if source_lang == "hi" and _normalize(p.get("hindi", "")) == n:
            return p
    return None


def _has_kannada_script(text: str) -> bool:
    """Check if the string contains at least one Kannada-script character."""
    return any("\u0C80" <= c <= "\u0CFF" for c in text)


# ---------- Cloudflare Workers AI (IndicTrans2) ----------
def _cloudflare_translate(text: str, target_lang: str = "kan_Knda"):
    if not Config.TRANSLATION_API_URL or not Config.TRANSLATION_API_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {Config.TRANSLATION_API_KEY}"}
        payload = {"text": text, "target_language": target_lang}
        r = requests.post(
            Config.TRANSLATION_API_URL, json=payload, headers=headers, timeout=20
        )

        # DEBUG: always print status + short body so we can see exactly what CF says
        print(
            f"[translation] CF status={r.status_code} body={r.text[:400]}"
        )

        if not r.ok:
            return None

        data = r.json()

        # Cloudflare sometimes returns 200 with embedded errors
        if data.get("success") is False:
            print(f"[translation] CF embedded errors: {data.get('errors')}")
            return None

        result = data.get("result") or {}
        translated = None

        # ACTUAL Cloudflare shape: {"result": {"translations": ["..."]}}
        if isinstance(result, dict):
            translations = result.get("translations")
            if isinstance(translations, list) and translations:
                translated = translations[0]
            if not translated:
                translated = result.get("translated_text")

        # Rare alternate shape
        if not translated:
            translated = data.get("translated_text")

        if translated and isinstance(translated, str) and translated.strip():
            return translated.strip()
        return None
    except Exception as e:
        print(f"[translation] CF exception: {e}")
        return None


# ---------- OpenRouter LLM fallback for translation ----------
def _llm_translate(text: str, source_lang: str):
    if not Config.LLM_API_URL or not Config.LLM_API_KEY:
        return None
    try:
        headers = {
            "Authorization": f"Bearer {Config.LLM_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/kannadasetu-ai",
            "X-OpenRouter-Title": "KannadaSetu AI",
        }
        src_name = {"en": "English", "hi": "Hindi"}.get(source_lang, "English")
        prompt = (
            f"Translate the following {src_name} sentence to natural, everyday Kannada. "
            "Reply with ONLY the Kannada translation in Kannada script. "
            "No transliteration. No quotes. No extra text. No explanation.\n\n"
            f"{src_name}: {text}\nKannada:"
        )
        payload = {
            "model": "poolside/laguna-s-2.1:free",  # model jo tumhare follow-ups me kaam kar raha hai
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        r = requests.post(
            Config.LLM_API_URL, json=payload, headers=headers, timeout=20
        )
        if not r.ok:
            print(f"[translation] LLM fallback HTTP {r.status_code}: {r.text[:300]}")
            return None

        content = r.json()["choices"][0]["message"]["content"].strip()
        # Clean common LLM artifacts
        content = content.strip().strip('"').strip("'").strip()
        for prefix in ("Kannada:", "kannada:", "Translation:", "translation:"):
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
        if content and _has_kannada_script(content):
            return content
        print(f"[translation] LLM returned non-Kannada: {content[:200]}")
        return None
    except Exception as e:
        print(f"[translation] LLM fallback exception: {e}")
        return None


# ---------- Main entry point ----------
def translate_to_kannada(
    text: str,
    source_lang: str = "en",
    formality: str = "polite",
    situation: str = "general",
) -> dict:
    # 1. Verified phrasebook (fast, accurate, free)
    phrase = find_phrase(text, source_lang)
    if phrase:
        return {
            "kannada": phrase["kannada"],
            "transliteration": phrase.get("transliteration", ""),
            "meaning": (
                phrase.get("english")
                if source_lang == "hi"
                else phrase.get("hindi", "")
            ),
            "source": "verified_phrase",
        }

    # 2. Cloudflare IndicTrans2
    cf_result = _cloudflare_translate(text)
    if cf_result:
        return {
            "kannada": cf_result,
            "transliteration": "",
            "meaning": text,
            "source": "cloudflare",
        }

    # 3. OpenRouter LLM (works reliably as we saw with follow-ups)
    llm_result = _llm_translate(text, source_lang)
    if llm_result:
        return {
            "kannada": llm_result,
            "transliteration": "",
            "meaning": text,
            "source": "llm",
        }

    # 4. Static honest fallback
    return {
        "kannada": "ಕ್ಷಮಿಸಿ, ಈ ವಾಕ್ಯವು ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ.",
        "transliteration": "Kshamisi, ee vaakyavu innu labhyavilla.",
        "meaning": "Sorry, this sentence is not available yet.",
        "source": "fallback",
    }