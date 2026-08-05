"""Dice: every stat in Eldoria is produced by rolling one of these, never a bare hardcoded number."""
from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class DieType(Enum):
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

    @property
    def sides(self) -> int:
        return self.value


@dataclass(frozen=True)
class DiceFormula:
    """An "NdX+M" formula, e.g. 2d8+3."""

    count: int
    die: DieType
    modifier: int = 0

    def roll(self, rng: random.Random) -> int:
        total = self.modifier
        for _ in range(self.count):
            total += rng.randint(1, self.die.sides)
        return total

    def average(self) -> float:
        return self.count * (self.die.sides + 1) / 2.0 + self.modifier

    def __str__(self) -> str:
        if self.modifier > 0:
            sign = f"+{self.modifier}"
        elif self.modifier < 0:
            sign = str(self.modifier)
        else:
            sign = ""
        return f"{self.count}d{self.die.sides}{sign}"
