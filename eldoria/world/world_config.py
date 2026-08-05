"""width * height must be >= 10,000. Default 130x90 = 11,700 map tiles, 6 vertical biome bands."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorldConfig:
    width: int = 130
    height: int = 90
    seed: int = 1337
    cities_per_biome: int = 2
    villages_per_city: int = 4
    dungeons_per_biome: int = 3
    dungeon_room_count_range: range = range(12, 21)
    beanstalks_per_biome: int = 2
    sky_room_count_range: range = range(10, 19)
    river_count: int = 3
    bridge_spacing: int = 10

    def __post_init__(self):
        assert self.width * self.height >= 10_000
