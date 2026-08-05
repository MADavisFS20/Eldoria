"""Ported from HomeRegionContentTest.kt: direct tests of home_region_content.graft()."""
from eldoria.data import dialogue_content, home_region_content
from eldoria.models import Biome, GameLocation, PopulationTier

HOME_NAMES = {
    "Oakhaven Village", "Whispering Woods", "Deep Whispering Woods", "Shadow Caves",
    "Sunken Citadel Courtyard", "Old Forest Road", "Ironstone Foothills", "Ironstone Mountain Pass",
    "Dragon's Peak Summit", "Eastern Swamps", "Coastal Town of Port Eldoria", "Sunken Shipwreck",
    "Northern Mountain Pass", "Ancient Ruins", "Forgotten Crypt",
}


def _fake_surrounding_locations(anchor_x: int, anchor_y: int) -> dict[str, GameLocation]:
    """A minimal stand-in world: just enough neighbor tiles for graft() to have something to read/leave alone."""
    locations: dict[str, GameLocation] = {}
    for dx in range(-2, 5):
        for dy in range(-4, 4):
            x, y = anchor_x + dx, anchor_y + dy
            loc_id = f"{x}_{y}"
            locations[loc_id] = GameLocation(
                id=loc_id, x=x, y=y, biome=Biome.PLAINS,
                name=f"Wild {loc_id}", description="placeholder",
                population_tier=PopulationTier.WILDERNESS, difficulty_tier=1, difficulty_score=20,
                beings=(), exits={},
            )
    return locations


def test_graft_adds_exactly_15_locations():
    locations = _fake_surrounding_locations(50, 50)
    before = len(locations)
    home_region_content.graft(locations, 50, 50)

    assert len(locations) == before, "graft replaces existing tiles at its offsets, it doesn't grow the map"
    actual_names = {loc.name for loc in locations.values() if loc.name in HOME_NAMES}
    assert actual_names == HOME_NAMES


def test_every_exit_resolves_to_a_real_location():
    locations = _fake_surrounding_locations(50, 50)
    home_region_content.graft(locations, 50, 50)
    oakhaven = next(loc for loc in locations.values() if loc.name == "Oakhaven Village")
    home_region_ids = {loc.id for loc in locations.values() if loc.name in HOME_NAMES}

    for loc in locations.values():
        if loc.id not in home_region_ids:
            continue
        for direction, dest_id in loc.exits.items():
            assert dest_id in locations, f"{loc.name}'s '{direction}' exit points at {dest_id}, which doesn't exist"

    west = oakhaven.exits["west"]
    assert west not in home_region_ids, "Oakhaven's west exit should be the gateway to the wider world"


def test_home_region_is_a_closed_loop_except_oakhaven_west():
    locations = _fake_surrounding_locations(50, 50)
    home_region_content.graft(locations, 50, 50)
    home_region_ids = {loc.id for loc in locations.values() if loc.name in HOME_NAMES}

    for loc in locations.values():
        if loc.id not in home_region_ids:
            continue
        outside_exits = {d: dest for d, dest in loc.exits.items() if dest not in home_region_ids}
        if loc.name == "Oakhaven Village":
            assert len(outside_exits) == 1, "Oakhaven should have exactly one exit leaving the home region (west)"
        else:
            assert not outside_exits, f"{loc.name} has an unexpected exit leaving the home region: {outside_exits}"


def test_named_quest_givers_placed_where_expected():
    locations = _fake_surrounding_locations(50, 50)
    home_region_content.graft(locations, 50, 50)
    oakhaven = next(loc for loc in locations.values() if loc.name == "Oakhaven Village")
    ironstone_foothills = next(loc for loc in locations.values() if loc.name == "Ironstone Foothills")
    sunken_citadel = next(loc for loc in locations.values() if loc.name == "Sunken Citadel Courtyard")

    assert any(b.name == home_region_content.ELDER_THERON for b in oakhaven.beings)
    assert any(b.name == home_region_content.OAKHAVEN_MERCHANT for b in oakhaven.beings)
    assert any(b.name == home_region_content.MOUNTAIN_GUIDE for b in ironstone_foothills.beings)
    assert any(b.name == home_region_content.MOUNTAIN_KEEPER for b in ironstone_foothills.beings)
    assert any(b.name == home_region_content.ARCANE_VENDOR for b in sunken_citadel.beings)


def test_quest_items_present_at_source_locations():
    locations = _fake_surrounding_locations(50, 50)
    home_region_content.graft(locations, 50, 50)
    deep_woods = next(loc for loc in locations.values() if loc.name == "Deep Whispering Woods")
    shadow_caves = next(loc for loc in locations.values() if loc.name == "Shadow Caves")
    eastern_swamps = next(loc for loc in locations.values() if loc.name == "Eastern Swamps")

    assert any(i.name == home_region_content.ITEM_ANCIENT_RELIC for i in deep_woods.items)
    assert sum(1 for i in shadow_caves.items if i.name == home_region_content.ITEM_GLOWING_MUSHROOM) == home_region_content.GLOWING_MUSHROOM_REQUIRED
    assert sum(1 for i in eastern_swamps.items if i.name == home_region_content.ITEM_SWAMP_HERB) == home_region_content.SWAMP_HERB_REQUIRED


def test_trader_names_match_trader_archetype():
    trader_names = [
        home_region_content.OAKHAVEN_MERCHANT, home_region_content.COASTAL_TRADER,
        home_region_content.MOUNTAIN_KEEPER, home_region_content.ARCANE_VENDOR,
    ]
    for name in trader_names:
        assert dialogue_content.archetype_for(name) == dialogue_content.NpcArchetype.TRADER, \
            f"{name} must resolve to the TRADER archetype for commands.open_shop() to find it"
