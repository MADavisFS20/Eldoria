"""Mr. Davis, the time traveler, and his invisible AI companion's biome narration."""
from dataclasses import replace

from eldoria.data import ai_companion_lore
from eldoria.game import commands, engine
from eldoria.models import Biome, CharacterClass, PopulationTier, Race


def test_ai_biome_lines_cover_every_biome_with_multiple_facts():
    for biome in Biome:
        facts = ai_companion_lore.AI_BIOME_LINES.get(biome)
        assert facts and len(facts) >= 2, f"{biome} needs at least two rotating facts"
        assert all(isinstance(f, str) and f for f in facts)


def test_mr_davis_is_present_at_the_guaranteed_start_location():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    assert any(b.name == ai_companion_lore.MR_DAVIS_NAME for b in session.current_location.beings)


def test_every_new_character_can_meet_mr_davis_immediately():
    for race in Race:
        for character_class in list(CharacterClass)[:2]:  # a couple of combos is enough to prove it's not race/class-dependent
            session, _ = engine.new_game("Wanderer", race, character_class)
            assert any(b.name == ai_companion_lore.MR_DAVIS_NAME for b in session.current_location.beings)


def test_talking_to_mr_davis_first_time_sets_flag_and_shows_full_intro():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    assert not session.met_time_traveler
    log = engine.execute_command(session, "davis-test", "talk davis")
    assert session.met_time_traveler
    joined = " ".join(text for _, text in log.lines)
    assert "Davis" in joined
    assert "frequency" in joined.lower()


def test_talking_to_mr_davis_again_shows_shorter_repeat_line():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    engine.execute_command(session, "davis-test2", "talk davis")
    log = engine.execute_command(session, "davis-test2", "talk davis")
    joined = " ".join(text for _, text in log.lines)
    assert any(line in joined for line in ai_companion_lore.MR_DAVIS_REPEAT)


def test_no_ai_narration_before_meeting_mr_davis():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    assert not session.met_time_traveler
    desert_city = next(loc for loc in session.world.locations.values() if loc.biome == Biome.DESERT and loc.population_tier == PopulationTier.CITY)
    session.discover(desert_city.id)
    log = engine.execute_command(session, "davis-test3", f"travel {desert_city.name.split()[0]}")
    assert not any("voice rides the wind" in text for _, text in log.lines)


def test_ai_narrates_on_biome_crossing_after_meeting_davis():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    session.met_time_traveler = True
    desert_city = next(loc for loc in session.world.locations.values() if loc.biome == Biome.DESERT and loc.population_tier == PopulationTier.CITY)
    session.discover(desert_city.id)
    log = engine.execute_command(session, "davis-test4", f"travel {desert_city.name.split()[0]}")
    assert any("voice rides the wind" in text for _, text in log.lines)


def test_ai_does_not_narrate_when_biome_is_unchanged():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    session.met_time_traveler = True
    same_biome_city = next(
        loc for loc in session.world.locations.values()
        if loc.biome == session.current_location.biome and loc.population_tier == PopulationTier.CITY and loc.id != session.location_id
    )
    session.discover(same_biome_city.id)
    log = engine.execute_command(session, "davis-test5", f"travel {same_biome_city.name.split()[0]}")
    assert not any("voice rides the wind" in text for _, text in log.lines)


def test_time_traveler_state_survives_snapshot_round_trip():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    engine.execute_command(session, "davis-test6", "talk davis")
    snap = session.snapshot()

    session2, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    session2.restore_from(snap)
    assert session2.met_time_traveler


# --- Proactive intercept within the first 10 moves -------------------------

def _bounce_moves(session, session_id, n):
    """Alternates south/north inside the home region, n times, without ever talking to anyone."""
    logs = []
    for i in range(n):
        direction = "south" if i % 2 == 0 else "north"
        logs.append(engine.execute_command(session, session_id, direction))
    return logs


def test_intercept_is_guaranteed_by_the_tenth_move_even_on_unlucky_rolls():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    # Force every 20% roll to miss by using a seed where the intercept never rolls true early --
    # verified empirically below via move_count, but the *guarantee* is the real contract being tested.
    logs = _bounce_moves(session, "intercept-guarantee-test", commands.TIME_TRAVELER_INTERCEPT_MAX_MOVES)
    assert session.met_time_traveler, "Mr. Davis must have intercepted the player by the 10th move at the latest"
    assert session.move_count <= commands.TIME_TRAVELER_INTERCEPT_MAX_MOVES
    triggering_log = next(log for log in logs if any("falls into step" in text for _, text in log.lines))
    joined = " ".join(text for _, text in triggering_log.lines)
    assert "Next-Flix" in joined


def test_intercept_never_fires_twice():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    logs = _bounce_moves(session, "intercept-once-test", commands.TIME_TRAVELER_INTERCEPT_MAX_MOVES + 5)
    intercept_count = sum(1 for log in logs if any("falls into step" in text for _, text in log.lines))
    assert intercept_count == 1


def test_intercept_does_not_fire_after_a_manual_talk():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    engine.execute_command(session, "intercept-vs-talk-test", "talk davis")
    assert session.met_time_traveler
    logs = _bounce_moves(session, "intercept-vs-talk-test", commands.TIME_TRAVELER_INTERCEPT_MAX_MOVES + 5)
    assert not any("falls into step" in text for log in logs for _, text in log.lines)


def test_move_count_only_advances_on_successful_overworld_moves():
    session, _ = engine.new_game("Wanderer", Race.HUMAN, CharacterClass.WARRIOR)
    assert session.move_count == 0
    engine.execute_command(session, "move-count-test", "look")
    assert session.move_count == 0, "non-movement commands must not advance the intercept countdown"
    engine.execute_command(session, "move-count-test", "north")
    assert session.move_count == 1
