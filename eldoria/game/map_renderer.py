"""Bordered ASCII viewport of the map centered on the player, plus a structured grid for the web map panel.

True fog of war: a tile only ever shows a symbol once the player has
physically stood on it (session.discovered_locations) -- everything else is
blank.
"""
from __future__ import annotations

from eldoria.game.session import GameSession
from eldoria.models import GameLocation, Item, PopulationTier, RealmKind, SpawnEntry, TerrainKind
from eldoria.models.sub_realm import SubRealmRoom

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


def _being_payload(being: SpawnEntry) -> dict:
    return {"name": being.name, "kind": being.kind.name, "disposition": being.disposition.name}


def _item_payload(item: Item) -> dict:
    return {"name": item.name}


def _current_spot_beings_items(session: GameSession) -> tuple[list[dict], list[dict]]:
    """Only ever computed for the player's actual current spot -- respects respawn/defeated/taken state."""
    beings = [_being_payload(b) for _, b in session.current_beings()]
    items = [_item_payload(i) for _, i in session.current_items()]
    return beings, items


def _overworld_tile_payload(session: GameSession, loc: GameLocation) -> dict:
    is_here = loc.id == session.location_id
    beings, items = _current_spot_beings_items(session) if is_here else ([], [])
    return {
        "id": loc.id,
        "x": loc.x,
        "y": loc.y,
        "biome": loc.biome.name,
        "terrain": loc.terrain.name,
        "population_tier": loc.population_tier.name,
        "hazard": loc.hazard.name if loc.hazard is not None else None,
        "portal_kind": loc.portal_kind.name if loc.portal_kind is not None else None,
        "exits": sorted(loc.exits.keys()),
        "beings": beings,
        "items": items,
    }


def _room_payload(session: GameSession, room: SubRealmRoom) -> dict:
    beings, items = _current_spot_beings_items(session)
    sub_realm = session.current_sub_realm()
    return {
        "id": room.id,
        "biome": sub_realm.biome.name if sub_realm is not None else None,
        "difficulty_tier": room.difficulty_tier,
        "is_boss_room": room.is_boss_room,
        "is_entry_room": sub_realm is not None and room.id == sub_realm.entry_room_id,
        "exits": sorted(room.exits.keys()),
        "beings": beings,
        "items": items,
    }


def tiles_3d(session: GameSession, cx: int | None = None, cy: int | None = None, radius: int = 3) -> dict:
    """Renderable tile/room data for the 3D client, honoring the same true fog-of-war rule as grid()/render().

    Undiscovered overworld tiles are omitted entirely. Only the player's actual
    current spot ever carries live beings/items (everywhere else can't reflect
    respawn/defeat/taken state, so it's left empty rather than stale or spoiling).
    """
    here = session.current_location
    room = session.current_room()
    if room is not None:
        return {"you": {"x": here.x, "y": here.y}, "room": _room_payload(session, room)}

    world = session.world
    cx = here.x if cx is None else cx
    cy = here.y if cy is None else cy
    tiles = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            x, y = cx + dx, cy + dy
            if x < 0 or y < 0 or x >= world.width or y >= world.height:
                continue
            loc = world.location_at(x, y)
            if loc is None or loc.id not in session.discovered_locations:
                continue
            tiles.append(_overworld_tile_payload(session, loc))
    return {"you": {"x": here.x, "y": here.y}, "tiles": tiles}


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
