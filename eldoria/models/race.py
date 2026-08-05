"""The five playable peoples of Eldoria."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from eldoria.models.skill import SkillType


@dataclass(frozen=True)
class AbilityModifiers:
    strength: int
    agility: int
    willpower: int


class Race(Enum):
    ELF = (
        "Elf",
        "Long-lived and graceful, elves favor the bow and the arcane over brute force.",
        AbilityModifiers(strength=-1, agility=2, willpower=2),
        {
            SkillType.ARCHERY: 10,
            SkillType.SNEAK: 5,
            SkillType.DESTRUCTION: 10,
            SkillType.ILLUSION: 10,
            SkillType.ALTERATION: 5,
        },
        "resistant to poison",
        10,
    )
    HUMAN = (
        "Human",
        "Adaptable and ambitious, humans have no great weakness and a knack for dealing with others.",
        AbilityModifiers(strength=0, agility=0, willpower=1),
        {
            SkillType.SPEECH: 10,
            SkillType.ONE_HANDED: 3,
            SkillType.LIGHT_ARMOR: 3,
            SkillType.BLOCK: 3,
            SkillType.SNEAK: 3,
        },
        "no special resistance, but no particular weakness either",
        0,
    )
    NORD = (
        "Nord",
        "Hardy warriors of the frozen north, raised on cold steel and colder winters.",
        AbilityModifiers(strength=2, agility=0, willpower=-1),
        {
            SkillType.TWO_HANDED: 10,
            SkillType.ONE_HANDED: 5,
            SkillType.BLOCK: 10,
            SkillType.HEAVY_ARMOR: 10,
        },
        "resistant to frost",
        20,
    )
    DWARF = (
        "Dwarf",
        "Stout and stubborn, unmatched at the forge and unshaken behind a shield wall.",
        AbilityModifiers(strength=2, agility=-1, willpower=1),
        {
            SkillType.BLACKSMITHING: 15,
            SkillType.HEAVY_ARMOR: 10,
            SkillType.BLOCK: 5,
            SkillType.ENCHANTING: 5,
        },
        "resistant to poison and disease",
        15,
    )
    ORC = (
        "Orc",
        "Fierce and imposing, orcs are bred for battle and have little patience for magic or manners.",
        AbilityModifiers(strength=3, agility=1, willpower=-2),
        {
            SkillType.TWO_HANDED: 10,
            SkillType.UNARMED: 10,
            SkillType.ONE_HANDED: 5,
            SkillType.HEAVY_ARMOR: 5,
            SkillType.SPEECH: -5,
        },
        "resistant to pain and fear effects",
        10,
    )

    def __init__(
        self,
        display_name: str,
        lore: str,
        ability_modifiers: AbilityModifiers,
        skill_affinities: dict[SkillType, int],
        resistance_lore: str,
        magic_resistance_percent: int,
    ):
        self.display_name = display_name
        self.lore = lore
        self.ability_modifiers = ability_modifiers
        self.skill_affinities = skill_affinities
        self.resistance_lore = resistance_lore
        self.magic_resistance_percent = magic_resistance_percent
