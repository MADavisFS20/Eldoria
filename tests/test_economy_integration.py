"""Engine-level integration coverage for the economy features -- catches command-dispatch wiring bugs
that unit tests of the underlying math can't."""
from dataclasses import replace

from eldoria.game import engine
from eldoria.models import CharacterClass, PopulationTier, Race


def _rich_session():
    session, _ = engine.new_game("Tester", Race.HUMAN, CharacterClass.WARRIOR)
    session.player = replace(session.player, gold=5000)
    return session


def _run(session, text):
    return engine.execute_command(session, "economy-test", text)


def test_bank_deposit_and_withdraw_round_trip():
    session = _rich_session()
    assert session.current_location.population_tier == PopulationTier.CITY

    _run(session, "deposit 1000")
    assert session.player.bank_gold == 1000
    assert session.player.gold == 4000

    log = _run(session, "withdraw 500")
    assert session.player.bank_gold == 500
    assert session.player.gold == 4498  # 4000 + 500 withdrawn - 2g fee (0.5% of 500, matching bank.withdrawal_fee)
    assert any("withdraw" in text.lower() for _, text in log.lines)


def test_bank_interest_accrues_over_many_commands():
    session = _rich_session()
    _run(session, "deposit 2000")
    for _ in range(60):
        _run(session, "look")
    log = _run(session, "bank")
    assert session.player.bank_gold > 2000, "interest should have compounded over that many ticks"
    assert any("interest" in text.lower() or "bank" in text.lower() for _, text in log.lines)


def test_buy_sell_house_round_trip():
    session = _rich_session()
    gold_before = session.player.gold
    _run(session, "buy house")
    assert len(session.player.owned_properties) == 1
    assert session.player.gold < gold_before

    _run(session, "sell house")
    assert len(session.player.owned_properties) == 0


def test_found_business_and_hire_manager():
    session = _rich_session()
    _run(session, "start tavern")
    assert len(session.player.owned_businesses) == 1
    biz = session.player.owned_businesses[0]
    assert biz.is_fully_owned
    assert not biz.has_manager

    _run(session, "hire manager")
    biz = session.player.owned_businesses[0]
    assert biz.has_manager
    assert biz.manager_quality is not None


def test_passive_business_investment():
    session = _rich_session()
    _run(session, "invest 200")
    assert len(session.player.owned_businesses) == 1
    biz = session.player.owned_businesses[0]
    assert not biz.is_fully_owned
    assert 1 <= biz.ownership_percent <= 49


def test_economy_state_survives_snapshot_round_trip():
    session = _rich_session()
    _run(session, "deposit 500")
    _run(session, "buy house")
    _run(session, "start tavern")
    _run(session, "hire manager")
    _run(session, "buy reckoning")

    snap = session.snapshot()
    session2 = _rich_session()
    session2.restore_from(snap)

    assert session2.player.bank_gold == session.player.bank_gold
    assert len(session2.player.owned_properties) == len(session.player.owned_properties)
    assert len(session2.player.owned_businesses) == len(session.player.owned_businesses)
    assert session2.player.owned_businesses[0].manager_name == session.player.owned_businesses[0].manager_name
    assert any(i.is_compounding for i in session2.player.inventory)


def test_prompt_command_shows_vitals():
    session = _rich_session()
    log = _run(session, "prompt")
    assert len(log.lines) == 1
    assert "HP:" in log.lines[0][1] and "Gold:" in log.lines[0][1]
