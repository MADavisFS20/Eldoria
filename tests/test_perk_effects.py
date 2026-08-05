"""Ported from PerkEffectsPhase1Test.kt: stackable perk ranks."""
import random
from dataclasses import replace

import pytest

from eldoria.models import CharacterClass, Perk, Race
from eldoria.world import perk_effects
from eldoria.world.player_character_factory import create as create_player


def _player_with_pending_choices(n: int):
    player = create_player("Test", Race.HUMAN, CharacterClass.WARRIOR, random.Random(1))
    return replace(player, pending_perk_choices=n)


def test_picking_same_perk_three_times_stacks_rank_and_effect():
    player = _player_with_pending_choices(3)
    starting_ac = player.armor_class

    for _ in range(3):
        player = perk_effects.apply_perk(player, Perk.IRON_SKIN)

    assert player.perk_rank(Perk.IRON_SKIN) == 3
    assert player.armor_class == starting_ac + 3, "each IRON_SKIN pick should add +1 AC, stacking to +3"
    assert player.pending_perk_choices == 0


def test_applying_perk_with_no_pending_choices_raises():
    player = _player_with_pending_choices(0)
    with pytest.raises(ValueError):
        perk_effects.apply_perk(player, Perk.TOUGHNESS)


def test_distinct_perks_have_independent_ranks():
    player = _player_with_pending_choices(2)
    player = perk_effects.apply_perk(player, Perk.IRON_SKIN)
    player = perk_effects.apply_perk(player, Perk.TOUGHNESS)

    assert player.perk_rank(Perk.IRON_SKIN) == 1
    assert player.perk_rank(Perk.TOUGHNESS) == 1
    assert player.perk_rank(Perk.QUICK_REFLEXES) == 0, "an unpicked perk must read as rank 0, not throw"
