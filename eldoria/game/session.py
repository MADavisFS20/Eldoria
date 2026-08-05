"""All the mutable runtime state a play session needs on top of the immutable generated World.

Where the player is, what they've discovered (for the fog-of-war map and
bestiary), what's been defeated/looted, and quest tracking. The World and
PlayerCharacter models stay immutable/generation-pure; this class is the one
place session state is allowed to live.

Respawn rule: a defeated being does NOT come back just because time passes
while you're standing there -- it only becomes eligible again once you've
*left* its spot and RESPAWN_DELAY_TICKS have passed since that departure.
"Spot" for the overworld is the single tile; for a dungeon/sky realm it's the
whole sub-realm.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from eldoria.game import serialization
from eldoria.models import GameLocation, Item, PlayerCharacter, SpawnEntry, SubRealm, SubRealmRoom, World

RESPAWN_DELAY_TICKS = 40


@dataclass(frozen=True)
class SubRealmPosition:
    sub_realm_id: str
    room_id: str


@dataclass
class Snapshot:
    """A flattened, disk-safe copy of every field save/load needs.

    Deliberately does NOT include the World itself (11,700+ generated
    locations) -- it's fully reproducible from `seed`.
    """

    seed: int
    player: PlayerCharacter
    location_id: str
    home_location_id: str
    sub_realm_id: str | None
    sub_realm_room_id: str | None
    game_tick: int
    discovered_locations: set[str]
    defeated_at: dict[str, dict[int, int]]
    departed_at: dict[str, int]
    taken_items: dict[str, set[int]]
    discovered_quests: set[str]
    completed_quests: set[str]
    bestiary: set[str]
    final_battle_unlocked: bool
    final_battle_won: bool
    completed_side_quests: set[str]
    quest_counters: dict[str, int] = field(default_factory=dict)
    active_home_region_quests: set[str] = field(default_factory=set)
    chronicle_discovered: set[str] = field(default_factory=set)
    met_time_traveler: bool = False
    move_count: int = 0

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "player": serialization.player_to_dict(self.player),
            "location_id": self.location_id,
            "home_location_id": self.home_location_id,
            "sub_realm_id": self.sub_realm_id,
            "sub_realm_room_id": self.sub_realm_room_id,
            "game_tick": self.game_tick,
            "discovered_locations": sorted(self.discovered_locations),
            "defeated_at": {k: {str(i): t for i, t in v.items()} for k, v in self.defeated_at.items()},
            "departed_at": dict(self.departed_at),
            "taken_items": {k: sorted(v) for k, v in self.taken_items.items()},
            "discovered_quests": sorted(self.discovered_quests),
            "completed_quests": sorted(self.completed_quests),
            "bestiary": sorted(self.bestiary),
            "final_battle_unlocked": self.final_battle_unlocked,
            "final_battle_won": self.final_battle_won,
            "completed_side_quests": sorted(self.completed_side_quests),
            "quest_counters": dict(self.quest_counters),
            "active_home_region_quests": sorted(self.active_home_region_quests),
            "chronicle_discovered": sorted(self.chronicle_discovered),
            "met_time_traveler": self.met_time_traveler,
            "move_count": self.move_count,
        }

    @staticmethod
    def from_dict(d: dict) -> "Snapshot":
        return Snapshot(
            seed=d["seed"],
            player=serialization.player_from_dict(d["player"]),
            location_id=d["location_id"],
            home_location_id=d["home_location_id"],
            sub_realm_id=d.get("sub_realm_id"),
            sub_realm_room_id=d.get("sub_realm_room_id"),
            game_tick=d["game_tick"],
            discovered_locations=set(d.get("discovered_locations", [])),
            defeated_at={k: {int(i): t for i, t in v.items()} for k, v in d.get("defeated_at", {}).items()},
            departed_at=dict(d.get("departed_at", {})),
            taken_items={k: set(v) for k, v in d.get("taken_items", {}).items()},
            discovered_quests=set(d.get("discovered_quests", [])),
            completed_quests=set(d.get("completed_quests", [])),
            bestiary=set(d.get("bestiary", [])),
            final_battle_unlocked=d.get("final_battle_unlocked", False),
            final_battle_won=d.get("final_battle_won", False),
            completed_side_quests=set(d.get("completed_side_quests", [])),
            quest_counters=dict(d.get("quest_counters", {})),
            active_home_region_quests=set(d.get("active_home_region_quests", [])),
            chronicle_discovered=set(d.get("chronicle_discovered", [])),
            met_time_traveler=d.get("met_time_traveler", False),
            move_count=d.get("move_count", 0),
        )


class GameSession:
    def __init__(self, world: World, player: PlayerCharacter, location_id: str, home_location_id: str, rng: random.Random):
        self.world = world
        self.player = player
        self.location_id = location_id
        self.home_location_id = home_location_id
        self.rng = rng

        self.game_tick: int = 0
        self.discovered_locations: set[str] = {location_id}
        self.sub_realm_position: SubRealmPosition | None = None

        self._defeated_at: dict[str, dict[int, int]] = {}
        self._departed_at: dict[str, int] = {}
        self._taken_items: dict[str, set[int]] = {}

        self.discovered_quests: set[str] = set()
        self.completed_quests: set[str] = set()
        self.bestiary: set[str] = set()
        self.chronicle_discovered: set[str] = set()
        self.met_time_traveler: bool = False
        self.move_count: int = 0

        self.completed_side_quests: set[str] = set()
        self.active_home_region_quests: set[str] = set()
        self.quest_counters: dict[str, int] = {}

        self.final_battle_unlocked = False
        self.final_battle_won = False
        self.ferryman_available = False
        self.balloon_man_available = False

        # Web-adaptation state (loop-local vars in the original console engine):
        # shop stock needs to survive across separate HTTP requests, and a
        # blocking yes/no quest-accept prompt becomes an explicit pending
        # choice resolved by a follow-up 'accept'/'decline' command.
        self.last_shop_trader: str | None = None
        self.last_shop_stock: list[Item] = []
        self.pending_prompt: dict | None = None

    @property
    def current_location(self) -> GameLocation:
        return self.world.locations[self.location_id]

    @property
    def in_sub_realm(self) -> bool:
        return self.sub_realm_position is not None

    def current_sub_realm(self) -> SubRealm | None:
        if self.sub_realm_position is None:
            return None
        return self.world.sub_realms.get(self.sub_realm_position.sub_realm_id)

    def current_room(self) -> SubRealmRoom | None:
        if self.sub_realm_position is None:
            return None
        realm = self.world.sub_realms.get(self.sub_realm_position.sub_realm_id)
        return realm.rooms.get(self.sub_realm_position.room_id) if realm else None

    def _spot_key(self) -> str:
        room = self.current_room()
        return room.id if room else self.location_id

    def advance_tick(self) -> None:
        self.game_tick += 1

    def record_overworld_departure(self, old_location_id: str) -> None:
        """Call right before changing location_id on the overworld (each spot's own respawn clock)."""
        self._departed_at[old_location_id] = self.game_tick

    def record_sub_realm_departure(self, sub_realm: SubRealm) -> None:
        """Call when fully exiting a sub-realm back to the overworld -- resets the clock for every room in it at once."""
        for room_id in sub_realm.rooms:
            self._departed_at[room_id] = self.game_tick

    def _is_respawn_eligible(self, spot: str, being_index: int) -> bool:
        death_tick = self._defeated_at.get(spot, {}).get(being_index)
        if death_tick is None:
            return True
        departed = self._departed_at.get(spot)
        if departed is None:
            return False
        return departed > death_tick and self.game_tick - departed >= RESPAWN_DELAY_TICKS

    def current_beings(self) -> list[tuple[int, SpawnEntry]]:
        """Living beings at the current spot, indexed exactly like the static list."""
        all_beings = self.current_room().beings if self.current_room() else self.current_location.beings
        spot = self._spot_key()
        return [(i, b) for i, b in enumerate(all_beings) if self._is_respawn_eligible(spot, i)]

    def current_items(self) -> list[tuple[int, Item]]:
        """Un-taken ground items at the current spot, indexed exactly like the static list."""
        items_here = self.current_room().items if self.current_room() else self.current_location.items
        gone = self._taken_items.get(self._spot_key(), set())
        return [(i, item) for i, item in enumerate(items_here) if i not in gone]

    def mark_defeated(self, being_index: int, being_name: str) -> None:
        self._defeated_at.setdefault(self._spot_key(), {})[being_index] = self.game_tick
        self.bestiary.add(being_name)

    def record_seen(self, being_name: str) -> None:
        self.bestiary.add(being_name)

    def mark_taken(self, item_index: int) -> None:
        self._taken_items.setdefault(self._spot_key(), set()).add(item_index)

    def discover(self, location_id: str) -> None:
        self.discovered_locations.add(location_id)

    def increment_quest_counter(self, key: str) -> None:
        self.quest_counters[key] = self.quest_counters.get(key, 0) + 1

    def snapshot(self) -> Snapshot:
        return Snapshot(
            seed=self.world.seed,
            player=self.player,
            location_id=self.location_id,
            home_location_id=self.home_location_id,
            sub_realm_id=self.sub_realm_position.sub_realm_id if self.sub_realm_position else None,
            sub_realm_room_id=self.sub_realm_position.room_id if self.sub_realm_position else None,
            game_tick=self.game_tick,
            discovered_locations=set(self.discovered_locations),
            defeated_at={k: dict(v) for k, v in self._defeated_at.items()},
            departed_at=dict(self._departed_at),
            taken_items={k: set(v) for k, v in self._taken_items.items()},
            discovered_quests=set(self.discovered_quests),
            completed_quests=set(self.completed_quests),
            bestiary=set(self.bestiary),
            final_battle_unlocked=self.final_battle_unlocked,
            final_battle_won=self.final_battle_won,
            completed_side_quests=set(self.completed_side_quests),
            quest_counters=dict(self.quest_counters),
            active_home_region_quests=set(self.active_home_region_quests),
            chronicle_discovered=set(self.chronicle_discovered),
            met_time_traveler=self.met_time_traveler,
            move_count=self.move_count,
        )

    def restore_from(self, snap: Snapshot) -> None:
        """Restores every field in place from a snapshot taken against this same World (seed must match)."""
        if snap.seed != self.world.seed:
            raise ValueError("Save is for a different world seed")
        self.player = snap.player
        self.location_id = snap.location_id
        if snap.sub_realm_id is not None and snap.sub_realm_room_id is not None:
            self.sub_realm_position = SubRealmPosition(snap.sub_realm_id, snap.sub_realm_room_id)
        else:
            self.sub_realm_position = None
        self.game_tick = snap.game_tick
        self.discovered_locations = set(snap.discovered_locations)
        self._defeated_at = {k: dict(v) for k, v in snap.defeated_at.items()}
        self._departed_at = dict(snap.departed_at)
        self._taken_items = {k: set(v) for k, v in snap.taken_items.items()}
        self.discovered_quests = set(snap.discovered_quests)
        self.completed_quests = set(snap.completed_quests)
        self.bestiary = set(snap.bestiary)
        self.final_battle_unlocked = snap.final_battle_unlocked
        self.final_battle_won = snap.final_battle_won
        self.completed_side_quests = set(snap.completed_side_quests)
        self.quest_counters = dict(snap.quest_counters)
        self.active_home_region_quests = set(snap.active_home_region_quests)
        self.chronicle_discovered = set(snap.chronicle_discovered)
        self.met_time_traveler = snap.met_time_traveler
        self.move_count = snap.move_count
