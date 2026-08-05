"""Builds one dungeon or sky realm as a graph of rooms.

A branching tunnel tree plus a few extra loop connections, with difficulty
rising from the entry room out to a single boss room that holds the unique
legendary item and quest item for that realm.
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

from eldoria.data.sub_realm_theme import SubRealmTheme
from eldoria.models import (
    Biome,
    Disposition,
    Item,
    QuestType,
    RealmKind,
    SpawnEntry,
    SpawnKind,
    SubRealm,
    SubRealmQuest,
    SubRealmRoom,
)
from eldoria.world import stat_generator as sg
from eldoria.world.deterministic_random import make_random, seed as mix_seed, string_hash

_OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
_DIRECTIONS = ["north", "south", "east", "west", "up", "down"]


def _pick_unique(pool: list, used: set, rng: random.Random):
    shuffled = list(pool)
    rng.shuffle(shuffled)
    choice = next((x for x in shuffled if x not in used), shuffled[0])
    used.add(choice)
    return choice


@dataclass
class _RoomGraph:
    adjacency: list[set[int]]
    depth: list[int]
    tier: list[int]
    boss_index: int


def _build_room_graph(rng: random.Random, room_count: int) -> _RoomGraph:
    parent = [-1] * room_count
    depth = [0] * room_count
    child_count = [0] * room_count
    max_children = 3
    frontier: deque[int] = deque()
    frontier.append(0)

    for i in range(1, room_count):
        p = rng.choice(list(frontier))
        attempts = 0
        while child_count[p] >= max_children and attempts < 10:
            p = rng.choice(list(frontier))
            attempts += 1
        if child_count[p] >= max_children:
            p = next((j for j in range(i) if child_count[j] < max_children), i - 1)
        parent[i] = p
        depth[i] = depth[p] + 1
        child_count[p] += 1
        frontier.append(i)
        if len(frontier) > 5:
            frontier.popleft()

    adjacency: list[set[int]] = [set() for _ in range(room_count)]
    for i in range(1, room_count):
        adjacency[i].add(parent[i])
        adjacency[parent[i]].add(i)

    extra_edges = max(0, room_count // 6)
    added = 0
    guard = 0
    while added < extra_edges and guard < extra_edges * 25 + 20:
        guard += 1
        a = rng.randrange(room_count)
        b = rng.randrange(room_count)
        if a == b:
            continue
        if len(adjacency[a]) >= 5 or len(adjacency[b]) >= 5:
            continue
        if abs(depth[a] - depth[b]) > 1:
            continue
        if b in adjacency[a]:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
        added += 1

    max_depth = max(1, max(depth) if depth else 1)
    tier = [max(1, min(5, int(1 + (depth[i] * 4.0 / max_depth)))) for i in range(room_count)]
    at_max_depth = [i for i in range(room_count) if depth[i] == max_depth]
    boss_index = max(at_max_depth) if at_max_depth else room_count - 1
    return _RoomGraph(adjacency, depth, tier, boss_index)


def _assign_exits(rng: random.Random, graph: _RoomGraph, room_count: int) -> list[dict[str, int]]:
    used: list[set[str]] = [set() for _ in range(room_count)]
    exits: list[dict[str, int]] = [dict() for _ in range(room_count)]
    seen_edges: set[tuple[int, int]] = set()

    for a in range(room_count):
        for b in graph.adjacency[a]:
            key = (min(a, b), max(a, b))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            candidates = list(_DIRECTIONS)
            rng.shuffle(candidates)
            connected = False
            for d in candidates:
                od = _OPPOSITE[d]
                if d not in used[a] and od not in used[b]:
                    used[a].add(d)
                    used[b].add(od)
                    exits[a][d] = b
                    exits[b][od] = a
                    connected = True
                    break
            if not connected:
                exits[a][f"passage_to_{b}"] = b
                exits[b][f"passage_to_{a}"] = a
    return exits


def generate(
    kind: RealmKind,
    biome: Biome,
    theme: SubRealmTheme,
    entrance_location_id: str,
    world_seed: int,
    room_count_range: range,
    used_realm_names: set[str],
    used_boss_names: set[str],
    used_legendary_names: set[str],
    used_quest_item_names: set[str],
) -> SubRealm:
    kind_ordinal = list(RealmKind).index(kind)
    realm_seed = mix_seed(world_seed, string_hash(entrance_location_id), kind_ordinal)
    rng = random.Random(realm_seed)

    base_realm_name = _pick_unique(theme.realm_names, set(), rng)
    realm_name = f"{base_realm_name} above the {biome.display_name}" if base_realm_name in used_realm_names else base_realm_name
    used_realm_names.add(realm_name)

    boss_creature_name = _pick_unique(theme.boss_creatures, used_boss_names, rng)

    weapon_or_armor_is_weapon = rng.choice([True, False])
    base = rng.choice(theme.weapon_bases) if weapon_or_armor_is_weapon else rng.choice(theme.armor_bases)
    legendary_name = f"{rng.choice(theme.item_prefixes)} {base}"
    guard = 0
    while legendary_name in used_legendary_names and guard < 20:
        legendary_name = f"{rng.choice(theme.item_prefixes)} {base}"
        guard += 1
    used_legendary_names.add(legendary_name)

    quest_item_name = _pick_unique(theme.quest_item_names, used_quest_item_names, rng)

    quest_type = rng.choice(list(QuestType))
    captive_name = rng.choice(theme.captive_names)

    room_count = rng.randrange(room_count_range.start, room_count_range.stop)
    graph = _build_room_graph(rng, room_count)
    exits = _assign_exits(rng, graph, room_count)
    boss_tier = graph.tier[graph.boss_index]

    if weapon_or_armor_is_weapon:
        legendary_item = sg.weapon_item(legendary_name, boss_tier, rng, legendary=True)
    else:
        legendary_item = sg.armor_item(legendary_name, boss_tier, rng, legendary=True)
    quest_item = sg.quest_item(quest_item_name, boss_tier, rng)

    realm_id_base = f"{kind.name.lower()}_{entrance_location_id}"

    rooms: dict[str, SubRealmRoom] = {}
    for i in range(room_count):
        room_rng = random.Random(mix_seed(realm_seed, i))
        is_boss = i == graph.boss_index
        adjective = room_rng.choice(theme.room_adjectives)
        feature = room_rng.choice(theme.room_features)
        name = f"{adjective} {feature} ({theme.label} Sanctum)" if is_boss else f"{adjective} {feature}"

        beings: list[SpawnEntry] = []
        items: list[Item] = []

        if is_boss:
            beings.append(SpawnEntry(boss_creature_name, SpawnKind.CREATURE, Disposition.HOSTILE, sg.creature_stats(graph.tier[i], room_rng)))
            items.append(legendary_item)
            items.append(quest_item)
            if quest_type == QuestType.RESCUE_CAPTIVE:
                beings.append(SpawnEntry(captive_name, SpawnKind.NPC, Disposition.PASSIVE, sg.creature_stats(1, room_rng), is_rescue_captive=True))
        else:
            pool = theme.creatures_for(graph.tier[i])
            if pool and room_rng.randrange(100) < 70:
                t = room_rng.choice(pool)
                pack_size = t.pack_size
                group_size = room_rng.randrange(pack_size.start, pack_size.stop) if pack_size[-1] > 1 else 1
                for _ in range(group_size):
                    beings.append(SpawnEntry(t.name, SpawnKind.CREATURE, t.disposition, sg.creature_stats(graph.tier[i], room_rng)))

        if is_boss:
            description = (
                f"You enter the heart of {theme.label}: the {name}. {boss_creature_name} lurks here, "
                f"guarding the {room_rng.choice(theme.item_prefixes).lower()} treasures of this place."
            )
        else:
            description = f"A {adjective.lower()} {feature}, deep within {realm_name}."

        room_id = f"{realm_id_base}_room{i}"
        rooms[room_id] = SubRealmRoom(
            id=room_id,
            name=name,
            description=description,
            difficulty_tier=graph.tier[i],
            is_boss_room=is_boss,
            beings=tuple(beings),
            items=tuple(items),
            exits={direction: f"{realm_id_base}_room{room_index}" for direction, room_index in exits[i].items()},
        )

    if quest_type == QuestType.RETRIEVE_ARTIFACT:
        objective = f"Deep within {realm_name} lies the {quest_item_name}. Recover it before it is lost to the dark forever."
    elif quest_type == QuestType.DEFEAT_GUARDIAN:
        objective = f"{boss_creature_name} has claimed {realm_name} as its lair. Slay it to reclaim these depths."
    else:
        objective = f"{captive_name} has been trapped within {realm_name}, guarded by {boss_creature_name}. Brave the depths and bring them home."

    quest = SubRealmQuest(
        title=realm_name,
        type=quest_type,
        objective=objective,
        quest_item=quest_item,
        legendary_item=legendary_item,
    )

    return SubRealm(
        id=realm_id_base,
        kind=kind,
        name=realm_name,
        biome=biome,
        entrance_location_id=entrance_location_id,
        entry_room_id=f"{realm_id_base}_room0",
        boss_room_id=f"{realm_id_base}_room{graph.boss_index}",
        rooms=rooms,
        quest=quest,
    )
