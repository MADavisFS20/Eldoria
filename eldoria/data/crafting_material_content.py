"""Where the raw materials for each crafting skill come from.

Every crafting SkillType has at least two biome sources so a player isn't
stuck if they've only explored one part of the world. Dropped by defeating
hostile creatures (see commands.py combat) -- not sold in shops, on purpose,
so gathering stays tied to actually adventuring.
"""
from __future__ import annotations

from dataclasses import dataclass

from eldoria.models import Biome, SkillType


@dataclass(frozen=True)
class MaterialTemplate:
    name: str
    feeds_skill: SkillType


_BY_BIOME: dict[Biome, list[MaterialTemplate]] = {
    Biome.MOUNTAINS: [
        MaterialTemplate("Iron Ore", SkillType.BLACKSMITHING),
        MaterialTemplate("Raw Gemstone", SkillType.ENCHANTING),
    ],
    Biome.PLAINS: [
        MaterialTemplate("Medicinal Herbs", SkillType.ALCHEMY),
        MaterialTemplate("Prime Hide", SkillType.LEATHERWORKING),
    ],
    Biome.DESERT: [
        MaterialTemplate("Sun-cured Hide", SkillType.LEATHERWORKING),
        MaterialTemplate("Glass Sand", SkillType.ENCHANTING),
    ],
    Biome.JUNGLE: [
        MaterialTemplate("Rare Jungle Herbs", SkillType.ALCHEMY),
        MaterialTemplate("Straight-Grain Wood", SkillType.WOODWORKING),
    ],
    Biome.TUNDRA: [
        MaterialTemplate("Frost Ore", SkillType.BLACKSMITHING),
        MaterialTemplate("Thick Pelt", SkillType.LEATHERWORKING),
    ],
    Biome.SEA: [
        MaterialTemplate("Kelp Extract", SkillType.ALCHEMY),
        MaterialTemplate("Driftwood", SkillType.WOODWORKING),
    ],
}


def materials_for(biome: Biome) -> list[MaterialTemplate]:
    return _BY_BIOME[biome]


def all_materials() -> list[MaterialTemplate]:
    return [m for group in _BY_BIOME.values() for m in group]
