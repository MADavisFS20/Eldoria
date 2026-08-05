"""Eldoria data models -- ported from core/model/*.kt. Immutable dataclasses/enums throughout."""
from eldoria.models.artifact import ArtifactKind
from eldoria.models.biome import Biome, Disposition, PopulationTier, SpawnKind
from eldoria.models.business import Business
from eldoria.models.character_class import CharacterClass, StartingGear
from eldoria.models.companion import EMPLOYMENT_DURATION_MILLIS, HiredCompanion
from eldoria.models.dice import DiceFormula, DieType
from eldoria.models.game_location import GameLocation, SpawnEntry, TerrainKind, World
from eldoria.models.hazard import HazardKind
from eldoria.models.item import Item, ItemKind
from eldoria.models.perk import Perk
from eldoria.models.player_character import PlayerCharacter
from eldoria.models.property import RentalProperty
from eldoria.models.race import AbilityModifiers, Race
from eldoria.models.realm import QuestType, RealmKind
from eldoria.models.side_quest import SideQuestKind, SideQuestResolution
from eldoria.models.skill import Skill, SkillCategory, SkillType
from eldoria.models.stat_block import MagicEffect, StatBlock
from eldoria.models.status_effect import StatusEffect
from eldoria.models.sub_realm import SubRealm, SubRealmQuest, SubRealmRoom
from eldoria.models.subclass import Subclass

__all__ = [
    "ArtifactKind",
    "Biome", "Disposition", "PopulationTier", "SpawnKind",
    "Business",
    "CharacterClass", "StartingGear",
    "EMPLOYMENT_DURATION_MILLIS", "HiredCompanion",
    "DiceFormula", "DieType",
    "GameLocation", "SpawnEntry", "TerrainKind", "World",
    "HazardKind",
    "Item", "ItemKind",
    "Perk",
    "PlayerCharacter",
    "RentalProperty",
    "AbilityModifiers", "Race",
    "QuestType", "RealmKind",
    "SideQuestKind", "SideQuestResolution",
    "Skill", "SkillCategory", "SkillType",
    "MagicEffect", "StatBlock",
    "StatusEffect",
    "SubRealm", "SubRealmQuest", "SubRealmRoom",
    "Subclass",
]
