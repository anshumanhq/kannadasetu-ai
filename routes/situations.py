from flask import Blueprint, jsonify
from services.translation import load_phrases

situations_bp = Blueprint("situations", __name__)

SITUATIONS = [
    "hospital",
    "bus_stand",
    "railway_station",
    "market",
    "college",
    "workplace",
    "general",
]


@situations_bp.route("/api/situations")
def list_situations():
    return jsonify({"situations": SITUATIONS})


@situations_bp.route("/api/situations/<name>")
def get_situation(name):
    if name not in SITUATIONS:
        return jsonify({"error": "Unknown situation"}), 404
    phrases = load_phrases()
    matched = [p for p in phrases if p.get("situation") == name]
    return jsonify({"situation": name, "phrases": matched})


@situations_bp.route("/api/phrasebook")
def phrasebook():
    return jsonify({"phrases": load_phrases()})
