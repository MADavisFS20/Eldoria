"""The 15 hand-authored, tightly connected home-region locations (Oakhaven Village and surroundings).

Spliced onto the deterministically-generated start city (see world_generator's
`graft` call) so every new game keeps this same tested content while the much
larger procedural world remains reachable beyond it -- Oakhaven's `west` exit
is the one deliberate gateway out.

Deliberately NOT wired through the procedural SideQuestKind machinery: these
quests are fetch-quests gated on specific items or kill counts, resolved
through a yes/no accept during `talk` and an automatic turn-in on a later
`talk` -- driven from commands.py's `talk()` using plain string quest ids in
GameSession.active_home_region_quests/completed_side_quests.
"""
from __future__ import annotations

import random
from dataclasses import replace

from eldoria.models import (
    Biome,
    Disposition,
    GameLocation,
    Item,
    ItemKind,
    PopulationTier,
    SpawnEntry,
    SpawnKind,
    StatusEffect,
    TerrainKind,
)
from eldoria.data.ai_companion_lore import MR_DAVIS_NAME
from eldoria.world import stat_generator as sg

# --- Quest ids (GameSession.active_home_region_quests / completed_side_quests keys) ---
QUEST_ANCIENT_RELIC = "ancient_relic"
QUEST_POISONED_WATERS = "poisoned_waters"
QUEST_GOBLIN_OUTBREAK = "goblin_outbreak"
QUEST_LOST_CARGO = "lost_cargo"
QUEST_MOUNTAIN_RESCUE = "mountain_rescue"
QUEST_SLAY_THE_WYRM = "slay_the_wyrm"
QUEST_ALCHEMICAL_FUNGI = "alchemical_fungi"
QUEST_ANCIENT_COMPASS = "ancient_compass"

QUEST_TITLES: dict[str, str] = {
    QUEST_ANCIENT_RELIC: "The Ancient Relic",
    QUEST_POISONED_WATERS: "The Poisoned Waters",
    QUEST_GOBLIN_OUTBREAK: "Goblin Outbreak",
    QUEST_LOST_CARGO: "Lost Cargo",
    QUEST_MOUNTAIN_RESCUE: "Mountain Rescue",
    QUEST_SLAY_THE_WYRM: "Slay the Wyrm",
    QUEST_ALCHEMICAL_FUNGI: "Alchemical Fungi",
    QUEST_ANCIENT_COMPASS: "The Ancient Compass",
}

# --- Named NPCs (exact names commands.py's handle_home_region_npc matches on) ---
ELDER_THERON = "Elder Theron"
FISHERMAN_FINN = "Fisherman Finn"
MOUNTAIN_GUIDE = "Mountain Guide"
ARCANE_VENDOR = "Arcane Vendor"
ANCIENT_SCHOLAR = "Ancient Scholar"
LOST_MINER = "Lost Miner"

# Trader names deliberately contain a dialogue_content TRADER keyword
# (trader/merchant/keeper/vendor) so commands.py's open_shop() finds them
# with zero changes -- see world/shop_generator.py's doc.
OAKHAVEN_MERCHANT = "Oakhaven General Merchant"
COASTAL_TRADER = "Coastal Market Trader"
MOUNTAIN_KEEPER = "Ironstone Outpost Keeper"

# --- Quest item names (checked by name in commands.py's handle_home_region_npc) ---
ITEM_ANCIENT_RELIC = "Ancient Relic"
ITEM_SWAMP_HERB = "Swamp Herb"
ITEM_SHIP_MANIFEST = "Ship's Manifest"
ITEM_LOST_MINER_NOTE = "Lost Miner's Note"
ITEM_ANCIENT_COMPASS = "Ancient Compass"
ITEM_GLOWING_MUSHROOM = "Glowing Mushroom"
SWAMP_HERB_REQUIRED = 3
GLOWING_MUSHROOM_REQUIRED = 2
GOBLINS_REQUIRED = 3


def _enemy(name: str, tier: int, seed: int, resistances: frozenset[StatusEffect] = frozenset()) -> SpawnEntry:
    stats = sg.creature_stats(tier, random.Random(seed))
    if resistances:
        stats = replace(stats, status_resistances=frozenset(resistances))
    return SpawnEntry(name=name, kind=SpawnKind.CREATURE, disposition=Disposition.HOSTILE, stats=stats)


def _npc(name: str, seed: int, tier: int = 1) -> SpawnEntry:
    return SpawnEntry(
        name=name, kind=SpawnKind.NPC, disposition=Disposition.PASSIVE,
        stats=sg.creature_stats(tier, random.Random(seed)),
    )


def _goblin(seed: int) -> SpawnEntry:
    return _enemy("Goblin Scavenger", 1, seed)


def _dire_wolf(seed: int) -> SpawnEntry:
    return _enemy("Dire Wolf", 1, seed)


def _mountain_goat(seed: int) -> SpawnEntry:
    return _enemy("Mountain Goat", 1, seed)


def _giant_toad(seed: int) -> SpawnEntry:
    return _enemy("Giant Toad", 2, seed, frozenset({StatusEffect.BURN}))


def _bandit_outlaw(seed: int) -> SpawnEntry:
    return _enemy("Bandit Outlaw", 2, seed)


def _giant_crab(seed: int) -> SpawnEntry:
    return _enemy("Giant Crab", 2, seed, frozenset({StatusEffect.POISON}))


def _shadow_cultist(seed: int) -> SpawnEntry:
    return _enemy("Shadow Cultist", 3, seed)


def _skeletal_warrior(seed: int) -> SpawnEntry:
    return _enemy("Skeletal Warrior", 3, seed, frozenset({StatusEffect.POISON}))


def _stone_golem(seed: int) -> SpawnEntry:
    return _enemy("Stone Golem", 4, seed, frozenset({StatusEffect.POISON, StatusEffect.BURN}))


def _ancient_dragon(seed: int) -> SpawnEntry:
    return _enemy("Ancient Flame Dragon", 5, seed, frozenset({StatusEffect.BURN}))


def _quest_item(name: str, tier: int, seed: int) -> Item:
    return sg.quest_item(name, tier, random.Random(seed))


def _material(name: str, seed: int) -> Item:
    item = sg.quest_item(name, 1, random.Random(seed))
    return replace(item, kind=ItemKind.MATERIAL, value=5)


def graft(locations: dict[str, GameLocation], anchor_x: int, anchor_y: int) -> None:
    """Splices the 15 home-region locations into an already-generated location map, anchored at (anchor_x, anchor_y).

    Offsets are unique but NOT geometry-consistent with each location's
    cardinal exits (the map view is cosmetic-only, non-load-bearing); every
    location's exits map is hand-set to the original topology regardless of
    where it actually sits on the grid.

    Exits intentionally point INTO 14 ids this function itself creates -- a
    fully closed loop -- except Oakhaven's `west`, which is deliberately left
    pointing at whatever real generated tile already existed there before the
    graft: the one gateway from the tested home region out into the much
    larger procedural world.
    """

    def loc_id(dx: int, dy: int) -> str:
        return f"{anchor_x + dx}_{anchor_y + dy}"

    id_oakhaven = loc_id(0, 0)
    id_whispering_woods = loc_id(0, -1)
    id_deep_woods = loc_id(0, -2)
    id_shadow_caves = loc_id(1, -1)
    id_sunken_citadel = loc_id(2, -1)
    id_old_road = loc_id(1, 0)
    id_ironstone_foothills = loc_id(2, 0)
    id_ironstone_pass = loc_id(2, 1)
    id_dragons_peak = loc_id(2, 2)
    id_eastern_swamps = loc_id(0, 1)
    id_coastal_town = loc_id(1, 1)
    id_sunken_shipwreck = loc_id(1, 2)
    id_mountain_pass_north = loc_id(3, 0)
    id_ancient_ruins = loc_id(-1, -2)
    id_forgotten_crypt = loc_id(-1, -3)

    def place(
        loc_id_: str, dx: int, dy: int, name: str, description: str,
        exits: dict[str, str], population_tier: PopulationTier, difficulty_tier: int,
        beings: tuple[SpawnEntry, ...] = (), items: tuple[Item, ...] = (),
    ) -> None:
        locations[loc_id_] = GameLocation(
            id=loc_id_, x=anchor_x + dx, y=anchor_y + dy, biome=Biome.PLAINS,
            name=name, description=description, population_tier=population_tier,
            difficulty_tier=difficulty_tier, difficulty_score=difficulty_tier * 20,
            beings=beings, exits=exits, terrain=TerrainKind.LAND, items=items,
        )

    existing = locations.get(loc_id(-1, 0))
    existing_west_neighbor = existing.id if existing is not None else id_oakhaven

    place(
        id_oakhaven, 0, 0, "Oakhaven Village",
        "A serene village surrounding a central square. The air smells of fresh bread and damp earth.",
        {"north": id_whispering_woods, "east": id_old_road, "south": id_eastern_swamps, "west": existing_west_neighbor},
        PopulationTier.CITY, 1,
        beings=(_npc(ELDER_THERON, seed=101), _npc(OAKHAVEN_MERCHANT, seed=102), _npc(MR_DAVIS_NAME, seed=110)),
    )
    place(
        id_whispering_woods, 0, -1, "Whispering Woods",
        "Dense forest with howling wind through misty trees. Ancient, gnarled trees loom overhead.",
        {"south": id_oakhaven, "north": id_deep_woods, "east": id_shadow_caves},
        PopulationTier.WILDERNESS, 1,
        beings=(_dire_wolf(201), _goblin(202)),
    )
    place(
        id_deep_woods, 0, -2, "Deep Whispering Woods",
        "Pitch dark canopy where sunlight cannot reach. Strange sounds echo from the shadows.",
        {"south": id_whispering_woods, "west": id_ancient_ruins},
        PopulationTier.WILDERNESS, 2,
        beings=(_goblin(203), _dire_wolf(204)),
        items=(_quest_item(ITEM_ANCIENT_RELIC, 2, 301),),
    )
    place(
        id_shadow_caves, 1, -1, "Shadow Caves",
        "Damp limestone cave network dripping with glowing flora. The air is cool and still.",
        {"west": id_whispering_woods, "east": id_sunken_citadel},
        PopulationTier.WILDERNESS, 2,
        beings=(_goblin(205), _giant_toad(206)),
        items=(_material(ITEM_GLOWING_MUSHROOM, 302), _material(ITEM_GLOWING_MUSHROOM, 303)),
    )
    place(
        id_sunken_citadel, 2, -1, "Sunken Citadel Courtyard",
        "Ancient flooded stone fortress radiating dark power. Water laps at crumbling walls.",
        {"west": id_shadow_caves},
        PopulationTier.CITY, 3,
        beings=(_npc(ARCANE_VENDOR, seed=103), _shadow_cultist(207), _skeletal_warrior(208)),
    )
    place(
        id_old_road, 1, 0, "Old Forest Road",
        "Long dirt path connecting distant provinces. Wagon tracks are faintly visible.",
        {"west": id_oakhaven, "east": id_ironstone_foothills, "south": id_coastal_town},
        PopulationTier.WILDERNESS, 1,
        beings=(_goblin(209), _bandit_outlaw(210)),
    )
    place(
        id_ironstone_foothills, 2, 0, "Ironstone Foothills",
        "Rocky ascending terrain surrounded by jagged cliff faces. The wind picks up here.",
        {"west": id_old_road, "north": id_ironstone_pass, "east": id_mountain_pass_north},
        PopulationTier.CITY, 2,
        beings=(_npc(MOUNTAIN_GUIDE, seed=104), _npc(MOUNTAIN_KEEPER, seed=105), _bandit_outlaw(211), _mountain_goat(212)),
    )
    place(
        id_ironstone_pass, 2, 1, "Ironstone Mountain Pass",
        "Freezing mountain path with howling blizzards. The air is thin and cold.",
        {"south": id_ironstone_foothills, "up": id_dragons_peak},
        PopulationTier.WILDERNESS, 4,
        beings=(_stone_golem(213), _mountain_goat(214)),
    )
    place(
        id_dragons_peak, 2, 2, "Dragon's Peak Summit",
        "High volcanic summit covered in ancient scorch marks. A faint smell of sulfur lingers.",
        {"down": id_ironstone_pass},
        PopulationTier.WILDERNESS, 5,
        beings=(_ancient_dragon(215),),
    )
    place(
        id_eastern_swamps, 0, 1, "Eastern Swamps",
        "A murky, humid marshland. Strange plants and buzzing insects fill the air.",
        {"north": id_oakhaven},
        PopulationTier.WILDERNESS, 1,
        beings=(_giant_toad(216), _dire_wolf(217)),
        items=tuple(_material(ITEM_SWAMP_HERB, 310 + i) for i in range(SWAMP_HERB_REQUIRED)),
    )
    place(
        id_coastal_town, 1, 1, "Coastal Town of Port Eldoria",
        "A bustling port town with the scent of salt and fish. Ships dock constantly.",
        {"north": id_old_road, "east": id_sunken_shipwreck},
        PopulationTier.CITY, 2,
        beings=(_npc(FISHERMAN_FINN, seed=106), _npc(COASTAL_TRADER, seed=107)),
    )
    place(
        id_sunken_shipwreck, 1, 2, "Sunken Shipwreck",
        "The remains of a grand ship, half-submerged in shallow waters.",
        {"west": id_coastal_town},
        PopulationTier.WILDERNESS, 2,
        beings=(_giant_crab(218),),
        items=(_quest_item(ITEM_SHIP_MANIFEST, 2, 304),),
    )
    place(
        id_mountain_pass_north, 3, 0, "Northern Mountain Pass",
        "A narrow, icy path winding through towering peaks.",
        {"west": id_ironstone_foothills, "north": id_forgotten_crypt},
        PopulationTier.WILDERNESS, 3,
        beings=(_mountain_goat(219), _stone_golem(220), _npc(LOST_MINER, seed=108)),
    )
    place(
        id_ancient_ruins, -1, -2, "Ancient Ruins",
        "Crumbling stone structures overgrown with vines.",
        {"east": id_deep_woods, "north": id_forgotten_crypt},
        PopulationTier.WILDERNESS, 3,
        beings=(_skeletal_warrior(221), _shadow_cultist(222), _npc(ANCIENT_SCHOLAR, seed=109)),
    )
    place(
        id_forgotten_crypt, -1, -3, "Forgotten Crypt",
        "A dark, musty crypt beneath the ancient ruins.",
        {"south": id_ancient_ruins, "west": id_mountain_pass_north},
        PopulationTier.WILDERNESS, 4,
        beings=(_skeletal_warrior(223),),
        items=(_quest_item(ITEM_ANCIENT_COMPASS, 3, 305),),
    )
