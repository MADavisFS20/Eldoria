"""A dungeon or sky realm: a graph of rooms reachable through an overworld portal tile."""
from __future__ import annotations

from dataclasses import dataclass, field

from eldoria.models.biome import Biome
from eldoria.models.game_location import SpawnEntry
from eldoria.models.item import Item
from eldoria.models.realm import QuestType, RealmKind

__all__ = ["RealmKind", "QuestType", "SubRealmRoom", "SubRealmQuest", "SubRealm"]


@dataclass(frozen=True)
class SubRealmRoom:
    """One room/chamber (dungeon) or island/terrace (sky realm) inside a SubRealm."""

    id: str
    name: str
    description: str
    difficulty_tier: int
    is_boss_room: bool
    beings: tuple[SpawnEntry, ...]
    items: tuple[Item, ...]
    exits: dict[str, str]


@dataclass(frozen=True)
class SubRealmQuest:
    title: str
    type: QuestType
    objective: str
    quest_item: Item
    legendary_item: Item


@dataclass(frozen=True)
class SubRealm:
    id: str
    kind: RealmKind
    name: str
    biome: Biome
    entrance_location_id: str
    entry_room_id: str
    boss_room_id: str
    rooms: dict[str, SubRealmRoom]
    quest: SubRealmQuest
