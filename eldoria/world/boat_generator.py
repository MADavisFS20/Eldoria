"""Boats are bought at Sea-biome settlements and modeled as a plain Item (kind=BOAT).

Sailing wears one down, a bad fight can destroy it outright, and repairs
cost gold scaled to how battered it is, same shape as stat_generator.repair_cost.
"""
from __future__ import annotations

import random

from eldoria.models import DiceFormula, DieType, Item, ItemKind

_NAMES = ["Gullwing Skiff", "Saltbrine Sloop", "The Tidewalker", "Driftrunner", "The Brinehopper", "Foamcutter"]


def buy(rng: random.Random) -> Item:
    durability = DiceFormula(3, DieType.D8, 10).roll(rng)
    price = DiceFormula(4, DieType.D20, 40).roll(rng) * 3
    return Item(
        name=rng.choice(_NAMES),
        kind=ItemKind.BOAT,
        tier=1,
        value=price,
        max_durability=durability,
    )


def repair_cost(boat: Item) -> int:
    return (boat.max_durability - boat.current_durability) * 5
