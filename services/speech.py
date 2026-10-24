import difflib

import requests
from config import Config


def synthesize_speech(text: str) -> dict:
    """Try configured TTS provider; fall back to browser speechSynthesis."""
    if Config.SPEECH_API_URL and Config.SPEECH_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {Config.SPEECH_API_KEY}"}
            r = requests.post(
                Config.SPEECH_API_URL,
                json={"text": text, "language": "kn"},
                headers=headers,
                timeout=10,
            )
            if r.ok:
                data = r.json()
                if data.get("audio_url"):
                    return {"audio_url": data["audio_url"], "source": "api"}
        except Exception as e:
            print(f"[speech] TTS error: {e}")

    return {
        "audio_url": None,
        "source": "browser",
        "message": "Browser speechSynthesis fallback",
        "lang": "kn-IN",
    }


def compare_pronunciation(reference: str, spoken: str) -> dict:
    """Lexical similarity only — NOT phonetic scoring. Be honest in the UI."""
    ref = reference.strip().lower()
    sp = spoken.strip().lower()
    ratio = difflib.SequenceMatcher(None, ref, sp).ratio()
    return {
        "similarity": round(ratio * 100, 2),
        "reference": reference,
        "spoken": spoken,
        "note": "Lexical similarity only. Not phonetic scoring.",
    }
