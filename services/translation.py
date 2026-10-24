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


def _api_translate(text: str, source_lang: str, target_lang: str = "kn"):
    """Attempt hosted translation API. Returns None on failure or missing config."""
    if not Config.TRANSLATION_API_URL or not Config.TRANSLATION_API_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {Config.TRANSLATION_API_KEY}"}
        payload = {"text": text, "source": source_lang, "target": target_lang}
        r = requests.post(
            Config.TRANSLATION_API_URL, json=payload, headers=headers, timeout=10
        )
        if r.ok:
            data = r.json()
            return data.get("translated_text") or data.get("translation")
    except Exception as e:
        print(f"[translation] API error: {e}")
    return None


def translate_to_kannada(
    text: str,
    source_lang: str = "en",
    formality: str = "polite",
    situation: str = "general",
) -> dict:
    phrase = find_phrase(text, source_lang)
    if phrase:
        return {
            "kannada": phrase["kannada"],
            "transliteration": phrase.get("transliteration", ""),
            "meaning": phrase.get("english") if source_lang == "hi" else phrase.get("hindi", ""),
            "source": "verified_phrase",
        }

    api_result = _api_translate(text, source_lang)
    if api_result:
        return {
            "kannada": api_result,
            "transliteration": "",
            "meaning": text,
            "source": "api",
        }

    return {
        "kannada": "ಕ್ಷಮಿಸಿ, ಈ ವಾಕ್ಯವು ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ.",
        "transliteration": "Kshamisi, ee vaakyavu innu labhyavilla.",
        "meaning": "Sorry, this sentence is not available yet.",
        "source": "fallback",
    }
