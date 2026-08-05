"""Every skill a character can practice."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SkillCategory(Enum):
    COMBAT = "COMBAT"
    MAGIC = "MAGIC"
    STEALTH = "STEALTH"
    CRAFTING = "CRAFTING"


class SkillType(Enum):
    # Combat -- known from level 1.
    ONE_HANDED = ("One-Handed Weapons", SkillCategory.COMBAT, False)
    TWO_HANDED = ("Two-Handed Weapons", SkillCategory.COMBAT, False)
    ARCHERY = ("Archery", SkillCategory.COMBAT, False)
    BLOCK = ("Block", SkillCategory.COMBAT, False)
    HEAVY_ARMOR = ("Heavy Armor", SkillCategory.COMBAT, False)
    LIGHT_ARMOR = ("Light Armor", SkillCategory.COMBAT, False)
    UNARMED = ("Unarmed Combat", SkillCategory.COMBAT, False)

    # Stealth -- known from level 1.
    SNEAK = ("Sneak", SkillCategory.STEALTH, False)
    LOCKPICKING = ("Lockpicking", SkillCategory.STEALTH, False)
    PICKPOCKETING = ("Pickpocketing", SkillCategory.STEALTH, False)
    SPEECH = ("Speech", SkillCategory.STEALTH, False)

    # Magic schools -- must be learned from a trainer.
    DESTRUCTION = ("Destruction Magic", SkillCategory.MAGIC, True)
    RESTORATION = ("Restoration Magic", SkillCategory.MAGIC, True)
    ALTERATION = ("Alteration Magic", SkillCategory.MAGIC, True)
    ILLUSION = ("Illusion Magic", SkillCategory.MAGIC, True)
    CONJURATION = ("Conjuration Magic", SkillCategory.MAGIC, True)

    # Crafting -- must be learned from a trainer.
    BLACKSMITHING = ("Blacksmithing", SkillCategory.CRAFTING, True)
    ALCHEMY = ("Alchemy", SkillCategory.CRAFTING, True)
    ENCHANTING = ("Enchanting", SkillCategory.CRAFTING, True)
    WOODWORKING = ("Woodworking", SkillCategory.CRAFTING, True)
    LEATHERWORKING = ("Leatherworking", SkillCategory.CRAFTING, True)

    def __init__(self, display_name: str, category: SkillCategory, trainer_locked: bool):
        self.display_name = display_name
        self.category = category
        self.trainer_locked = trainer_locked

    @classmethod
    def base_skills(cls) -> list["SkillType"]:
        return [s for s in cls if not s.trainer_locked]

    @classmethod
    def trainer_locked_skills(cls) -> list["SkillType"]:
        return [s for s in cls if s.trainer_locked]


@dataclass(frozen=True)
class Skill:
    """One skill's mastery: level 1..100, plus banked xp toward the next level."""

    type: SkillType
    level: int
    xp: int = 0
