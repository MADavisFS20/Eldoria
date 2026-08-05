"""Bordered ASCII viewport of the map centered on the player, plus a structured grid for the web map panel.

True fog of war: a tile only ever shows a symbol once the player has
physically stood on it (session.discovered_locations) -- everything else is
blank.
"""
from __future__ import annotations

from eldoria.game.session import GameSession
from eldoria.models import PopulationTier, RealmKind, TerrainKind

_HALF_WIDTH = 12
_HALF_HEIGHT = 6

_LEGEND = (
    "Legend: @=you  C=city  v=village  D=dungeon  S=sky realm  ~=water  "
    "==bridge  !=hazard  .=explored  (blank)=undiscovered"
)


def _symbol_and_style(session: GameSession, x: int, y: int) -> tuple[str, str]:
    world = session.world
    here = session.current_location
    if x == here.x and y == here.y:
        return "@", "cyan"
    if x < 0 or y < 0 or x >= world.width or y >= world.height:
        return " ", "plain"
    loc = world.location_at(x, y)
    if loc is None or loc.id not in session.discovered_locations:
        return " ", "plain"
    if loc.portal_kind == RealmKind.DUNGEON:
        return "D", "red"
    if loc.portal_kind == RealmKind.SKY_REALM:
        return "S", "blue"
    if loc.population_tier == PopulationTier.CITY:
        return "C", "yellow"
    if loc.population_tier == PopulationTier.COUNTRYSIDE:
        return "v", "yellow"
    if loc.hazard is not None:
        return "!", "red"
    if loc.terrain == TerrainKind.BRIDGE:
        return "=", "yellow"
    if loc.terrain == TerrainKind.WATERWAY:
        return "~", "blue"
    return ".", "white"


def render(session: GameSession) -> str:
    """Plain-text ASCII rendering (no color) -- used when the map is embedded directly into the log."""
    here = session.current_location
    width = _HALF_WIDTH * 2 + 1
    lines = ["+" + "-" * width + "+"]
    for dy in range(-_HALF_HEIGHT, _HALF_HEIGHT + 1):
        y = here.y + dy
        row = ["|"]
        for dx in range(-_HALF_WIDTH, _HALF_WIDTH + 1):
            x = here.x + dx
            symbol, _ = _symbol_and_style(session, x, y)
            row.append(symbol)
        row.append("|")
        lines.append("".join(row))
    lines.append("+" + "-" * width + "+")
    lines.append(_LEGEND)
    return "\n".join(lines)


def grid(session: GameSession) -> dict:
    """Structured cell data for the web map panel: rows of {symbol, style} cells, centered on the player."""
    here = session.current_location
    rows = []
    for dy in range(-_HALF_HEIGHT, _HALF_HEIGHT + 1):
        y = here.y + dy
        row = []
        for dx in range(-_HALF_WIDTH, _HALF_WIDTH + 1):
            x = here.x + dx
            symbol, style = _symbol_and_style(session, x, y)
            row.append({"symbol": symbol, "style": style})
        rows.append(row)
    return {"rows": rows, "legend": _LEGEND}
