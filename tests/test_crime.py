"""Street and white-collar crime: robbery only ever touches cash on hand; gambling always favors the house."""
import random

from eldoria.world import crime


def test_no_robbery_below_the_gold_threshold():
    for seed in range(50):
        assert crime.maybe_rob_player(crime.ROBBERY_GOLD_THRESHOLD - 1, random.Random(seed)) == 0


def test_robbery_is_a_reachable_outcome_above_the_threshold():
    stolen_amounts = [crime.maybe_rob_player(500, random.Random(seed)) for seed in range(300)]
    assert any(amount > 0 for amount in stolen_amounts), "robbery must actually be able to happen, not just be threatened"
    assert all(amount <= 500 for amount in stolen_amounts), "can never steal more than the player is carrying"


def test_gambling_house_edge_means_the_house_wins_more_than_half_the_time():
    outcomes = [crime.gamble(10, random.Random(seed))[0] for seed in range(2000)]
    win_rate = sum(outcomes) / len(outcomes)
    expected = (50 - crime.GAMBLING_HOUSE_EDGE_PERCENT) / 100.0
    assert abs(win_rate - expected) < 0.03, "win rate should track the stated house edge, not fair 50/50 odds"
    assert win_rate < 0.5, "the house edge must make gambling a losing proposition on average"


def test_gambling_net_change_matches_win_loss():
    won, delta = True, None
    for seed in range(50):
        won, delta = crime.gamble(25, random.Random(seed))
        assert delta == 25 if won else delta == -25


def test_fence_pays_well_under_fair_value():
    price = crime.fence_price(1000)
    assert price < 1000
    assert price == int(1000 * crime.FENCE_PAYOUT_PERCENT / 100.0)
