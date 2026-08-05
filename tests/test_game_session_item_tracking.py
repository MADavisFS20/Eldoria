"""Ported from GameSessionItemTrackingTest.kt: index-based (not name-based) ground-item tracking."""
import random

from eldoria.game.session import GameSession
from eldoria.models import Biome, CharacterClass, GameLocation, Item, ItemKind, PopulationTier, Race, World
from eldoria.world.player_character_factory import create as create_player


def _session_with_duplicate_items() -> GameSession:
    herb = Item(name="Swamp Herb", kind=ItemKind.MATERIAL, tier=1, value=5, max_durability=1)
    loc = GameLocation(
        id="0_0", x=0, y=0, biome=Biome.PLAINS, name="Swamp", description="test",
        population_tier=PopulationTier.WILDERNESS, difficulty_tier=1, difficulty_score=20,
        beings=(), exits={}, items=(herb, herb, herb),
    )
    world = World(width=1, height=1, seed=1, locations={"0_0": loc})
    player = create_player("Test", Race.HUMAN, CharacterClass.WARRIOR, random.Random(1))
    return GameSession(world, player, "0_0", "0_0", random.Random(1))


def test_three_identically_named_items_taken_one_at_a_time():
    session = _session_with_duplicate_items()

    assert len(session.current_items()) == 3
    first_idx, _ = session.current_items()[0]
    session.mark_taken(first_idx)

    assert len(session.current_items()) == 2, "taking one Swamp Herb must leave the other two available"

    second_idx, _ = session.current_items()[0]
    session.mark_taken(second_idx)
    assert len(session.current_items()) == 1

    third_idx, _ = session.current_items()[0]
    session.mark_taken(third_idx)
    assert session.current_items() == []


def test_taken_item_state_round_trips_through_snapshot():
    session = _session_with_duplicate_items()
    idx, _ = session.current_items()[0]
    session.mark_taken(idx)
    assert len(session.current_items()) == 2

    snap = session.snapshot()
    restored = _session_with_duplicate_items()
    restored.restore_from(snap)
    assert len(restored.current_items()) == 2, "exactly one of the three should still read as taken after restoring"
