"""Compound interest math: the core lesson the Bank exists to teach."""
from eldoria.world import bank


def test_no_interest_before_a_full_cycle_elapses():
    new_balance, new_last_tick, gain, simple = bank.settle_interest(1000, 0, bank.CYCLE_TICKS - 1)
    assert new_balance == 1000
    assert new_last_tick == 0
    assert gain == 0
    assert simple == 0


def test_compound_interest_outpaces_simple_interest_over_multiple_cycles():
    balance, last_tick, compound_gain, simple_gain = bank.settle_interest(1000, 0, bank.CYCLE_TICKS * 5)
    assert last_tick == bank.CYCLE_TICKS * 5
    # Compound: 1000 * 1.02^5 - 1000; simple: 1000 * 0.02 * 5 -- compound must be strictly larger past cycle 1.
    assert compound_gain > simple_gain
    assert balance == 1000 + compound_gain


def test_compound_interest_matches_the_textbook_formula():
    balance, _, _, _ = bank.settle_interest(1000, 0, bank.CYCLE_TICKS * 3)
    expected = int(1000 * (1 + bank.RATE_PER_CYCLE) ** 3)
    assert balance == expected


def test_zero_balance_never_accrues_interest():
    balance, last_tick, gain, simple = bank.settle_interest(0, 0, bank.CYCLE_TICKS * 10)
    assert balance == 0
    assert gain == 0
    assert simple == 0


def test_withdrawal_fee_matches_achaeas_real_rate():
    assert bank.withdrawal_fee(1000) == int(1000 * 0.005)
    assert bank.withdrawal_fee(0) == 0
    assert bank.withdrawal_fee(1) == 1, "even a tiny withdrawal costs at least 1 gold in fees, never rounds to free"


def test_rule_of_72_is_the_standard_approximation():
    assert bank.rule_of_72_cycles(2.0) == 36
    assert bank.rule_of_72_cycles(6.0) == 12
