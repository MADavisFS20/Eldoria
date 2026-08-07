"""Any physical item: weapon, armor, quest item, or misc trinket."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from eldoria.models.dice import DiceFormula
from eldoria.models.stat_block import MagicEffect
from eldoria.models.status_effect import StatusEffect


class ItemKind(Enum):
    """WEAPON/ARMOR(chest)/OFFHAND/HEAD/RING/AMULET are the six equip slots on PlayerCharacter."""

    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    OFFHAND = "OFFHAND"
    HEAD = "HEAD"
    RING = "RING"
    AMULET = "AMULET"
    QUEST_ITEM = "QUEST_ITEM"
    TRINKET = "TRINKET"
    MATERIAL = "MATERIAL"
    BOAT = "BOAT"
    CONSUMABLE = "CONSUMABLE"


@dataclass(frozen=True)
class Item:
    name: str
    kind: ItemKind
    tier: int
    value: int
    max_durability: int
    damage: DiceFormula | None = None
    armor_class_bonus: int | None = None
    magic_effect: MagicEffect | None = None
    current_durability: int | None = None
    is_legendary: bool = False
    has_cannons: bool = False
    inflicts_status: StatusEffect | None = None
    is_compounding: bool = False
    """WEAPON-only: each consecutive hit on the same target doubles the last hit's damage (capped). See commands.attack."""
    heal_amount: int | None = None
    """CONSUMABLE-only: health restored on use, see commands.use_item."""

    def __post_init__(self):
        if self.current_durability is None:
            object.__setattr__(self, "current_durability", self.max_durability)

    @property
    def is_broken(self) -> bool:
        return self.current_durability <= 0

    def worn(self, amount: int) -> "Item":
        return replace(self, current_durability=max(0, self.current_durability - amount))

    def repaired(self) -> "Item":
        return replace(self, current_durability=self.max_durability)
