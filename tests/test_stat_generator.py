"""Ported from StatGeneratorPhase1Test.kt: equip-slot item generators and combat math."""
import random

from eldoria.models import ItemKind, StatusEffect
from eldoria.world import stat_generator as sg


def test_armor_item_defaults_to_chest_slot():
    item = sg.armor_item("Test Armor", 2, random.Random(1))
    assert item.kind == ItemKind.ARMOR
    assert item.armor_class_bonus is not None


def test_armor_item_offhand_and_head_grant_smaller_bonus_than_chest():
    tier = 3
    chest = sg.armor_item("Chest", tier, random.Random(1))
    offhand = sg.armor_item("Offhand", tier, random.Random(1), slot=ItemKind.OFFHAND)
    head = sg.armor_item("Head", tier, random.Random(1), slot=ItemKind.HEAD)

    assert offhand.kind == ItemKind.OFFHAND
    assert head.kind == ItemKind.HEAD
    assert offhand.armor_class_bonus <= chest.armor_class_bonus
    assert head.armor_class_bonus <= chest.armor_class_bonus
    assert offhand.armor_class_bonus >= 1, "should floor at +1, never 0 or negative"


def test_accessory_item_always_rolls_beneficial_magic_effect():
    for seed in range(1, 26):
        ring = sg.accessory_item("Test Ring", 2, random.Random(seed), slot=ItemKind.RING)
        assert ring.kind == ItemKind.RING
        assert ring.magic_effect is not None
        assert ring.magic_effect.beneficial, "accessory items must never roll a curse"
        assert ring.armor_class_bonus is None, "rings/amulets carry their bonus via magic_effect"


def test_legendary_weapons_always_inflict_status_mundane_never_do():
    legendary = sg.weapon_item("Legendary Blade", 3, random.Random(1), legendary=True)
    assert legendary.inflicts_status is not None
    assert legendary.inflicts_status in list(StatusEffect)

    mundane = sg.weapon_item("Plain Sword", 3, random.Random(1), legendary=False)
    assert mundane.inflicts_status is None


def test_crit_threshold_widens_crit_range_without_disturbing_fumble_rule():
    vanilla = sg.AttackRoll(natural_d20=19, total=25, crit_threshold=20)
    assert not vanilla.is_critical, "natural 19 should not crit at the default threshold"

    widened = sg.AttackRoll(natural_d20=19, total=25, crit_threshold=18)
    assert widened.is_critical, "natural 19 should crit once the threshold is lowered to 18"

    fumble = sg.AttackRoll(natural_d20=1, total=30, crit_threshold=10)
    assert fumble.is_fumble, "a natural 1 is always a fumble regardless of crit threshold"
    assert not fumble.is_critical, "natural 1 must never also count as a crit, even with a very wide threshold"
