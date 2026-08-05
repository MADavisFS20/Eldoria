"""Single-player local save, one JSON file per session id under saves/.

Same atomic write pattern as the old engine's jvmMain SaveManager: write to a
.tmp file, delete the old save, rename the tmp into place -- crash-mid-write
safe.
"""
from __future__ import annotations

import json
from pathlib import Path

from eldoria.game.session import Snapshot

_SAVES_DIR = Path(__file__).resolve().parent.parent.parent / "saves"


def _paths(session_id: str) -> tuple[Path, Path]:
    _SAVES_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return _SAVES_DIR / f"{safe_id}.json", _SAVES_DIR / f"{safe_id}.json.tmp"


def exists(session_id: str) -> bool:
    save_file, _ = _paths(session_id)
    return save_file.exists()


def save(session_id: str, snapshot: Snapshot) -> None:
    save_file, tmp_file = _paths(session_id)
    tmp_file.write_text(json.dumps(snapshot.to_dict()))
    if save_file.exists():
        save_file.unlink()
    tmp_file.rename(save_file)


def load(session_id: str) -> Snapshot | None:
    save_file, _ = _paths(session_id)
    if not save_file.exists():
        return None
    return Snapshot.from_dict(json.loads(save_file.read_text()))
