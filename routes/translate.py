from flask import Blueprint, request, jsonify, render_template
from services.translation import translate_to_kannada
from services.conversation import get_follow_ups

translate_bp = Blueprint("translate", __name__)


@translate_bp.route("/")
def home():
    return render_template("index.html")


@translate_bp.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    source_lang = data.get("source_lang", "en")
    formality = data.get("formality", "polite")
    situation = data.get("situation", "general")

    if not text:
        return jsonify({"error": "Text is required"}), 400
    if len(text) > 500:
        return jsonify({"error": "Text too long (max 500 chars)"}), 400
    if source_lang not in ("en", "hi"):
        return jsonify({"error": "source_lang must be 'en' or 'hi'"}), 400

    result = translate_to_kannada(text, source_lang, formality, situation)
    follow_ups = get_follow_ups(situation)

    return jsonify({
        "input": text,
        "kannada": result["kannada"],
        "transliteration": result["transliteration"],
        "meaning": result["meaning"],
        "source": result["source"],
        "situation": situation,
        "follow_ups": follow_ups,
    })
