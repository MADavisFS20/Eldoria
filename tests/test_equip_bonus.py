"""Ported from EquipBonusTest.kt: apply_item_bonus is the highest-risk arithmetic in equip()."""
import random

from eldoria.game.commands import apply_item_bonus
from eldoria.models import CharacterClass, Item, ItemKind, MagicEffect, Race
from eldoria.world.player_character_factory import create as create_player


def _base_player():
    return create_player("Test", Race.HUMAN, CharacterClass.WARRIOR, random.Random(1))


def test_armor_class_bonus_applies_then_fully_reverses():
    player = _base_player()
    starting_ac = player.armor_class
    shield = Item(name="Test Shield", kind=ItemKind.OFFHAND, tier=1, armor_class_bonus=4, value=10, max_durability=10)

    equipped = apply_item_bonus(player, shield, 1)
    assert equipped.armor_class == starting_ac + 4

    reversed_ = apply_item_bonus(equipped, shield, -1)
    assert reversed_.armor_class == starting_ac, "reversing must land exactly back at the starting AC, not drift"


def test_beneficial_magic_effect_applies_then_fully_reverses():
    player = _base_player()
    starting_str = player.strength
    ring = Item(
        name="Ring of Might", kind=ItemKind.RING, tier=1,
        magic_effect=MagicEffect("Empowering Aura", "strength", 3, True),
        value=10, max_durability=10,
    )

    equipped = apply_item_bonus(player, ring, 1)
    assert equipped.strength == starting_str + 3

    reversed_ = apply_item_bonus(equipped, ring, -1)
    assert reversed_.strength == starting_str


def test_curse_magic_effect_subtracts_on_apply_and_adds_back_on_reverse():
    player = _base_player()
    starting_speed = player.speed
    cursed_item = Item(
        name="Cursed Trinket", kind=ItemKind.AMULET, tier=1,
        magic_effect=MagicEffect("Chilling Grasp", "speed", 5, False),
        value=10, max_durability=10,
    )

    equipped = apply_item_bonus(player, cursed_item, 1)
    assert equipped.speed == starting_speed - 5, "a curse (beneficial=False) must subtract, not add"

    reversed_ = apply_item_bonus(equipped, cursed_item, -1)
    assert reversed_.speed == starting_speed


def test_item_with_no_bonus_fields_is_a_noop():
    player = _base_player()
    plain_item = Item(name="Plain Rock", kind=ItemKind.TRINKET, tier=1, value=1, max_durability=1)
    assert apply_item_bonus(player, plain_item, 1) == player
