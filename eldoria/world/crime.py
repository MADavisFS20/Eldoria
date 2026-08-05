"""Street-level and white-collar crime, scaled by a settlement's difficulty tier.

Poorer, rougher settlements (low difficulty tier) lean toward street crime --
robbery. Wealthier settlements (high difficulty tier, still CITY population)
lean toward organized/white-collar crime -- illegal gambling, black-market
fencing. Neither is glamorized: gambling always favors the house by design,
and getting robbed only ever touches gold carried on hand -- a real, honest
argument for keeping most of your wealth banked instead of on your person.
"""
from __future__ import annotations

import random

ROBBERY_GOLD_THRESHOLD = 40
ROBBERY_CHANCE_PERCENT = 10

GAMBLING_HOUSE_EDGE_PERCENT = 8
"""A real casino-style house edge -- the house wins more than fair 50/50 odds would suggest, every time, by design."""

FENCE_PAYOUT_PERCENT = 55
"""A fence pays well under fair value -- moving goods through someone who doesn't ask questions always costs a steep cut."""


def maybe_rob_player(gold_on_hand: int, rng: random.Random) -> int:
    """Returns gold stolen (0 if nothing happens). Only ever touches gold ON HAND, never banked gold."""
    if gold_on_hand < ROBBERY_GOLD_THRESHOLD:
        return 0
    if rng.randrange(100) >= ROBBERY_CHANCE_PERCENT:
        return 0
    return max(1, int(gold_on_hand * rng.uniform(0.15, 0.4)))


def gamble(amount: int, rng: random.Random) -> tuple[bool, int]:
    """A wager with a real house edge. Returns (won, net_gold_change)."""
    win_chance = 50 - GAMBLING_HOUSE_EDGE_PERCENT
    won = rng.randrange(100) < win_chance
    return won, (amount if won else -amount)


def fence_price(fair_value: int) -> int:
    return max(1, int(fair_value * FENCE_PAYOUT_PERCENT / 100.0))
