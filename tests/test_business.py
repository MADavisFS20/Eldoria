"""Entrepreneurship: passive stakes carry real business risk; owned businesses depend entirely on who runs them."""
import random

from eldoria.models import Business
from eldoria.world import business as business_gen


def _passive(**overrides) -> Business:
    base = dict(
        id="biz1", location_id="1_1", location_name="Testville", name="Testville Tavern",
        business_type="Tavern", investment=1000, ownership_percent=20,
    )
    base.update(overrides)
    return Business(**base)


def _owned(**overrides) -> Business:
    base = dict(
        id="biz2", location_id="1_1", location_name="Testville", name="Testville Smithy",
        business_type="Smithy", investment=1000, ownership_percent=100,
    )
    base.update(overrides)
    return Business(**base)


def test_no_event_before_a_full_cycle_elapses():
    biz = _passive(last_event_tick=0)
    updated, lines, gold = business_gen.process_cycle(biz, business_gen.EVENT_CYCLE_TICKS - 1, random.Random(1))
    assert updated == biz
    assert lines == []
    assert gold == 0


def test_passive_stake_can_fail_entirely():
    found_failure = False
    for seed in range(200):
        biz = _passive(last_event_tick=0)
        updated, lines, gold = business_gen.process_cycle(biz, business_gen.EVENT_CYCLE_TICKS, random.Random(seed))
        if updated.is_failed:
            found_failure = True
            assert gold == 0
            break
    assert found_failure, "total loss must be a reachable outcome of a passive stake -- that's the real risk being taught"


def test_failed_business_stays_failed_and_produces_no_further_events():
    biz = _passive(is_failed=True, last_event_tick=0)
    updated, lines, gold = business_gen.process_cycle(biz, business_gen.EVENT_CYCLE_TICKS * 3, random.Random(5))
    assert updated.is_failed
    assert lines == []
    assert gold == 0


def test_owned_business_with_no_manager_earns_nothing():
    biz = _owned(last_event_tick=0)
    updated, lines, gold = business_gen.process_cycle(biz, business_gen.EVENT_CYCLE_TICKS, random.Random(1))
    assert gold == 0
    assert any("idle" in line for line in lines)


def test_good_manager_grows_profit_over_successive_cycles():
    biz = _owned(manager_name="Test Manager", manager_quality="good", last_event_tick=0)
    rng = random.Random(2)
    tick = 0
    first_profit = None
    last_profit = None
    for _ in range(8):
        tick += business_gen.EVENT_CYCLE_TICKS
        biz, lines, gold = business_gen.process_cycle(biz, tick, rng)
        if gold > 0:
            if first_profit is None:
                first_profit = gold
            last_profit = gold
    assert first_profit is not None and last_profit is not None
    assert last_profit >= first_profit, "a good manager's profit should trend upward (or flat), not shrink, the longer they stay"


def test_manager_quality_is_revealed_only_after_enough_cycles_observed():
    biz = _owned(manager_name="Test Manager", manager_quality="corrupt", last_event_tick=0)
    rng = random.Random(3)
    tick = 0
    for i in range(business_gen.MANAGER_REVEAL_CYCLES - 1):
        tick += business_gen.EVENT_CYCLE_TICKS
        biz, _, _ = business_gen.process_cycle(biz, tick, rng)
        assert not biz.manager_revealed, "quality must stay hidden before the reveal threshold"
    tick += business_gen.EVENT_CYCLE_TICKS
    biz, lines, _ = business_gen.process_cycle(biz, tick, rng)
    assert biz.manager_revealed
    assert any("skimming" in line or "clear" in line for line in lines)


def test_roll_manager_candidate_quality_distribution_is_reachable():
    qualities = {business_gen.roll_manager_candidate(random.Random(seed))[1] for seed in range(200)}
    assert qualities == {"good", "average", "corrupt", "incompetent"}


def test_sell_price_rewards_a_net_profitable_business_over_a_lossy_one():
    profitable = _owned(lifetime_profit_collected=500, lifetime_losses=50)
    lossy = _owned(lifetime_profit_collected=50, lifetime_losses=500)
    assert business_gen.sell_price(profitable) > business_gen.sell_price(lossy)


def test_stake_percent_for_investment_is_capped_at_49():
    assert business_gen.stake_percent_for_investment(10_000, existing_percent=0) <= 49
    assert business_gen.stake_percent_for_investment(1000, existing_percent=45) <= 4
