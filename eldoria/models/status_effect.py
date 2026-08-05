"""A combat status a weapon (or spell) can inflict on a hit."""
from __future__ import annotations

from enum import Enum


class StatusEffect(Enum):
    BURN = ("Burning", 5, False, 3)
    POISON = ("Poisoned", 5, False, 3)
    FREEZE = ("Frozen", 0, True, 1)

    def __init__(self, display_name: str, per_turn_damage: int, skips_turn: bool, default_turns: int):
        self.display_name = display_name
        self.per_turn_damage = per_turn_damage
        self.skips_turn = skips_turn
        self.default_turns = default_turns
