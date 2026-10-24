# KannadaSetu AI

**Understand Kannada. Navigate life. Connect with people.**

An AI-powered Kannada communication assistant for non-Kannada speakers in Karnataka — travel, shopping, healthcare, college and everyday situations.

Built for **Kannada Technology Challenge — Statement 03: Kannada in Everyday Life**.

---

## Quick Start

```
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure APIs
cp .env.example .env
# Edit .env with your API keys

# 4. Run
python app.py
# Open http://localhost:5000
```

## Features

| Feature | Status |
| --- | --- |
| Context-aware phrase translation (EN/HI → KN) | Done |
| Kannada script + Roman transliteration + meaning | Done |
| Situations: bus, railway, hospital, market, college, workplace | Done |
| Verified phrasebook (30+ curated phrases) | Done |
| Audio playback (browser TTS, API-ready) | Done |
| Speak & practice (mic + lexical similarity) | Done |
| Contextual follow-up suggestions | Done |
| Offline phrasebook fallback when APIs fail | Done |

## Architecture

```
Browser (HTML/CSS/JS)
       |
       v
   Flask API
   |-- /api/translate          -> services/translation.py
   |-- /api/situations         -> routes/situations.py
   |-- /api/phrasebook         -> routes/situations.py
   |-- /api/tts                -> services/speech.py
   |-- /api/compare            -> services/speech.py
       |
       |-- data/verified_phrases.json  (SQLite-ready)
       |-- (optional) External APIs:
           * IndicTrans2 / BHASHINI (translation)
           * TTS / ASR provider (speech)
           * LLM (contextual replies)
```

**Design philosophy:**

1. Verified phrase match first (fast, correct, free)
2. API translation if configured
3. Graceful fallback + offline phrasebook if APIs fail

## Why the fallback message appears

If you type a sentence that is not in the verified phrasebook AND no translation API is configured in `.env`, the app responds with:

```
ಕ್ಷಮಿಸಿ, ಈ ವಾಕ್ಯವು ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ.
Kshamisi, ee vaakyavu innu labhyavilla.
Sorry, this sentence is not available yet.
```

This is **intentional** — we never invent unverified Kannada. To get real translations for arbitrary sentences, configure `TRANSLATION_API_URL` and `TRANSLATION_API_KEY` in `.env`.

To see verified phrases in action, try these inputs (English):

- Hello
- Thank you
- How are you?
- I need to go to the railway station.
- How much is the ticket?
- Where is the doctor?
- How much does this cost?

## Running Tests

```
pytest tests/ -v
```

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `TRANSLATION_API_URL` / `_KEY` | Hosted translation API (IndicTrans2 / BHASHINI) |
| `SPEECH_API_URL` / `_KEY` | TTS provider (falls back to browser) |
| `LLM_API_URL` / `_KEY` | Optional LLM for follow-ups |

**Without any keys**, the app still works using the verified phrasebook, browser speech synthesis, and lexical comparison.

## Project Structure

```
kannadasetu-ai/
|-- app.py
|-- config.py
|-- requirements.txt
|-- .env.example
|-- routes/
|   |-- translate.py
|   |-- practice.py
|   |-- situations.py
|-- services/
|   |-- translation.py
|   |-- speech.py
|   |-- conversation.py
|-- data/
|   |-- verified_phrases.json
|-- templates/
|   |-- index.html
|   |-- practice.html
|-- static/
|   |-- css/style.css
|   |-- js/
|       |-- main.js
|       |-- practice.js
|-- tests/
|   |-- test_app.py
|-- README.md
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET  | `/`                       | Main translate page |
| GET  | `/practice`               | Speak & practice page |
| POST | `/api/translate`          | Translate EN/HI text to Kannada |
| GET  | `/api/situations`         | List all situations |
| GET  | `/api/situations/<name>`  | Get phrases for a situation |
| GET  | `/api/phrasebook`         | Get full verified phrasebook |
| POST | `/api/tts`                | Text-to-speech |
| POST | `/api/compare`            | Compare spoken vs reference |

### Example: Translate API

Request:

```
POST /api/translate
Content-Type: application/json

{
  "text": "Thank you",
  "source_lang": "en",
  "situation": "general"
}
```

Response:

```
{
  "input": "Thank you",
  "kannada": "ಧನ್ಯವಾದಗಳು",
  "transliteration": "Dhanyavaadagalu",
  "meaning": "",
  "source": "verified_phrase",
  "situation": "general",
  "follow_ups": [...]
}
```

## How This Differs From Google Translate

- **Situation-aware**: Follow-ups stay relevant to the chosen context
- **Verified phrasebook**: Human-reviewed Kannada phrases marked distinctly from AI output
- **Transliteration always shown**: Learners can read Kannada without knowing the script
- **Offline safe**: Core phrasebook works without network
- **Honest scoring**: Similarity is labelled as lexical, not phonetic
- **Never guesses**: Falls back clearly instead of inventing unverified Kannada

## Testing Manually

1. Open http://localhost:5000
2. Select language = English, situation = General
3. Type `Thank you` and click **Translate to Kannada**
4. Verify:
   - Kannada text = ಧನ್ಯವಾದಗಳು
   - Transliteration = Dhanyavaadagalu
   - Badge = "Verified phrase" (green)
5. Click **Play** — browser should speak the Kannada text (requires `kn-IN` voice; Chrome/Edge recommended)
6. Click a follow-up phrase — it should auto-translate
7. Open http://localhost:5000/practice — try **Listen**, **Record** (mic), **Compare**

## Roadmap

- [ ] Wire real IndicTrans2 / BHASHINI endpoint
- [ ] SQLite + admin review workflow for phrasebook
- [ ] PWA service worker for true offline mode
- [ ] Whisper-based Kannada ASR for better practice
- [ ] Native-speaker reviewed test set (30–50 scenarios)
- [ ] Expand phrasebook to 100+ verified phrases

## 🏆 Hackathon Alignment

**Kannada Technology Challenge**

**Primary Statement:** Problem 03 — Kannada in Everyday Life

**Secondary Coverage:**
- Problem 01 (Language Learning) — Speak & Practice mode, transliteration, guided phrases
- Problem 02 (Voice & Speech) — Browser TTS playback, mic-based pronunciation practice

**Problem 03 ko kaise solve karta hai:**

| Real-world situation | KannadaSetu feature |
| --- | --- |
| Travelling (bus, railway) | Situation mode + verified travel phrases |
| Shopping / market | Price negotiation, quantity phrases |
| Healthcare / hospital | Symptom and doctor communication phrases |
| College / admission | Fee, office, class schedule phrases |
| Workplace | Meeting, file sharing, follow-up phrases |

**Differentiator (Why not just Google Translate?):**

1. **Verified-first pipeline** — Human-reviewed phrases pehle, AI fallback baad me
2. **Situation-aware follow-ups** — Context ke hisaab se next phrase suggest karta hai
3. **Transliteration always visible** — Bina Kannada script jaane bhi user bol sakta hai
4. **Offline-safe core** — API fail hone par bhi phrasebook kaam karta hai
5. **Honest scoring** — Pronunciation ko "lexical similarity" label karta hai, fake phonetic score nahi

**Judge Demo Flow (90 seconds):**

```
1. Type "I need to go to the railway station" → situation: bus_stand
2. Output: Kannada script + transliteration + meaning + Play button
3. Click follow-up "How much is the ticket?" → auto-translates in context
4. Simulate API failure → fallback phrasebook still works
5. Show pytest output: all tests passing
```

## License

MIT