"""Ported from PlayerCharacterEquipSlotTest.kt: the 6-slot equip lookup/update helpers."""
import random
from dataclasses import replace

from eldoria.models import CharacterClass, Item, ItemKind, Race
from eldoria.world.player_character_factory import create as create_player


def _base_player():
    return create_player("Test", Race.HUMAN, CharacterClass.WARRIOR, random.Random(1))


def test_equipped_in_slot_reads_right_field_for_each_slot():
    player = _base_player()
    ring = Item(name="Ring", kind=ItemKind.RING, tier=1, value=1, max_durability=1)
    amulet = Item(name="Amulet", kind=ItemKind.AMULET, tier=1, value=1, max_durability=1)
    head = Item(name="Head", kind=ItemKind.HEAD, tier=1, value=1, max_durability=1)
    offhand = Item(name="Offhand", kind=ItemKind.OFFHAND, tier=1, value=1, max_durability=1)

    equipped = replace(player, equipped_ring=ring, equipped_amulet=amulet, equipped_head=head, equipped_offhand=offhand)

    assert equipped.equipped_in_slot(ItemKind.RING) == ring
    assert equipped.equipped_in_slot(ItemKind.AMULET) == amulet
    assert equipped.equipped_in_slot(ItemKind.HEAD) == head
    assert equipped.equipped_in_slot(ItemKind.OFFHAND) == offhand
    assert equipped.equipped_in_slot(ItemKind.WEAPON) == player.equipped_weapon
    assert equipped.equipped_in_slot(ItemKind.ARMOR) == player.equipped_armor


def test_equipped_in_slot_returns_none_for_non_equippable_kinds():
    player = _base_player()
    assert player.equipped_in_slot(ItemKind.QUEST_ITEM) is None
    assert player.equipped_in_slot(ItemKind.MATERIAL) is None
    assert player.equipped_in_slot(ItemKind.BOAT) is None
    assert player.equipped_in_slot(ItemKind.TRINKET) is None


def test_with_equipped_in_slot_writes_right_field_leaves_others():
    player = _base_player()
    ring = Item(name="Ring", kind=ItemKind.RING, tier=1, value=1, max_durability=1)

    updated = player.with_equipped_in_slot(ItemKind.RING, ring)

    assert updated.equipped_ring == ring
    assert updated.equipped_weapon == player.equipped_weapon
    assert updated.equipped_armor == player.equipped_armor
    assert updated.equipped_amulet is None
