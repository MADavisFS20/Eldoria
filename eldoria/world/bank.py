"""The Bank: compound interest on deposited gold, plus an honest side-by-side with simple interest.

Inspired by Achaea (achaea.com), the 1997 MUD this whole project traces its
roots to -- Achaea's economy runs on "gold sovereigns," kept in a personal
container or deposited at a bank, where withdrawals/transfers cost a real
0.5% fee. This module borrows that fee and adds interest on top of it, since
the goal here is to actually teach compound interest, not just flavor text.

Real personal-finance facts this is meant to demonstrate, honestly:
 - Compound interest is calculated on your growing balance (principal +
   previously earned interest), not just the original amount -- that's what
   makes it grow faster than simple interest over time.
 - The "Rule of 72": divide 72 by the interest rate (as a percent) to
   estimate how many compounding periods it takes to double your money.
 - Fees matter: a small, flat withdrawal fee is a real cost that quietly
   eats into returns if you move money in and out often.
"""
from __future__ import annotations

RATE_PER_CYCLE = 0.02
"""2% per compounding cycle -- deliberately a round, easy-to-verify-by-hand number."""

CYCLE_TICKS = 10
"""One compounding cycle = 10 game ticks (roughly 10 commands), so growth is visible within a session."""

WITHDRAWAL_FEE_PERCENT = 0.5
"""Matches Achaea's real bank withdrawal fee exactly -- a small, real transaction cost."""


def cycles_elapsed(last_settled_tick: int, current_tick: int) -> int:
    return max(0, (current_tick - last_settled_tick) // CYCLE_TICKS)


def settle_interest(balance: int, last_settled_tick: int, current_tick: int) -> tuple[int, int, int, int]:
    """Applies every fully-elapsed compounding cycle since the balance was last settled.

    Returns (new_balance, new_last_settled_tick, compound_gain, simple_gain_equivalent).
    `simple_gain_equivalent` answers "what would simple interest have paid over
    the same stretch, on the same starting balance?" -- for the side-by-side
    lesson, not an actual account state.
    """
    cycles = cycles_elapsed(last_settled_tick, current_tick)
    if cycles <= 0 or balance <= 0:
        return balance, last_settled_tick, 0, 0
    new_balance = int(balance * ((1 + RATE_PER_CYCLE) ** cycles))
    compound_gain = new_balance - balance
    simple_gain_equivalent = int(balance * RATE_PER_CYCLE * cycles)
    new_last_settled_tick = last_settled_tick + cycles * CYCLE_TICKS
    return new_balance, new_last_settled_tick, compound_gain, simple_gain_equivalent


def withdrawal_fee(amount: int) -> int:
    if amount <= 0:
        return 0
    return max(1, int(amount * WITHDRAWAL_FEE_PERCENT / 100.0))


def rule_of_72_cycles(rate_percent: float) -> float:
    """Cycles to roughly double at the given per-cycle rate (as a percent, e.g. 2.0 for 2%)."""
    return 72 / rate_percent if rate_percent > 0 else float("inf")
