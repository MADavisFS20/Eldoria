"""One tile of the world map, and the beings that occupy it."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from eldoria.models.biome import Biome, Disposition, PopulationTier, SpawnKind
from eldoria.models.hazard import HazardKind
from eldoria.models.item import Item
from eldoria.models.realm import RealmKind
from eldoria.models.side_quest import SideQuestKind
from eldoria.models.skill import SkillType
from eldoria.models.stat_block import StatBlock
from eldoria.models.subclass import Subclass


class TerrainKind(Enum):
    """LAND is normal walkable ground. WATERWAY is impassable on foot. BRIDGE is always crossable."""

    LAND = "LAND"
    WATERWAY = "WATERWAY"
    BRIDGE = "BRIDGE"


@dataclass(frozen=True)
class SpawnEntry:
    """A living being present at a location: a creature or an NPC, hostile or passive."""

    name: str
    kind: SpawnKind
    disposition: Disposition
    stats: StatBlock
    teaches_skill: SkillType | None = None
    is_family_member: bool = False
    offers_subclass: Subclass | None = None
    offers_bionic_upgrade: bool = False
    offers_companionship: bool = False
    offers_side_quest: SideQuestKind | None = None
    is_rescue_captive: bool = False


@dataclass(frozen=True)
class GameLocation:
    """One tile of the world map. Every one of the 10,000+ map cells is a GameLocation."""

    id: str
    x: int
    y: int
    biome: Biome
    name: str
    description: str
    population_tier: PopulationTier
    difficulty_tier: int
    difficulty_score: int
    beings: tuple[SpawnEntry, ...]
    exits: dict[str, str]
    portal_id: str | None = None
    portal_kind: RealmKind | None = None
    terrain: TerrainKind = TerrainKind.LAND
    items: tuple[Item, ...] = field(default_factory=tuple)
    hazard: HazardKind | None = None

    @property
    def creatures(self) -> list[SpawnEntry]:
        return [b for b in self.beings if b.kind == SpawnKind.CREATURE]

    @property
    def npcs(self) -> list[SpawnEntry]:
        return [b for b in self.beings if b.kind == SpawnKind.NPC]


@dataclass(frozen=True)
class World:
    width: int
    height: int
    seed: int
    locations: dict[str, GameLocation]
    sub_realms: dict[str, "SubRealm"] = field(default_factory=dict)  # noqa: F821

    def location_at(self, x: int, y: int) -> GameLocation | None:
        return self.locations.get(f"{x}_{y}")
