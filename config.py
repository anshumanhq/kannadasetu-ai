import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # Translation API (IndicTrans2 / BHASHINI / any hosted provider)
    TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "")
    TRANSLATION_API_URL = os.getenv("TRANSLATION_API_URL", "")

    # Speech (TTS / ASR)
    SPEECH_API_KEY = os.getenv("SPEECH_API_KEY", "")
    SPEECH_API_URL = os.getenv("SPEECH_API_URL", "")

    # LLM for contextual follow-ups
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_API_URL = os.getenv("LLM_API_URL", "")

    # Phrase database
    PHRASES_PATH = os.path.join(
        os.path.dirname(__file__), "data", "verified_phrases.json"
    )
