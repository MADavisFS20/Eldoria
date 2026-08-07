"""Bordered ASCII viewport of the map centered on the player, plus a structured grid for the web map panel.

True fog of war: a tile only ever shows a symbol once the player has
physically stood on it (session.discovered_locations) -- everything else is
blank.
"""
from __future__ import annotations

from eldoria.game.session import GameSession
from eldoria.models import Biome, PopulationTier, RealmKind, TerrainKind

_HALF_WIDTH = 12
_HALF_HEIGHT = 6

_LEGEND = (
    "Legend: @=you  C=city  v=village  D=dungeon  S=sky realm  ~=water  "
    "==bridge  !=hazard  .=explored  (blank)=undiscovered  |  "
    "tile color=biome (blue=sea white=tundra green=jungle tan=plains sand=desert gray=mountains)  |  "
    "black glyphs=landmarks"
)

_BIOME_CLASS = {
    Biome.SEA: "sea",
    Biome.TUNDRA: "tundra",
    Biome.JUNGLE: "jungle",
    Biome.PLAINS: "plains",
    Biome.DESERT: "desert",
    Biome.MOUNTAINS: "mountains",
}


def _symbol_and_style(session: GameSession, x: int, y: int) -> tuple[str, str, str]:
    """Returns (symbol, text style, biome background class)."""
    world = session.world
    here = session.current_location
    if x == here.x and y == here.y:
        return "@", "cyan", _BIOME_CLASS[here.biome]
    if x < 0 or y < 0 or x >= world.width or y >= world.height:
        return " ", "plain", ""
    loc = world.location_at(x, y)
    if loc is None or loc.id not in session.discovered_locations:
        return " ", "plain", ""
    biome_cls = _BIOME_CLASS[loc.biome]
    if loc.portal_kind == RealmKind.DUNGEON:
        return "D", "landmark", biome_cls
    if loc.portal_kind == RealmKind.SKY_REALM:
        return "S", "landmark", biome_cls
    if loc.population_tier == PopulationTier.CITY:
        return "C", "landmark", biome_cls
    if loc.population_tier == PopulationTier.COUNTRYSIDE:
        return "v", "landmark", biome_cls
    if loc.hazard is not None:
        return "!", "red", biome_cls
    if loc.terrain == TerrainKind.BRIDGE:
        return "=", "yellow", biome_cls
    if loc.terrain == TerrainKind.WATERWAY:
        return "~", "blue", biome_cls
    return ".", "white", biome_cls


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
            symbol, _, _ = _symbol_and_style(session, x, y)
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
            symbol, style, biome = _symbol_and_style(session, x, y)
            row.append({"symbol": symbol, "style": style, "biome": biome})
        rows.append(row)
    return {"rows": rows, "legend": _LEGEND}
