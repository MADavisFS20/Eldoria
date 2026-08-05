"""In-memory GameSession registry, keyed by a server-generated session id.

A restart loses in-memory sessions, but any session that ever slept or hit
the autosave interval is recoverable via /api/continue_game (which
regenerates the World from its seed and restores the on-disk Snapshot).
"""
from __future__ import annotations

import uuid

from eldoria.game.session import GameSession

_sessions: dict[str, GameSession] = {}


def create(session: GameSession) -> str:
    session_id = uuid.uuid4().hex
    _sessions[session_id] = session
    return session_id


def get(session_id: str) -> GameSession | None:
    return _sessions.get(session_id)


def put(session_id: str, session: GameSession) -> None:
    _sessions[session_id] = session


def remove(session_id: str) -> None:
    _sessions.pop(session_id, None)
