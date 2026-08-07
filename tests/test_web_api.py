"""Basic coverage for the FastAPI layer (new in the Python port, no Kotlin equivalent)."""
from fastapi.testclient import TestClient

from eldoria.web.main import app

client = TestClient(app)


def test_meta_lists_races_and_classes():
    r = client.get("/api/meta")
    assert r.status_code == 200
    data = r.json()
    assert len(data["races"]) == 5
    assert len(data["classes"]) == 7


def test_new_game_then_command_round_trip():
    r = client.post("/api/new_game", json={"name": "Testy", "race": "ELF", "character_class": "MAGE"})
    assert r.status_code == 200
    data = r.json()
    session_id = data["session_id"]
    assert data["state"]["character"]["name"] == "Testy"
    assert data["state"]["character"]["race"] == "Elf"

    r = client.post("/api/command", json={"session_id": session_id, "text": "look"})
    assert r.status_code == 200
    assert len(r.json()["log"]) > 0

    r = client.get(f"/api/state/{session_id}")
    assert r.status_code == 200
    assert "map" not in r.json()

    r = client.get(f"/api/map/{session_id}")
    assert r.status_code == 200
    assert "rows" in r.json()["map"]


def test_new_game_rejects_unknown_race():
    r = client.post("/api/new_game", json={"name": "X", "race": "NOPE", "character_class": "WARRIOR"})
    assert r.status_code == 400


def test_command_on_unknown_session_is_404():
    r = client.post("/api/command", json={"session_id": "does-not-exist", "text": "look"})
    assert r.status_code == 404


def test_continue_game_with_no_save_is_404():
    r = client.post("/api/continue_game", json={"session_id": "no-such-save"})
    assert r.status_code == 404


def test_static_files_served():
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/style.css").status_code == 200


