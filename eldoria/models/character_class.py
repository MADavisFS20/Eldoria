"""The seven playable archetypes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from eldoria.models.skill import SkillType


@dataclass(frozen=True)
class StartingGear:
    weapon_name: str
    armor_name: str


class CharacterClass(Enum):
    WARRIOR = (
        "Warrior",
        "A frontline fighter who wins battles through steel, armor, and grit.",
        frozenset({SkillType.ONE_HANDED, SkillType.TWO_HANDED, SkillType.BLOCK, SkillType.HEAVY_ARMOR}),
        None,
        StartingGear("Iron Longsword", "Iron Armor"),
    )
    MAGE = (
        "Mage",
        "A scholar of the arcane, trading steel for spellcraft across every school of magic.",
        frozenset({SkillType.DESTRUCTION, SkillType.ALTERATION, SkillType.RESTORATION, SkillType.CONJURATION, SkillType.ILLUSION}),
        SkillType.DESTRUCTION,
        StartingGear("Apprentice's Staff", "Padded Robes"),
    )
    ROGUE = (
        "Rogue",
        "A quick-fingered opportunist who prefers a hidden blade to an honest fight.",
        frozenset({SkillType.ONE_HANDED, SkillType.SNEAK, SkillType.LOCKPICKING, SkillType.PICKPOCKETING, SkillType.LIGHT_ARMOR, SkillType.SPEECH}),
        None,
        StartingGear("Steel Dagger", "Leather Jerkin"),
    )
    RANGER = (
        "Ranger",
        "A wilderness hunter, equally at home tracking prey and putting an arrow through it.",
        frozenset({SkillType.ARCHERY, SkillType.LIGHT_ARMOR, SkillType.SNEAK, SkillType.UNARMED}),
        None,
        StartingGear("Hunting Bow", "Leather Jerkin"),
    )
    CLERIC = (
        "Cleric",
        "A devoted healer who channels faith into restorative and protective magic.",
        frozenset({SkillType.RESTORATION, SkillType.BLOCK, SkillType.LIGHT_ARMOR, SkillType.SPEECH}),
        SkillType.RESTORATION,
        StartingGear("Mace of the Faithful", "Padded Robes"),
    )
    PALADIN = (
        "Paladin",
        "A holy warrior blending swordsmanship with the power to mend and protect.",
        frozenset({SkillType.ONE_HANDED, SkillType.HEAVY_ARMOR, SkillType.BLOCK, SkillType.RESTORATION}),
        SkillType.RESTORATION,
        StartingGear("Blessed Longsword", "Chainmail Armor"),
    )
    NECROMANCER = (
        "Necromancer",
        "A dark practitioner who trades in life drain, venomous curses, and forbidden rites.",
        frozenset({SkillType.CONJURATION, SkillType.DESTRUCTION, SkillType.ALTERATION}),
        SkillType.CONJURATION,
        StartingGear("Bone-Inlaid Staff", "Tattered Death Shroud"),
    )

    def __init__(
        self,
        display_name: str,
        description: str,
        primary_skills: frozenset[SkillType],
        free_signature_skill: SkillType | None,
        starting_gear: StartingGear,
    ):
        self.display_name = display_name
        self.description = description
        self.primary_skills = primary_skills
        self.free_signature_skill = free_signature_skill
        self.starting_gear = starting_gear
