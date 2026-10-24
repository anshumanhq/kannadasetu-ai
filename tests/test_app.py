import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app


def make_client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_home():
    client = make_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"KannadaSetu" in res.data


def test_translate_verified_phrase():
    client = make_client()
    res = client.post(
        "/api/translate",
        json={"text": "Thank you", "source_lang": "en", "situation": "general"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["source"] == "verified_phrase"
    assert "ಧನ್ಯವಾದಗಳು" in data["kannada"]


def test_translate_missing_text():
    client = make_client()
    res = client.post("/api/translate", json={"text": ""})
    assert res.status_code == 400


def test_translate_fallback():
    client = make_client()
    res = client.post(
        "/api/translate",
        json={"text": "This is a very unique sentence not in db 12345", "source_lang": "en"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["source"] in ("fallback", "api")


def test_situations_list():
    client = make_client()
    res = client.get("/api/situations")
    assert res.status_code == 200
    assert "hospital" in res.get_json()["situations"]


def test_situation_detail():
    client = make_client()
    res = client.get("/api/situations/hospital")
    assert res.status_code == 200
    data = res.get_json()
    assert data["situation"] == "hospital"
    assert len(data["phrases"]) > 0


def test_situation_unknown():
    client = make_client()
    res = client.get("/api/situations/xyz")
    assert res.status_code == 404


def test_phrasebook():
    client = make_client()
    res = client.get("/api/phrasebook")
    assert res.status_code == 200
    assert len(res.get_json()["phrases"]) >= 30


def test_compare():
    client = make_client()
    res = client.post(
        "/api/compare", json={"reference": "ನಮಸ್ಕಾರ", "spoken": "ನಮಸ್ಕಾರ"}
    )
    assert res.status_code == 200
    assert res.get_json()["similarity"] == 100.0


def test_compare_missing():
    client = make_client()
    res = client.post("/api/compare", json={"reference": "", "spoken": ""})
    assert res.status_code == 400
