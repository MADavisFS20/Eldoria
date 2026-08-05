"""Shared template dataclasses used across the content registries."""
from __future__ import annotations

from dataclasses import dataclass, field

from eldoria.models import Biome, Disposition


@dataclass(frozen=True)
class CreatureTemplate:
    """A kind of creature that can spawn in a biome within a tier range (1..5, easy..hard)."""

    name: str
    disposition: Disposition
    min_tier: int
    max_tier: int
    pack_size: range = field(default_factory=lambda: range(1, 2))


@dataclass(frozen=True)
class NpcTemplate:
    """A kind of NPC (civilian or otherwise) that can appear in a biome within a tier range."""

    name: str
    disposition: Disposition
    min_tier: int
    max_tier: int


@dataclass(frozen=True)
class BiomeContent:
    """All the hardcoded flavor content for one biome: names, terrain words, and populations."""

    biome: Biome
    adjectives: tuple[str, ...]
    features: tuple[str, ...]
    qualifiers: tuple[str, ...]
    city_names: tuple[str, ...]
    village_names: tuple[str, ...]
    creatures: tuple[CreatureTemplate, ...]
    npcs: tuple[NpcTemplate, ...]

    def creatures_for(self, tier: int) -> list[CreatureTemplate]:
        return [c for c in self.creatures if c.min_tier <= tier <= c.max_tier]

    def npcs_for(self, tier: int) -> list[NpcTemplate]:
        return [n for n in self.npcs if n.min_tier <= tier <= n.max_tier]
