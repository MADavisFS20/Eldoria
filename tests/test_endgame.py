"""check_endgame_trigger: the final battle must unlock off quests the player actually took on,
not off every dungeon/sky-realm generated anywhere in the whole world map."""
from eldoria.game import commands, engine
from eldoria.models import CharacterClass, Race


def _session_with_main_quest_done():
    session, _ = engine.new_game("Hero", Race.HUMAN, CharacterClass.WARRIOR)
    session.completed_quests.add(commands.MAIN_QUEST_ID)
    return session


def test_endgame_does_not_unlock_without_completing_main_quest():
    session, _ = engine.new_game("Hero", Race.HUMAN, CharacterClass.WARRIOR)
    from eldoria.game.commands import Log

    commands.check_endgame_trigger(session, Log())
    assert not session.final_battle_unlocked


def test_endgame_does_not_unlock_with_no_dungeons_discovered_yet():
    """Main quest alone shouldn't vacuously satisfy an empty discovered-quests check."""
    from eldoria.game.commands import Log

    session = _session_with_main_quest_done()
    assert not session.discovered_quests
    commands.check_endgame_trigger(session, Log())
    assert not session.final_battle_unlocked


def test_endgame_does_not_unlock_while_a_discovered_subrealm_quest_is_incomplete():
    from eldoria.game.commands import Log

    session = _session_with_main_quest_done()
    session.discovered_quests.add("some-dungeon-id")
    commands.check_endgame_trigger(session, Log())
    assert not session.final_battle_unlocked


def test_endgame_unlocks_from_discovered_quests_alone_ignoring_the_rest_of_the_world():
    """The real bug: the world generates ~30 sub-realms total, but the player should only
    ever need to finish the ones they found, not every dungeon on the entire map."""
    from eldoria.game.commands import Log

    session = _session_with_main_quest_done()
    assert len(session.world.sub_realms) > 1, "world generation should produce many sub-realms"

    session.discovered_quests.add("some-dungeon-id")
    session.completed_quests.add("some-dungeon-id")
    commands.check_endgame_trigger(session, Log())

    assert session.final_battle_unlocked
    assert not all(sid in session.completed_quests for sid in session.world.sub_realms), \
        "unlock happened without touching the vast majority of the world's sub-realms"
