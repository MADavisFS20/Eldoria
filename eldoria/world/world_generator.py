"""Deterministic, fully hardcoded-rules world generator.

No AI, no network, no runtime text generation beyond combining fixed word
banks. The same seed always produces the exact same map.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from eldoria.data import biome_content, family_content, home_region_content, skill_trainer_content, sub_realm_theme
from eldoria.models import (
    ArtifactKind,
    Biome,
    DiceFormula,
    DieType,
    Disposition,
    GameLocation,
    HazardKind,
    Item,
    ItemKind,
    PopulationTier,
    RealmKind,
    SideQuestKind,
    SpawnEntry,
    SpawnKind,
    Subclass,
    TerrainKind,
    World,
)
from eldoria.world import stat_generator as sg
from eldoria.world import sub_realm_generator
from eldoria.world.deterministic_random import make_random
from eldoria.world.world_config import WorldConfig

Pos = tuple[int, int]


@dataclass(frozen=True)
class _CellInfo:
    biome: Biome
    tier: int
    score: int


@dataclass(frozen=True)
class _Portal:
    sub_realm_id: str
    kind: RealmKind
    name: str
    description: str


@dataclass(frozen=True)
class _Settlement:
    pos: Pos
    name: str
    tier: PopulationTier


def _cell_random(world_seed: int, x: int, y: int, salt: int = 0) -> random.Random:
    return make_random(world_seed, x, y, salt)


def _manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _place_points(candidates: list[Pos], count: int, min_dist: int, rng: random.Random, excluded: set[Pos]) -> list[Pos]:
    if count <= 0:
        return []
    shuffled = list(candidates)
    rng.shuffle(shuffled)
    chosen: list[Pos] = []
    dist = min_dist
    while len(chosen) < count and dist >= 0:
        for c in shuffled:
            if len(chosen) >= count:
                break
            if c in excluded:
                continue
            if all(_manhattan(existing, c) >= dist for existing in chosen):
                chosen.append(c)
        dist -= 3
    excluded.update(chosen)
    return chosen


def generate(config: WorldConfig | None = None) -> World:
    if config is None:
        config = WorldConfig()
    assert config.width * config.height >= 10_000, "Map must contain at least 10,000 locations"

    biome_order = list(Biome)  # 6 bands, left (west) to right (east)
    band_count = len(biome_order)

    # --- 1. Per-row jittered band boundaries (jagged borders between biomes) ---
    def boundaries_for_row(row: int) -> list[int]:
        w = config.width
        ideal = [(w * (i + 1)) // band_count for i in range(band_count - 1)]
        jittered = list(ideal)
        for i in range(len(ideal)):
            r = _cell_random(config.seed, i, row, salt=9001)
            jittered[i] = max(1, min(w - 1, ideal[i] + r.randint(-3, 3)))
        for i in range(1, len(jittered)):
            if jittered[i] <= jittered[i - 1] + 5:
                jittered[i] = jittered[i - 1] + 5
        if jittered and jittered[-1] >= w - 5:
            jittered[-1] = w - 5
        boundaries = [0] * (band_count + 1)
        for i, v in enumerate(jittered):
            boundaries[i + 1] = v
        boundaries[band_count] = w
        return boundaries

    # --- 2. Compute biome + difficulty for every cell ---
    grid: list[list[_CellInfo]] = [[None] * config.width for _ in range(config.height)]  # type: ignore[list-item]
    for y in range(config.height):
        boundaries = boundaries_for_row(y)
        for x in range(config.width):
            band_index = band_count - 1
            for i in range(band_count):
                if boundaries[i] <= x < boundaries[i + 1]:
                    band_index = i
                    break
            band_start = boundaries[band_index]
            band_end = boundaries[band_index + 1]
            band_width = max(1, band_end - band_start)
            local_x = x - band_start
            frac = local_x / max(1, band_width - 1)
            score = max(1, min(100, int(1 + frac * 99.0)))
            tier = max(1, min(5, ((score - 1) // 20) + 1))
            grid[y][x] = _CellInfo(biome_order[band_index], tier, score)

    # --- 2.5. Carve waterways: rivers cut west-to-east through the 5 land biomes,
    # impassable on foot except at periodic bridges. ---
    terrain_grid: list[list[TerrainKind]] = [[TerrainKind.LAND] * config.width for _ in range(config.height)]
    river_rng = make_random(config.seed, 13131)
    river_rows: list[int] = []
    for _ in range(config.river_count):
        row = river_rng.randint(8, config.height - 9)
        guard = 0
        while any(abs(r - row) < 12 for r in river_rows) and guard < 30:
            row = river_rng.randint(8, config.height - 9)
            guard += 1
        river_rows.append(row)
    for row in river_rows:
        y = row
        path: list[Pos] = []
        for x in range(config.width):
            step_rng = _cell_random(config.seed, x, row, salt=7777)
            if step_rng.randrange(100) < 35:
                y += step_rng.randint(-1, 1)
            y = max(2, min(config.height - 3, y))
            path.append((x, y))
            terrain_grid[y][x] = TerrainKind.WATERWAY
        for i, (bx, by) in enumerate(path):
            if i % config.bridge_spacing == config.bridge_spacing // 2:
                terrain_grid[by][bx] = TerrainKind.BRIDGE

    # --- 3. Group cells by biome & tier for settlement/portal placement ---
    cells_by_biome_tier: dict[Biome, dict[int, list[Pos]]] = {b: {} for b in biome_order}
    for y in range(config.height):
        for x in range(config.width):
            info = grid[y][x]
            if info.biome != Biome.SEA and terrain_grid[y][x] != TerrainKind.LAND:
                continue
            cells_by_biome_tier[info.biome].setdefault(info.tier, []).append((x, y))

    settlements_by_biome: dict[Biome, list[_Settlement]] = {}
    trainer_at: dict[Pos, skill_trainer_content.TrainerTemplate] = {}

    # Main-quest premise: exactly one village in the whole world hides the player's
    # long-lost family member, picked deterministically off the world seed.
    family_rng = make_random(config.seed, 424242)
    family_relation = family_rng.choice(family_content.CANDIDATES)
    family_biome = family_rng.choice(biome_order)
    family_village_index = family_rng.randrange(config.cities_per_biome * config.villages_per_city)
    family_member_at: dict[Pos, family_content.FamilyRelation] = {}

    # 26 small side quests, spread roughly evenly across all 12 cities, deterministic per seed.
    all_side_quests = list(SideQuestKind.all())
    make_random(config.seed, 24681357).shuffle(all_side_quests)
    total_cities = len(biome_order) * config.cities_per_biome
    quest_count_for_city = [
        len(all_side_quests) // total_cities + (1 if i < len(all_side_quests) % total_cities else 0)
        for i in range(total_cities)
    ]
    side_quest_at: dict[Pos, list[SideQuestKind]] = {}
    global_city_index = 0
    quest_cursor = 0

    for biome in biome_order:
        content = biome_content.get(biome)
        excluded: set[Pos] = set()
        rng = make_random(config.seed, list(Biome).index(biome), 42)

        city_candidates = cells_by_biome_tier[biome].get(1, [])
        cities = _place_points(city_candidates, config.cities_per_biome, 20, rng, excluded)

        village_candidates = cells_by_biome_tier[biome].get(1, []) + cells_by_biome_tier[biome].get(2, [])
        village_count = config.cities_per_biome * config.villages_per_city
        villages = _place_points(village_candidates, village_count, 7, rng, excluded)

        settlements: list[_Settlement] = []
        for i, pos in enumerate(cities):
            settlements.append(_Settlement(pos, content.city_names[i % len(content.city_names)], PopulationTier.CITY))
            trainer = skill_trainer_content.trainer_for(biome, i)
            if trainer is not None:
                trainer_at[pos] = trainer
            quest_count = quest_count_for_city[global_city_index]
            side_quest_at[pos] = all_side_quests[quest_cursor:quest_cursor + quest_count]
            quest_cursor += quest_count
            global_city_index += 1
        for i, pos in enumerate(villages):
            settlements.append(_Settlement(pos, content.village_names[i % len(content.village_names)], PopulationTier.COUNTRYSIDE))
            if biome == family_biome and i == family_village_index:
                family_member_at[pos] = family_relation
        settlements_by_biome[biome] = settlements

    settlement_at: dict[Pos, _Settlement] = {}
    for settlements in settlements_by_biome.values():
        for s in settlements:
            settlement_at[s.pos] = s

    # --- 4. Place dungeon (underground) and beanstalk (sky) portals ---
    excluded_cells: set[Pos] = set(settlement_at.keys())
    all_sub_realms: dict[str, object] = {}
    portal_at: dict[Pos, _Portal] = {}
    used_realm_names: set[str] = set()
    used_boss_names: set[str] = set()
    used_legendary_names: set[str] = set()
    used_quest_item_names: set[str] = set()
    sky_variant_counter = 0

    for biome in biome_order:
        rng = make_random(config.seed, list(Biome).index(biome), 777)

        # Dungeon mouths hide in the more dangerous reaches of the biome where possible.
        dangerous_candidates = [pos for t in (3, 4, 5) for pos in cells_by_biome_tier[biome].get(t, [])]
        all_biome_cells = [pos for cells in cells_by_biome_tier[biome].values() for pos in cells]
        dungeon_candidates = dangerous_candidates if len(dangerous_candidates) >= config.dungeons_per_biome * 3 else all_biome_cells

        dungeon_spots = _place_points(dungeon_candidates, config.dungeons_per_biome, 15, rng, excluded_cells)
        dungeon_theme = sub_realm_theme.dungeon_theme_for(biome)
        for spot in dungeon_spots:
            loc_id = f"{spot[0]}_{spot[1]}"
            sub_realm = sub_realm_generator.generate(
                kind=RealmKind.DUNGEON,
                biome=biome,
                theme=dungeon_theme,
                entrance_location_id=loc_id,
                world_seed=config.seed,
                room_count_range=config.dungeon_room_count_range,
                used_realm_names=used_realm_names,
                used_boss_names=used_boss_names,
                used_legendary_names=used_legendary_names,
                used_quest_item_names=used_quest_item_names,
            )
            all_sub_realms[sub_realm.id] = sub_realm
            portal_at[spot] = _Portal(
                sub_realm.id, RealmKind.DUNGEON,
                f"Entrance to {sub_realm.name}",
                f"A dark cave mouth yawns in the earth here, leading down into {sub_realm.name}. Something ancient stirs below.",
            )

        # Beanstalks can sprout anywhere in the biome, not just its dangerous edges.
        beanstalk_spots = _place_points(all_biome_cells, config.beanstalks_per_biome, 15, rng, excluded_cells)
        for spot in beanstalk_spots:
            loc_id = f"{spot[0]}_{spot[1]}"
            variant = sub_realm_theme.sky_theme_for(sky_variant_counter)
            sky_variant_counter += 1
            sub_realm = sub_realm_generator.generate(
                kind=RealmKind.SKY_REALM,
                biome=biome,
                theme=variant,
                entrance_location_id=loc_id,
                world_seed=config.seed,
                room_count_range=config.sky_room_count_range,
                used_realm_names=used_realm_names,
                used_boss_names=used_boss_names,
                used_legendary_names=used_legendary_names,
                used_quest_item_names=used_quest_item_names,
            )
            all_sub_realms[sub_realm.id] = sub_realm
            portal_at[spot] = _Portal(
                sub_realm.id, RealmKind.SKY_REALM,
                f"Beanstalk to {sub_realm.name}",
                f"An impossibly tall beanstalk climbs into the clouds here, leading up into {sub_realm.name}.",
            )

    # --- 4.5. Everything in the Sea band that isn't a settlement or portal is open water. ---
    for y in range(config.height):
        for x in range(config.width):
            if grid[y][x].biome == Biome.SEA and (x, y) not in settlement_at and (x, y) not in portal_at:
                terrain_grid[y][x] = TerrainKind.WATERWAY

    # --- 4.6. Three sunken treasures, hidden on random open-sea tiles. ---
    treasure_rng = make_random(config.seed, 24680)
    sea_water_cells = [
        (x, y) for y in range(config.height) for x in range(config.width)
        if grid[y][x].biome == Biome.SEA and terrain_grid[y][x] == TerrainKind.WATERWAY
    ]
    treasure_names = ["Sunken Treasure Chest", "Barnacled Strongbox", "Corsair's Buried Hoard"]
    treasure_at: dict[Pos, Item] = {}
    shuffled_sea = list(sea_water_cells)
    treasure_rng.shuffle(shuffled_sea)
    for i, pos in enumerate(shuffled_sea[:3]):
        value = DiceFormula(6, DieType.D20, 150).roll(treasure_rng)
        treasure_at[pos] = Item(
            name=treasure_names[i % len(treasure_names)], kind=ItemKind.TRINKET, tier=5,
            value=value, max_durability=1, is_legendary=True,
        )

    # --- 4.7. Vampire and Werewolf curse-givers -- exactly one of each. ---
    curse_rng = make_random(config.seed, 555999)
    subclass_giver_at: dict[Pos, Subclass] = {}
    vampire_candidates = [pos for t in (4, 5) for pos in cells_by_biome_tier[Biome.TUNDRA].get(t, []) if pos not in excluded_cells]
    if vampire_candidates:
        spot = curse_rng.choice(vampire_candidates)
        subclass_giver_at[spot] = Subclass.VAMPIRE
        excluded_cells.add(spot)
    werewolf_candidates = [pos for t in (4, 5) for pos in cells_by_biome_tier[Biome.JUNGLE].get(t, []) if pos not in excluded_cells]
    if werewolf_candidates:
        spot = curse_rng.choice(werewolf_candidates)
        subclass_giver_at[spot] = Subclass.WEREWOLF
        excluded_cells.add(spot)

    # --- 4.8. The Mad Scientist -- one homeless tinkerer, in exactly one city in the whole world. ---
    mad_science_rng = make_random(config.seed, 741852)
    city_positions = [pos for pos, s in settlement_at.items() if s.tier == PopulationTier.CITY]
    mad_scientist_at = mad_science_rng.choice(city_positions) if city_positions else None

    # --- 4.9. Three hidden sci-fi artifacts, one each in Desert, Mountains, and Tundra. ---
    artifact_rng = make_random(config.seed, 99001122)
    artifact_biomes = {
        Biome.DESERT: ArtifactKind.TELEPATH_DEVICE,
        Biome.MOUNTAINS: ArtifactKind.COERCION_DEVICE,
        Biome.TUNDRA: ArtifactKind.PRECOGNITION_DEVICE,
    }
    artifact_at: dict[Pos, Item] = {}
    for biome, kind in artifact_biomes.items():
        candidates = [pos for t in (4, 5) for pos in cells_by_biome_tier[biome].get(t, []) if pos not in excluded_cells]
        if not candidates:
            continue
        spot = artifact_rng.choice(candidates)
        excluded_cells.add(spot)
        artifact_at[spot] = Item(name=kind.item_name, kind=ItemKind.TRINKET, tier=5, value=0, max_durability=1, is_legendary=True)

    # --- 5. Build every GameLocation ---
    def wilderness_name(biome: Biome, x: int, y: int) -> str:
        content = biome_content.get(biome)
        rng = _cell_random(config.seed, x, y, salt=1)
        adjective = rng.choice(content.adjectives)
        feature = rng.choice(content.features)
        if rng.randrange(100) < 30:
            return f"{rng.choice(content.qualifiers)} {adjective} {feature}"
        return f"{adjective} {feature}"

    def wilderness_description(biome: Biome, name: str, tier: int) -> str:
        danger_line = {
            1: "It feels peaceful here; little seems capable of doing you harm.",
            2: "A faint sense of caution lingers in the air.",
            3: "This place feels genuinely dangerous.",
            4: "Every sound puts you on edge; something powerful could be near.",
        }.get(tier, "A deep, ancient dread hangs over this place.")
        return f"You stand in the {name}, deep within the {biome.display_name.lower()}. {danger_line}"

    def settlement_description(biome: Biome, name: str, tier: PopulationTier) -> str:
        if tier == PopulationTier.CITY:
            return f"{name} rises before you, a major hub of civilization amid the {biome.display_name.lower()}, bustling with residents and travelers."
        return f"{name} is a small, close-knit settlement in the {biome.display_name.lower()}, quiet but for the daily business of its few residents."

    def river_name(biome: Biome, terrain: TerrainKind) -> str:
        return f"{biome.display_name} River Crossing" if terrain == TerrainKind.BRIDGE else f"{biome.display_name} River"

    def river_description(biome: Biome, terrain: TerrainKind) -> str:
        if terrain == TerrainKind.BRIDGE:
            return "A weathered bridge carries the path across the river here, water rushing beneath the planks."
        return f"A river cuts across the {biome.display_name.lower()} here -- too deep and swift to cross on foot. You would need a boat, or a bridge."

    def pick_beings(biome: Biome, tier: int, population_tier: PopulationTier, x: int, y: int) -> list[SpawnEntry]:
        content = biome_content.get(biome)
        rng = _cell_random(config.seed, x, y, salt=2)
        beings: list[SpawnEntry] = []
        if population_tier == PopulationTier.WILDERNESS:
            pool = content.creatures_for(tier)
            if pool:
                roll = rng.randrange(100)
                encounters = 0 if roll < 55 else (1 if roll < 90 else 2)
                for _ in range(encounters):
                    t = rng.choice(pool)
                    group_size = rng.randrange(t.pack_size.start, t.pack_size.stop) if t.pack_size[-1] > 1 else 1
                    for _ in range(group_size):
                        beings.append(SpawnEntry(t.name, SpawnKind.CREATURE, t.disposition, sg.creature_stats(tier, rng)))
            if rng.randrange(100) < 5:
                npc_pool = content.npcs_for(tier)
                if npc_pool:
                    t = rng.choice(npc_pool)
                    beings.append(SpawnEntry(t.name, SpawnKind.NPC, t.disposition, sg.creature_stats(tier, rng)))
            subclass = subclass_giver_at.get((x, y))
            if subclass is not None:
                name = "Countess Mireille, the Pale Widow" if subclass == Subclass.VAMPIRE else "Kael Thornfang, the Lone Howler"
                beings.append(SpawnEntry(name, SpawnKind.NPC, Disposition.PASSIVE, sg.creature_stats(5, rng), offers_subclass=subclass))
        else:
            npc_pool = [t for t in content.npcs_for(tier) if t.disposition == Disposition.PASSIVE]
            count = rng.randint(4, 6) if population_tier == PopulationTier.CITY else rng.randint(2, 4)
            shuffled_pool = list(npc_pool)
            rng.shuffle(shuffled_pool)
            chosen_npcs = shuffled_pool[:count]
            companion_pick = (rng.choice(chosen_npcs) if chosen_npcs else None) if population_tier == PopulationTier.CITY else None
            quests_here = side_quest_at.get((x, y), []) if population_tier == PopulationTier.CITY else []
            quest_candidates = [n for n in chosen_npcs if n != companion_pick]
            rng.shuffle(quest_candidates)
            quest_assignment = dict(zip(quest_candidates, quests_here))
            for t in chosen_npcs:
                beings.append(SpawnEntry(
                    t.name, SpawnKind.NPC, t.disposition, sg.creature_stats(tier, rng),
                    offers_companionship=(t == companion_pick),
                    offers_side_quest=quest_assignment.get(t),
                ))
            if rng.randrange(100) < 8:
                hostile_pool = [t for t in content.npcs_for(tier) if t.disposition == Disposition.HOSTILE]
                if hostile_pool:
                    t = rng.choice(hostile_pool)
                    beings.append(SpawnEntry(t.name, SpawnKind.NPC, t.disposition, sg.creature_stats(tier, rng)))
            trainer = trainer_at.get((x, y))
            if trainer is not None:
                beings.append(SpawnEntry(trainer.name, SpawnKind.NPC, Disposition.PASSIVE, sg.creature_stats(tier, rng), teaches_skill=trainer.skill))
            relation = family_member_at.get((x, y))
            if relation is not None:
                beings.append(SpawnEntry(
                    f"{relation.name}, your long-lost {relation.relation}", SpawnKind.NPC, Disposition.PASSIVE,
                    sg.creature_stats(tier, rng), is_family_member=True,
                ))
            if mad_scientist_at == (x, y):
                beings.append(SpawnEntry(
                    "Barnaby \"Bolt\" Higgins, the Homeless Tinkerer", SpawnKind.NPC, Disposition.PASSIVE,
                    sg.creature_stats(1, rng), offers_bionic_upgrade=True,
                ))
        return beings

    def hazard_for(biome: Biome, x: int, y: int, terrain: TerrainKind, population_tier: PopulationTier) -> HazardKind | None:
        if population_tier != PopulationTier.WILDERNESS:
            return None
        eligible = terrain == TerrainKind.WATERWAY if biome == Biome.SEA else terrain == TerrainKind.LAND
        if not eligible:
            return None
        rng = _cell_random(config.seed, x, y, salt=8888)
        if rng.randrange(1000) >= 25:  # ~2.5% of eligible tiles
            return None
        return rng.choice(HazardKind.for_biome(biome))

    locations: dict[str, GameLocation] = {}
    for y in range(config.height):
        for x in range(config.width):
            info = grid[y][x]
            terrain = terrain_grid[y][x]
            settlement = settlement_at.get((x, y))
            portal = portal_at.get((x, y))
            population_tier = settlement.tier if settlement is not None else PopulationTier.WILDERNESS
            is_land_river = info.biome != Biome.SEA and terrain != TerrainKind.LAND
            hazard = hazard_for(info.biome, x, y, terrain, population_tier)

            if settlement is not None:
                name = settlement.name
            elif portal is not None:
                name = portal.name
            elif is_land_river:
                name = river_name(info.biome, terrain)
            else:
                name = wilderness_name(info.biome, x, y)

            treasure = treasure_at.get((x, y))
            artifact = artifact_at.get((x, y))
            if settlement is not None:
                description = settlement_description(info.biome, name, population_tier)
                if mad_scientist_at == (x, y):
                    description += " Word has it this is the most advanced city in the whole Kingdom."
            elif portal is not None:
                description = portal.description
            elif is_land_river:
                description = river_description(info.biome, terrain)
            else:
                description = wilderness_description(info.biome, name, info.tier)
                if treasure is not None:
                    description += " Something glints beneath the waves here."
                if artifact is not None:
                    description += " Something utterly out of place lies half-buried here, catching the light strangely."
                if hazard is not None:
                    description += f" {hazard.encounter_line}"

            exits: dict[str, str] = {}
            if y > 0:
                exits["north"] = f"{x}_{y - 1}"
            if y < config.height - 1:
                exits["south"] = f"{x}_{y + 1}"
            if x < config.width - 1:
                exits["east"] = f"{x + 1}_{y}"
            if x > 0:
                exits["west"] = f"{x - 1}_{y}"

            if portal is not None and settlement is None:
                beings: list[SpawnEntry] = []
            elif is_land_river:
                beings = []
            else:
                beings = pick_beings(info.biome, info.tier, population_tier, x, y)

            loc_id = f"{x}_{y}"
            locations[loc_id] = GameLocation(
                id=loc_id,
                x=x,
                y=y,
                biome=info.biome,
                name=name,
                description=description,
                population_tier=population_tier,
                difficulty_tier=info.tier,
                difficulty_score=info.score,
                beings=tuple(beings),
                exits=exits,
                portal_id=portal.sub_realm_id if portal is not None else None,
                portal_kind=portal.kind if portal is not None else None,
                terrain=terrain,
                items=tuple(x for x in (treasure, artifact) if x is not None),
                hazard=hazard,
            )

    # Splice the tested 15-location home region onto whichever tile the game's
    # own start-city selection will land on (same filter/tie-break rule).
    plains_cities = [loc for loc in locations.values() if loc.biome == Biome.PLAINS and loc.population_tier == PopulationTier.CITY]
    if plains_cities:
        home_anchor = min(plains_cities, key=lambda loc: loc.id)
    else:
        home_anchor = next(loc for loc in locations.values() if loc.population_tier == PopulationTier.CITY)
    home_region_content.graft(locations, home_anchor.x, home_anchor.y)

    return World(config.width, config.height, config.seed, locations, all_sub_realms)
