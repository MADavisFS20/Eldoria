"""The six main environments the world map is divided into.

Order here also defines their left-to-right band order in the generated map.
"""
from __future__ import annotations

from enum import Enum


class Biome(Enum):
    MOUNTAINS = "Mountains"
    PLAINS = "Plains"
    DESERT = "Desert"
    JUNGLE = "Jungle"
    TUNDRA = "Tundra"
    SEA = "Sea"

    @property
    def display_name(self) -> str:
        return self.value


class PopulationTier(Enum):
    WILDERNESS = "WILDERNESS"
    COUNTRYSIDE = "COUNTRYSIDE"
    CITY = "CITY"


class Disposition(Enum):
    HOSTILE = "HOSTILE"
    PASSIVE = "PASSIVE"


class SpawnKind(Enum):
    CREATURE = "CREATURE"
    NPC = "NPC"
