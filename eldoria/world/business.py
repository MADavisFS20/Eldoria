"""Entrepreneurship: a passive minority stake in someone else's venture, or founding and running your own.

Teaches, honestly, through outcomes rather than a lecture:
 - A passive equity stake pays a share of profit but comes with zero
   control -- the business succeeds or fails on its own, and a real
   business can fail completely (total loss of your stake), not just
   underperform.
 - Owning a business outright means someone has to run it day to day.
   Real delegation risk: a good manager compounds profit over time, an
   incompetent one bleeds it, and a corrupt one can look fine right up
   until a scandal wipes out a chunk of the business at once.
 - Competence and honesty don't announce themselves. A candidate's
   quality here is deliberately NOT signaled by how they're described --
   the polished one can be a disaster, the unlikely one can be exactly
   who you needed. It only becomes clear after you've actually seen them
   work for a while.
"""
from __future__ import annotations

import random
from dataclasses import replace

from eldoria.models import Business, PopulationTier

EVENT_CYCLE_TICKS = 15
MANAGER_REVEAL_CYCLES = 3
"""How many cycles of observed performance before the player can be sure what kind of manager they hired."""

BUSINESS_TYPES = ["Tavern", "Smithy", "Trading Post", "Apothecary", "Tannery", "Bakery", "Stable", "Weaver's Shop"]

_CANDIDATE_DESCRIPTIONS = [
    "a bright-eyed young merchant fresh from the capital, silk-vested and full of confident talk",
    "a limping stablehand who mostly talks to the horses",
    "a retired soldier missing two fingers, blunt and unsmiling",
    "a cheerful widow who's run three market stalls into the ground already, by her own admission",
    "a quiet scholar with ink-stained hands and a battered ledger",
    "a boisterous former pirate who swears they've gone straight",
    "a sharp-dressed accountant with a very firm handshake",
    "a barefoot orphan grown into a surprisingly steady adult",
    "a nobleman's disowned second son, all polish and no calluses",
    "a weathered dockworker who reads faster than anyone gives them credit for",
]


def founding_cost_for(population_tier: PopulationTier, difficulty_tier: int) -> int:
    base = 500 if population_tier == PopulationTier.CITY else 200
    return base + difficulty_tier * 80


def stake_percent_for_investment(amount: int, existing_percent: int = 0) -> int:
    """20g buys roughly 1% -- passive stakes are capped at 49% so you're never the one steering."""
    bought = max(1, amount // 20)
    return min(49, existing_percent + bought) - existing_percent


def roll_manager_candidate(rng: random.Random) -> tuple[str, str]:
    """Returns (description, hidden_quality). The description carries no reliable signal of quality -- that's the point."""
    description = rng.choice(_CANDIDATE_DESCRIPTIONS)
    roll = rng.randrange(100)
    if roll < 25:
        quality = "good"
    elif roll < 60:
        quality = "average"
    elif roll < 85:
        quality = "corrupt"
    else:
        quality = "incompetent"
    return description, quality


def sell_price(business: Business) -> int:
    """A rough valuation: half the original investment, adjusted by whether it's been net profitable."""
    base = business.investment * 0.5
    net = business.lifetime_profit_collected - business.lifetime_losses
    if net > 0:
        base *= 1.15
    elif net < 0:
        base *= 0.75
    return max(0, int(base))


def _passive_stake_cycle(biz: Business, rng: random.Random) -> tuple[Business, list[str], int]:
    """A business you don't control -- it succeeds or fails on its own merits."""
    roll = rng.randrange(100)
    profit_share = max(1, int(biz.investment * 0.06 * (biz.ownership_percent / 100.0)))

    if roll < 5:
        # Total business failure -- a real, if uncommon, outcome of passive investing.
        lines = [f"{biz.location_name}: word comes that the {biz.name} has folded entirely. Your stake is gone -- passive investing carries real risk of total loss, not just a bad quarter."]
        return replace(biz, is_failed=True), lines, 0
    if roll < 45:
        lines = [f"{biz.location_name}: the {biz.name} turns a solid profit this cycle. Your {biz.ownership_percent}% share pays out {profit_share}g."]
        return replace(biz, lifetime_profit_collected=biz.lifetime_profit_collected + profit_share), lines, profit_share
    if roll < 75:
        lines = [f"{biz.location_name}: the {biz.name} breaks even this cycle -- no payout, no loss."]
        return biz, lines, 0
    loss = max(1, int(biz.investment * 0.03 * (biz.ownership_percent / 100.0)))
    lines = [f"{biz.location_name}: the {biz.name} has a rough cycle and posts a loss. Your share absorbs {loss}g of it -- passive owners share the downside too, not just the profit."]
    return replace(biz, lifetime_losses=biz.lifetime_losses + loss), lines, -loss


def _owned_business_cycle(biz: Business, rng: random.Random) -> tuple[Business, list[str], int]:
    if not biz.has_manager:
        return biz, [f"{biz.location_name}: the {biz.name} sits idle -- no one is running it day to day, and it earns nothing while it waits for leadership."], 0

    quality = biz.manager_quality or "average"
    base_rate = biz.investment * 0.06
    roll = rng.randrange(100)
    observed = biz.manager_cycles_observed + 1
    just_revealed = (not biz.manager_revealed) and observed >= MANAGER_REVEAL_CYCLES

    if quality == "good":
        growth = 1 + min(observed, 10) * 0.03
        profit = max(1, int(base_rate * growth))
        lines = [f"{biz.location_name}: {biz.manager_name} runs the {biz.name} well and reinvests the gains -- {profit}g this cycle, and it's still growing."]
        biz = replace(biz, lifetime_profit_collected=biz.lifetime_profit_collected + profit)
        gold_delta = profit
    elif quality == "average":
        if roll < 70:
            profit = max(1, int(base_rate * (0.8 + rng.random() * 0.4)))
            lines = [f"{biz.location_name}: {biz.manager_name} keeps the {biz.name} running steadily. +{profit}g."]
            biz = replace(biz, lifetime_profit_collected=biz.lifetime_profit_collected + profit)
            gold_delta = profit
        else:
            lines = [f"{biz.location_name}: {biz.manager_name} has a slow cycle at the {biz.name} -- no profit this time, nothing lost either."]
            gold_delta = 0
    elif quality == "corrupt":
        if roll < 15:
            scandal = max(1, int(biz.investment * 0.35))
            lines = [
                f"{biz.location_name}: the books finally don't add up -- {biz.manager_name} has been skimming from the {biz.name} for a while now, and it costs you {scandal}g all at once when it comes out.",
                "A corrupt manager can look perfectly fine right up until the scandal breaks -- by then the damage is already done.",
            ]
            biz = replace(biz, lifetime_losses=biz.lifetime_losses + scandal)
            gold_delta = -scandal
        else:
            reported = max(0, int(base_rate * 0.35))
            lines = [f"{biz.location_name}: {biz.manager_name} reports a thin profit from the {biz.name} this cycle. +{reported}g." if reported else f"{biz.location_name}: {biz.manager_name} reports no profit from the {biz.name} this cycle -- again."]
            biz = replace(biz, lifetime_profit_collected=biz.lifetime_profit_collected + reported)
            gold_delta = reported
    else:  # incompetent
        if roll < 40:
            loss = max(1, int(base_rate * 0.5))
            lines = [f"{biz.location_name}: {biz.manager_name} means well, but the {biz.name} loses {loss}g to plain bad decisions this cycle."]
            biz = replace(biz, lifetime_losses=biz.lifetime_losses + loss)
            gold_delta = -loss
        elif roll < 70:
            lines = [f"{biz.location_name}: {biz.manager_name} scrapes by at the {biz.name} -- no profit, no disaster."]
            gold_delta = 0
        else:
            profit = max(1, int(base_rate * 0.25))
            lines = [f"{biz.location_name}: {biz.manager_name} gets lucky and the {biz.name} turns a small profit. +{profit}g."]
            biz = replace(biz, lifetime_profit_collected=biz.lifetime_profit_collected + profit)
            gold_delta = profit

    biz = replace(biz, manager_cycles_observed=observed)
    if just_revealed:
        biz = replace(biz, manager_revealed=True)
        verdicts = {
            "good": f"After watching {biz.manager_name} work for a while, it's clear: you found a genuinely good manager. Sometimes the best help really does come from the most unlikely places.",
            "average": f"You've seen enough now -- {biz.manager_name} is a perfectly ordinary manager. Not a disaster, not a star.",
            "corrupt": f"You've seen enough now to be sure: {biz.manager_name} is skimming from the till. Trust, once you have the evidence, is no longer a guess.",
            "incompetent": f"You've seen enough now: {biz.manager_name} means well but simply isn't cut out for this. Good intentions aren't the same as competence.",
        }
        lines = lines + [verdicts[quality]]

    return biz, lines, gold_delta


def process_cycle(biz: Business, current_tick: int, rng: random.Random) -> tuple[Business, list[str], int]:
    if biz.is_failed:
        return biz, [], 0
    if current_tick - biz.last_event_tick < EVENT_CYCLE_TICKS:
        return biz, [], 0
    biz = replace(biz, last_event_tick=current_tick)

    if biz.is_fully_owned:
        return _owned_business_cycle(biz, rng)
    return _passive_stake_cycle(biz, rng)
