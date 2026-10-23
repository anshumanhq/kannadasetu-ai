import json
import re

import requests
from config import Config

FOLLOW_UPS = {
    "hospital": [
        {"en": "Where is the doctor?", "kn": "ವೈದ್ಯರು ಎಲ್ಲಿದ್ದಾರೆ?"},
        {"en": "I have a headache.", "kn": "ನನಗೆ ತಲೆನೋವು ಇದೆ."},
        {"en": "How much is the consultation?", "kn": "ಪರೀಕ್ಷೆ ಶುಲ್ಕ ಎಷ್ಟು?"},
    ],
    "bus_stand": [
        {"en": "Which bus goes to the railway station?", "kn": "ರೈಲ್ವೆ ನಿಲ್ದಾಣಕ್ಕೆ ಯಾವ ಬಸ್ ಹೋಗುತ್ತದೆ?"},
        {"en": "How much is the ticket?", "kn": "ಟಿಕೆಟ್ ಎಷ್ಟು?"},
        {"en": "Where does this bus stop?", "kn": "ಈ ಬಸ್ ಎಲ್ಲಿ ನಿಲ್ಲುತ್ತದೆ?"},
    ],
    "railway_station": [
        {"en": "Which platform?", "kn": "ಯಾವ ಪ್ಲಾಟ್‌ಫಾರ್ಮ್?"},
        {"en": "When is the next train?", "kn": "ಮುಂದಿನ ರೈಲು ಯಾವಾಗ?"},
        {"en": "Where is the ticket counter?", "kn": "ಟಿಕೆಟ್ ಕೌಂಟರ್ ಎಲ್ಲಿದೆ?"},
    ],
    "market": [
        {"en": "How much does this cost?", "kn": "ಇದರ ಬೆಲೆ ಎಷ್ಟು?"},
        {"en": "Can you reduce the price?", "kn": "ಸ್ವಲ್ಪ ಕಡಿಮೆ ಮಾಡಿ."},
        {"en": "Give me one kilo.", "kn": "ಒಂದು ಕಿಲೋ ಕೊಡಿ."},
    ],
    "college": [
        {"en": "Where is the admission office?", "kn": "ಪ್ರವೇಶ ಕಚೇರಿ ಎಲ್ಲಿದೆ?"},
        {"en": "What is the fee structure?", "kn": "ಶುಲ್ಕ ರಚನೆ ಏನು?"},
        {"en": "When do classes start?", "kn": "ತರಗತಿಗಳು ಯಾವಾಗ ಪ್ರಾರಂಭ?"},
    ],
    "workplace": [
        {"en": "Where is the meeting?", "kn": "ಸಭೆ ಎಲ್ಲಿದೆ?"},
        {"en": "Can we talk tomorrow?", "kn": "ನಾಳೆ ಮಾತನಾಡಬಹುದೇ?"},
        {"en": "Please send the file.", "kn": "ದಯವಿಟ್ಟು ಫೈಲ್ ಕಳುಹಿಸಿ."},
    ],
    "general": [
        {"en": "How are you?", "kn": "ಹೇಗಿದ್ದೀರಿ?"},
        {"en": "Thank you.", "kn": "ಧನ್ಯವಾದಗಳು."},
        {"en": "Please help me.", "kn": "ದಯವಿಟ್ಟು ಸಹಾಯ ಮಾಡಿ."},
    ],
}


def _static_follow_ups(situation: str):
    return FOLLOW_UPS.get(situation, FOLLOW_UPS["general"])


def get_follow_ups(situation: str, user_input: str = ""):
    """Try LLM via OpenRouter; fall back to static list on any failure."""
    if Config.LLM_API_URL and Config.LLM_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {Config.LLM_API_KEY}",
                "Content-Type": "application/json",
                # OpenRouter attribution headers — required for many models
                "HTTP-Referer": "https://github.com/kannadasetu-ai",
                "X-OpenRouter-Title": "KannadaSetu AI",
            }
            prompt = (
                f"User is in a '{situation}' situation in Karnataka. "
                f"They said: '{user_input}'. "
                "Suggest 3 short Kannada follow-up phrases with English meaning. "
                "Return ONLY a JSON array, no extra text, in this exact format: "
                "[{\"kn\": \"...\", \"en\": \"...\"}]"
            )
            payload = {
                "model": "poolside/laguna-s-2.1:free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
            }
            r = requests.post(
                Config.LLM_API_URL, json=payload, headers=headers, timeout=15
            )
            if r.ok:
                content = r.json()["choices"][0]["message"]["content"]
                match = re.search(r"\[.*\]", content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed
            else:
                print(f"[conversation] OpenRouter error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[conversation] LLM error: {e}")

    return _static_follow_ups(situation)