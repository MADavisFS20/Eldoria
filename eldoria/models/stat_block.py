"""The full physical/magical profile of any creature, NPC, or player."""
from __future__ import annotations

from dataclasses import dataclass, field

from eldoria.models.dice import DiceFormula
from eldoria.models.status_effect import StatusEffect


@dataclass(frozen=True)
class MagicEffect:
    """A magic effect that shifts one trait/skill up (buff) or down (curse)."""

    name: str
    affected_trait: str
    magnitude: int
    beneficial: bool


@dataclass(frozen=True)
class StatBlock:
    tier: int
    strength: int
    agility: int
    willpower: int
    max_health: int
    armor_class: int
    speed: int
    attack_bonus: int
    damage: DiceFormula
    magic_damage: DiceFormula | None
    magic_effect: MagicEffect | None
    worth: int
    status_resistances: frozenset[StatusEffect] = field(default_factory=frozenset)

    @staticmethod
    def modifier_of(score: int) -> int:
        """(score - 10) // 2, D&D-style ability modifier. Python's // already floors like Kotlin's floorDiv."""
        return (score - 10) // 2
