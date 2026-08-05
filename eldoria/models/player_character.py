"""The player's own character sheet.

Immutable like every other model in the engine -- progression always returns
an updated copy (dataclasses.replace), never mutates in place.

Two independent progression tracks:
 - level/experience (1..50) rises from combat/quest XP and grants small
   across-the-board stat growth, health and strength most.
 - skills (each 1..100) rise purely from using that skill and never feed
   back into character level.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from eldoria.models.artifact import ArtifactKind
from eldoria.models.business import Business
from eldoria.models.character_class import CharacterClass
from eldoria.models.companion import HiredCompanion
from eldoria.models.dice import DiceFormula
from eldoria.models.item import Item, ItemKind
from eldoria.models.perk import Perk
from eldoria.models.property import RentalProperty
from eldoria.models.race import Race
from eldoria.models.skill import Skill, SkillType
from eldoria.models.subclass import Subclass


@dataclass(frozen=True)
class PlayerCharacter:
    name: str
    race: Race
    character_class: CharacterClass
    level: int
    experience: int
    strength: int
    agility: int
    willpower: int
    max_health: int
    current_health: int
    max_stamina: int
    current_stamina: int
    armor_class: int
    speed: int
    attack_bonus: int
    unarmed_damage: DiceFormula
    skills: dict[SkillType, Skill]
    gold: int
    inventory: tuple[Item, ...] = field(default_factory=tuple)
    equipped_weapon: Item | None = None
    equipped_armor: Item | None = None
    equipped_offhand: Item | None = None
    equipped_head: Item | None = None
    equipped_ring: Item | None = None
    equipped_amulet: Item | None = None
    owned_boat: Item | None = None
    materials: dict[str, int] = field(default_factory=dict)
    reputation: int = 0
    perks: dict[Perk, int] = field(default_factory=dict)
    pending_perk_choices: int = 0
    second_wind_ready: bool = False
    subclass: Subclass | None = None
    bionic_upgrade_used: bool = False
    artifacts: frozenset[ArtifactKind] = field(default_factory=frozenset)
    companion: HiredCompanion | None = None
    has_gills: bool = False
    defeated_big_kahoona: bool = False
    bank_gold: int = 0
    """Deposited at any city's Bank -- earns compound interest over time, see world/bank.py."""
    bank_last_interest_tick: int = 0
    banker_reckoning_purchased: bool = False
    """The Banker's Reckoning is a one-per-character purchase, like the Mad Scientist's bionic upgrade."""
    owned_properties: tuple[RentalProperty, ...] = field(default_factory=tuple)
    owned_businesses: tuple[Business, ...] = field(default_factory=tuple)

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0

    @property
    def is_exhausted(self) -> bool:
        return self.current_stamina <= 0

    def skill_level(self, type_: SkillType) -> int:
        skill = self.skills.get(type_)
        return skill.level if skill else 0

    def knows_skill(self, type_: SkillType) -> bool:
        return type_ in self.skills

    def perk_rank(self, perk: Perk) -> int:
        return self.perks.get(perk, 0)

    def equipped_in_slot(self, kind: ItemKind) -> Item | None:
        return {
            ItemKind.WEAPON: self.equipped_weapon,
            ItemKind.ARMOR: self.equipped_armor,
            ItemKind.OFFHAND: self.equipped_offhand,
            ItemKind.HEAD: self.equipped_head,
            ItemKind.RING: self.equipped_ring,
            ItemKind.AMULET: self.equipped_amulet,
        }.get(kind)

    def with_equipped_in_slot(self, kind: ItemKind, item: Item | None) -> "PlayerCharacter":
        from dataclasses import replace

        field_name = {
            ItemKind.WEAPON: "equipped_weapon",
            ItemKind.ARMOR: "equipped_armor",
            ItemKind.OFFHAND: "equipped_offhand",
            ItemKind.HEAD: "equipped_head",
            ItemKind.RING: "equipped_ring",
            ItemKind.AMULET: "equipped_amulet",
        }.get(kind)
        if field_name is None:
            return self
        return replace(self, **{field_name: item})

    @property
    def reputation_title(self) -> str:
        if self.reputation <= -60:
            return "Reviled"
        if self.reputation <= -20:
            return "Outlaw"
        if self.reputation < 20:
            return "Unknown"
        if self.reputation < 60:
            return "Recognized"
        return "Renowned"
