"""Rental property: an ongoing side-mechanic in real-estate investing, good and bad.

Teaches, honestly, through outcomes rather than a lecture:
 - Rental yield: rent collected relative to what a property cost, the basic
   way real investors compare one property to another.
 - Vacancy risk: an empty property earns nothing while it sits empty --
   a real, common risk in real estate, not a bug in this game.
 - Tenant risk and maintenance cost: a bad tenant (skipped rent, damage)
   can erase a property's paper gains just as easily as a good one grows them.
 - Not every investment pays off. Sometimes the honest answer is to sell at
   a loss rather than keep paying to maintain a bad one.
"""
from __future__ import annotations

import random
from dataclasses import replace

from eldoria.models import PopulationTier, RentalProperty

EVENT_CYCLE_TICKS = 15
RENT_YIELD_PER_CYCLE = 0.05
"""5% of purchase price per cycle, if occupied and paying -- a plausible rough rental yield."""

_TENANT_FIRST = ["Merric", "Yolanda", "Osric", "Petra", "Dalen", "Wren", "Bram", "Sela", "Corin", "Ilsa"]
_TENANT_LAST = ["Coombs", "Thatcher", "Vane", "Hollis", "Brandt", "Sowerby", "Marsh", "Quill", "Redditch", "Fenwick"]


def purchase_price_for(population_tier: PopulationTier, difficulty_tier: int) -> int:
    base = 600 if population_tier == PopulationTier.CITY else 250
    return base + difficulty_tier * 100


def repair_cost(prop: RentalProperty) -> int:
    missing = 100 - prop.condition
    return max(0, int(missing * prop.purchase_price * 0.01))


def sell_price(prop: RentalProperty) -> int:
    """Selling back returns a fraction of purchase price scaled by condition -- a run-down property sells for less."""
    return max(0, int(prop.purchase_price * 0.6 * (prop.condition / 100.0)))


def _roll_tenant_quality(rng: random.Random) -> str:
    roll = rng.randrange(100)
    if roll < 25:
        return "good"
    if roll < 85:
        return "average"
    return "bad"


def _random_tenant_name(rng: random.Random) -> str:
    return f"{rng.choice(_TENANT_FIRST)} {rng.choice(_TENANT_LAST)}"


def process_cycle(prop: RentalProperty, current_tick: int, rng: random.Random) -> tuple[RentalProperty, list[str], int]:
    """If a full cycle has elapsed since the property's last event, rolls exactly one.

    Returns (updated_property, narrative_lines, gold_delta). gold_delta is
    already net of nothing -- the caller applies it to the player's gold.
    """
    if current_tick - prop.last_event_tick < EVENT_CYCLE_TICKS:
        return prop, [], 0

    p = replace(prop, last_event_tick=current_tick)
    lines: list[str] = []
    gold_delta = 0

    if p.is_condemned:
        lines.append(f"{p.location_name}: the property still sits condemned, in too poor a state for anyone to rent. It needs real repair first.")
        return p, lines, 0

    if not p.is_occupied:
        p = replace(p, cycles_vacant_streak=p.cycles_vacant_streak + 1)
        if rng.randrange(100) < 40:
            quality = _roll_tenant_quality(rng)
            name = _random_tenant_name(rng)
            p = replace(p, tenant_name=name, tenant_quality=quality, cycles_vacant_streak=0)
            lines.append(f"{p.location_name}: a tenant named {name} has moved in.")
        else:
            lines.append(f"{p.location_name}: still sitting empty this cycle -- an empty property earns nothing while it waits (vacancy risk, and it's a real one).")
            if p.cycles_vacant_streak >= 3:
                lines.append(f"{p.location_name} has stayed vacant a long while now. Not every property is a good investment -- sometimes the honest move is to sell and cut your losses.")
        return p, lines, 0

    quality = p.tenant_quality or "average"
    roll = rng.randrange(100)
    rent = max(1, int(p.purchase_price * RENT_YIELD_PER_CYCLE))

    if quality == "good":
        if roll < 70:
            gold_delta = rent
            p = replace(p, condition=min(100, p.condition + 1), lifetime_rent_collected=p.lifetime_rent_collected + rent)
            lines.append(f"{p.location_name}: {p.tenant_name} pays rent on time and even tidies up the place. +{rent}g.")
        elif roll < 95:
            gold_delta = rent
            p = replace(p, lifetime_rent_collected=p.lifetime_rent_collected + rent)
            lines.append(f"{p.location_name}: {p.tenant_name} pays rent, quiet and reliable as ever. +{rent}g.")
        else:
            lines.append(f"{p.location_name}: {p.tenant_name} has moved on, leaving the place in good order.")
            p = replace(p, tenant_name=None, tenant_quality=None)
    elif quality == "bad":
        if roll < 35:
            gold_delta = rent
            p = replace(p, lifetime_rent_collected=p.lifetime_rent_collected + rent)
            lines.append(f"{p.location_name}: {p.tenant_name} actually pays rent this time. +{rent}g.")
        elif roll < 65:
            wear = 10
            p = replace(p, condition=max(0, p.condition - wear))
            lines.append(f"{p.location_name}: {p.tenant_name} skips rent and does {wear} worth of damage besides. A bad tenant is a real cost, not just lost income.")
        elif roll < 85:
            lines.append(f"{p.location_name}: {p.tenant_name} skips rent again.")
        else:
            wear = 15
            lines.append(f"{p.location_name}: {p.tenant_name} moves out in the night, leaving {wear} worth of damage on the way out.")
            p = replace(p, condition=max(0, p.condition - wear), tenant_name=None, tenant_quality=None)
    else:
        if roll < 55:
            gold_delta = rent
            p = replace(p, lifetime_rent_collected=p.lifetime_rent_collected + rent)
            lines.append(f"{p.location_name}: {p.tenant_name} pays rent as expected. +{rent}g.")
        elif roll < 70:
            wear = 3
            gold_delta = rent
            p = replace(p, condition=max(0, p.condition - wear), lifetime_rent_collected=p.lifetime_rent_collected + rent)
            lines.append(f"{p.location_name}: {p.tenant_name} pays rent, but ordinary wear and tear costs {wear} condition. +{rent}g.")
        elif roll < 90:
            lines.append(f"{p.location_name}: {p.tenant_name} is short this cycle and pays nothing.")
        else:
            lines.append(f"{p.location_name}: {p.tenant_name} moves out; the property is left in reasonable shape.")
            p = replace(p, tenant_name=None, tenant_quality=None)

    return p, lines, gold_delta
