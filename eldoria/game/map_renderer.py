"""Bordered ASCII viewport of the map centered on the player, plus a structured full-world
grid for the web map panel.

Two different fog-of-war rules apply to two different things:
 - Terrain (biome coloring, rivers, bridges) is visible across the whole world from the very
   start -- it's geography, not a secret.
 - Landmarks (cities, villages, dungeon/sky-realm portals, hazards) only appear once the player
   has physically stood on that tile (session.discovered_locations); until then the tile shows
   its terrain color with no symbol at all.
"""
from __future__ import annotations

from eldoria.game.session import GameSession
from eldoria.models import Biome, PopulationTier, RealmKind, TerrainKind

_HALF_WIDTH = 12
_HALF_HEIGHT = 6

_LEGEND = (
    "Legend: @=you  C=city  v=village  D=dungeon  S=sky realm  ~=water  ==bridge  !=hazard  "
    ".=visited  (blank glyph)=undiscovered landmark  |  "
    "tile color=biome, visible everywhere (blue=sea white=tundra green=jungle tan=plains sand=desert gray=mountains)  |  "
    "black glyphs=discovered landmarks"
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
    """Returns (symbol, text style, biome background class).

    Terrain (the biome background class, plus rivers/bridges) shows unconditionally. Landmark
    glyphs (city/village/portal/hazard) and the "visited" dot only show once discovered.
    """
    world = session.world
    here = session.current_location
    if x == here.x and y == here.y:
        return "@", "cyan", _BIOME_CLASS[here.biome]
    if x < 0 or y < 0 or x >= world.width or y >= world.height:
        return " ", "plain", ""
    loc = world.location_at(x, y)
    if loc is None:
        return " ", "plain", ""
    biome_cls = _BIOME_CLASS[loc.biome]
    discovered = loc.id in session.discovered_locations
    if discovered:
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
    return (".", "white", biome_cls) if discovered else (" ", "plain", biome_cls)


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
    """Structured cell data for the web map panel: the WHOLE world, every tile -- not a viewport
    around the player. Terrain is visible everywhere from the start; landmark symbols only
    appear once discovered (see _symbol_and_style)."""
    world = session.world
    rows = []
    for y in range(world.height):
        row = []
        for x in range(world.width):
            symbol, style, biome = _symbol_and_style(session, x, y)
            row.append({"symbol": symbol, "style": style, "biome": biome})
        rows.append(row)
    return {"rows": rows, "legend": _LEGEND}
