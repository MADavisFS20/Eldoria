"""Ported from SaveManagerTest.kt: round-trip test for the JSON save/load, including 'exotic' nested types."""
import random

from eldoria.game.session import Snapshot
from eldoria.models import CharacterClass, DiceFormula, DieType, HiredCompanion, Item, ItemKind, MagicEffect, Perk, Race, Subclass
from eldoria.world import save_manager
from eldoria.world.player_character_factory import create as create_player

_TEST_SESSION_ID = "pytest-save-roundtrip"


def _cleanup():
    save_file, tmp_file = save_manager._paths(_TEST_SESSION_ID)
    save_file.unlink(missing_ok=True)
    tmp_file.unlink(missing_ok=True)


def setup_function(_):
    _cleanup()


def teardown_function(_):
    _cleanup()


def _build_snapshot() -> Snapshot:
    from dataclasses import replace

    rng = random.Random(42)
    player = create_player("RoundTripHero", Race.DWARF, CharacterClass.PALADIN, rng)
    player = replace(
        player,
        gold=777,
        level=3,
        perks={Perk.TOUGHNESS: 1, Perk.IRON_SKIN: 3},
        subclass=Subclass.VAMPIRE,
        companion=HiredCompanion(
            name="Loyal Retainer",
            attack_bonus=4,
            armor_class=14,
            damage=DiceFormula(1, DieType.D8, 2),
            origin_location_id="loc-1",
            hired_at_millis=1_700_000_000_000,
        ),
        inventory=(
            Item(
                name="Ring of Cursed Fortune",
                kind=ItemKind.TRINKET,
                tier=3,
                magic_effect=MagicEffect("Cursed Luck", "willpower", -2, False),
                value=250,
                max_durability=1,
            ),
        ),
    )
    return Snapshot(
        seed=123456789,
        player=player,
        location_id="loc-1",
        home_location_id="loc-1",
        sub_realm_id="dungeon-3",
        sub_realm_room_id="room-7",
        game_tick=42,
        discovered_locations={"loc-1", "loc-2", "loc-3"},
        defeated_at={"loc-2": {0: 5, 3: 12}},
        departed_at={"loc-1": 40},
        taken_items={"loc-2": {0}},
        discovered_quests={"quest-a"},
        completed_quests={"quest-a"},
        bestiary={"Goblin Scavenger", "Dire Wolf"},
        final_battle_unlocked=True,
        final_battle_won=False,
        completed_side_quests={"side-1", "side-2"},
    )


def test_save_then_load_round_trips_every_field():
    original = _build_snapshot()

    assert not save_manager.exists(_TEST_SESSION_ID), "no stray save file should exist before the test writes one"
    save_manager.save(_TEST_SESSION_ID, original)
    assert save_manager.exists(_TEST_SESSION_ID)

    loaded = save_manager.load(_TEST_SESSION_ID)
    assert loaded is not None
    assert loaded == original, "round-tripped snapshot must be structurally identical to the original"


def test_load_returns_none_when_no_save_exists():
    assert not save_manager.exists(_TEST_SESSION_ID)
    assert save_manager.load(_TEST_SESSION_ID) is None


def test_save_overwrites_previous_save_rather_than_versioning():
    from dataclasses import replace

    save_manager.save(_TEST_SESSION_ID, _build_snapshot())
    second = replace(_build_snapshot(), game_tick=999)
    save_manager.save(_TEST_SESSION_ID, second)

    loaded = save_manager.load(_TEST_SESSION_ID)
    assert loaded.game_tick == 999
    _, tmp_file = save_manager._paths(_TEST_SESSION_ID)
    assert not tmp_file.exists(), "temp file must not linger after a successful save"
