"""FastAPI backend for Eldoria: character creation, one command per request, and state for the side panel/map."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from eldoria.game import character_panel, commands, engine, map_renderer
from eldoria.game.commands import Log
from eldoria.game.session import GameSession
from eldoria.models import CharacterClass, Race
from eldoria.web import session_store

app = FastAPI(title="Eldoria")


class NewGameRequest(BaseModel):
    name: str
    race: str
    character_class: str


class ContinueRequest(BaseModel):
    session_id: str


class CommandRequest(BaseModel):
    session_id: str
    text: str


def _log_to_json(log: Log) -> list[dict]:
    return [{"style": style, "text": text} for style, text in log.lines]


def _state(session: GameSession) -> dict:
    room = session.current_room()
    return {
        "character": character_panel.sheet_data(session.player),
        "inventory": character_panel.inventory_data(session.player),
        "journal": commands.journal_data(session),
        "alive": session.player.is_alive,
        "pending_prompt": session.pending_prompt,
        "location_name": room.name if room else session.current_location.name,
        "in_sub_realm": session.in_sub_realm,
    }


@app.get("/api/meta")
def meta() -> dict:
    return {
        "races": [
            {"id": r.name, "display_name": r.display_name, "lore": r.lore, "resistance_lore": r.resistance_lore}
            for r in Race
        ],
        "classes": [
            {"id": c.name, "display_name": c.display_name, "description": c.description}
            for c in CharacterClass
        ],
    }


@app.post("/api/new_game")
def new_game(req: NewGameRequest) -> dict:
    try:
        race = Race[req.race.upper()]
        character_class = CharacterClass[req.character_class.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Unknown race or class")
    session, log = engine.new_game(req.name, race, character_class)
    session_id = session_store.create(session)
    return {"session_id": session_id, "log": _log_to_json(log), "state": _state(session)}


@app.post("/api/continue_game")
def continue_game(req: ContinueRequest) -> dict:
    result = engine.continue_game(req.session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No save found for that session")
    session, log = result
    session_store.put(req.session_id, session)
    return {"session_id": req.session_id, "log": _log_to_json(log), "state": _state(session)}


@app.post("/api/command")
def command(req: CommandRequest) -> dict:
    session = session_store.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session -- start or continue a game first")
    log = engine.execute_command(session, req.session_id, req.text)
    return {"log": _log_to_json(log), "state": _state(session)}


@app.get("/api/state/{session_id}")
def state(session_id: str) -> dict:
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")
    return _state(session)


@app.get("/api/map/{session_id}")
def map_state(session_id: str) -> dict:
    """The whole-world map is ~600KB of cell data -- fetched only when the Map tab is opened,
    not embedded in every /api/command response."""
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")
    return {"map": map_renderer.grid(session)}


_static_dir = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")
