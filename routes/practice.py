from flask import Blueprint, request, jsonify, render_template
from services.speech import synthesize_speech, compare_pronunciation

practice_bp = Blueprint("practice", __name__)


@practice_bp.route("/practice")
def practice_page():
    return render_template("practice.html")


@practice_bp.route("/api/tts", methods=["POST"])
def tts():
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = synthesize_speech(text)
    return jsonify(result)


@practice_bp.route("/api/compare", methods=["POST"])
def compare():
    data = request.get_json() or {}
    reference = (data.get("reference") or "").strip()
    spoken = (data.get("spoken") or "").strip()

    if not reference or not spoken:
        return jsonify({"error": "Both 'reference' and 'spoken' are required"}), 400

    result = compare_pronunciation(reference, spoken)
    return jsonify(result)
