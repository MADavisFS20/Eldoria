"""Optional local-LLM assist via Ollama: free-text command interpretation and in-character NPC replies.

Entirely best-effort. If Ollama isn't running, the model isn't pulled, or a call
times out, every function here returns None and callers fall back to the
existing rigid-command / canned-dialogue behavior -- the game never depends
on this module to function. Model output is never executed directly: command
interpretation is re-validated against the fixed verb dispatch table, and NPC
replies are just a line of text appended to the log.
"""
from __future__ import annotations

import os
import time

import requests

HOST = os.environ.get("ELDORIA_LLM_HOST", "http://127.0.0.1:11434")
MODEL = os.environ.get("ELDORIA_LLM_MODEL", "qwen2.5:0.5b")
ENABLED = os.environ.get("ELDORIA_LLM_ENABLED", "1") != "0"

_CONNECT_TIMEOUT = 2.0
_READ_TIMEOUT = 8.0
_DOWN_RETRY_SECONDS = 30.0

_last_failure_at: float | None = None

KNOWN_VERBS = (
    "look, map, character, inventory, journal, codex, chronicle, north, south, east, west, up, down, "
    "go <place>, enter, leave, talk <name>, train, attack <name>, take <item>, equip <item>, craft <item>, "
    "rest, sleep, hire, fire, shop, buy <item>, sell <item>, travel <place>, sail <place>, bank, "
    "deposit <amount>, withdraw <amount>, property, business, invest <business>, start <business>, "
    "gamble <amount>, prompt, help"
)


def _server_reachable() -> bool:
    global _last_failure_at
    if not ENABLED:
        return False
    if _last_failure_at is not None and (time.monotonic() - _last_failure_at) < _DOWN_RETRY_SECONDS:
        return False
    return True


def _mark_failure() -> None:
    global _last_failure_at
    _last_failure_at = time.monotonic()


def _mark_success() -> None:
    global _last_failure_at
    _last_failure_at = None


def _generate(prompt: str, num_predict: int = 40) -> str | None:
    if not _server_reachable():
        return None
    try:
        resp = requests.post(
            f"{HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": num_predict},
            },
            timeout=(_CONNECT_TIMEOUT, _READ_TIMEOUT),
        )
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
    except (requests.RequestException, ValueError):
        _mark_failure()
        return None
    _mark_success()
    return text or None


def _first_line(text: str) -> str:
    return text.strip().splitlines()[0].strip().strip('"') if text.strip() else ""


def interpret_command(raw_text: str, exits: list[str], being_names: list[str]) -> str | None:
    """Map free-form player text to one line in the game's command grammar, or None on failure/refusal."""
    prompt = (
        "You translate a text-adventure player's free-form sentence into exactly one command line "
        "from this game's fixed grammar. Reply with ONLY the command line, nothing else. "
        "If nothing fits, reply with exactly: NONE\n\n"
        f"Available commands: {KNOWN_VERBS}\n"
        f"Exits here: {', '.join(exits) or '(none)'}\n"
        f"People/creatures here: {', '.join(being_names) or '(none)'}\n\n"
        f"Player said: \"{raw_text}\"\n"
        "Command:"
    )
    text = _generate(prompt, num_predict=20)
    if text is None:
        return None
    line = _first_line(text)
    if not line or line.upper() == "NONE":
        return None
    return line


def npc_reply(*, name: str, kind_label: str, disposition_label: str, location: str, player_message: str) -> str | None:
    """One short in-character line from an ambient NPC responding to free-form player speech."""
    prompt = (
        f"You are {name}, a {disposition_label.lower()} {kind_label.lower()} in the fantasy kingdom of Eldoria, "
        f"currently at {location}. A traveler just said to you: \"{player_message}\"\n"
        "Reply in character with ONE short sentence (max ~20 words) of spoken dialogue only -- no narration, "
        "no stage directions, no mention of game mechanics, rules, or that you are an AI. "
        "Reply:"
    )
    text = _generate(prompt, num_predict=50)
    if text is None:
        return None
    line = _first_line(text)
    return line or None
