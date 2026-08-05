"""Basic coverage for the FastAPI layer (new in the Python port, no Kotlin equivalent)."""
import random

from fastapi.testclient import TestClient

from eldoria.game.session import GameSession
from eldoria.models import (
    Biome, CharacterClass, Disposition, GameLocation, PopulationTier, QuestType,
    Race, RealmKind, SpawnEntry, SpawnKind, SubRealm, SubRealmQuest, SubRealmRoom, World,
)
from eldoria.web import session_store
from eldoria.web.main import app
from eldoria.world import stat_generator as sg
from eldoria.world.player_character_factory import create as create_player

client = TestClient(app)


def test_meta_lists_races_and_classes():
    r = client.get("/api/meta")
    assert r.status_code == 200
    data = r.json()
    assert len(data["races"]) == 5
    assert len(data["classes"]) == 7


def test_new_game_then_command_round_trip():
    r = client.post("/api/new_game", json={"name": "Testy", "race": "ELF", "character_class": "MAGE"})
    assert r.status_code == 200
    data = r.json()
    session_id = data["session_id"]
    assert data["state"]["character"]["name"] == "Testy"
    assert data["state"]["character"]["race"] == "Elf"

    r = client.post("/api/command", json={"session_id": session_id, "text": "look"})
    assert r.status_code == 200
    assert len(r.json()["log"]) > 0

    r = client.get(f"/api/state/{session_id}")
    assert r.status_code == 200
    assert "rows" in r.json()["map"]


def test_new_game_rejects_unknown_race():
    r = client.post("/api/new_game", json={"name": "X", "race": "NOPE", "character_class": "WARRIOR"})
    assert r.status_code == 400


def test_command_on_unknown_session_is_404():
    r = client.post("/api/command", json={"session_id": "does-not-exist", "text": "look"})
    assert r.status_code == 404


def test_continue_game_with_no_save_is_404():
    r = client.post("/api/continue_game", json={"session_id": "no-such-save"})
    assert r.status_code == 404


def test_static_files_served():
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/style.css").status_code == 200


def test_tiles3d_on_unknown_session_is_404():
    r = client.get("/api/tiles3d/does-not-exist")
    assert r.status_code == 404


def test_tiles3d_only_shows_discovered_tiles_with_live_beings_at_current_spot():
    r = client.post("/api/new_game", json={"name": "Scout", "race": "HUMAN", "character_class": "WARRIOR"})
    session_id = r.json()["session_id"]

    r = client.get(f"/api/tiles3d/{session_id}?radius=5")
    assert r.status_code == 200
    data = r.json()
    assert "tiles" in data
    here = data["you"]

    ids_seen = {t["id"] for t in data["tiles"]}
    assert f"{here['x']}_{here['y']}" in ids_seen

    current_tile = next(t for t in data["tiles"] if t["id"] == f"{here['x']}_{here['y']}")
    assert current_tile["biome"]
    assert current_tile["terrain"] in {"LAND", "WATERWAY", "BRIDGE"}

    # A far-off corner tile the player has never visited must never appear,
    # even though it's a valid in-bounds coordinate.
    r2 = client.get(f"/api/tiles3d/{session_id}?cx=0&cy=0&radius=1")
    far_ids = {t["id"] for t in r2.json()["tiles"]}
    assert "0_0" not in far_ids

    # A neighboring tile that IS discovered shows terrain but no live beings/items
    # (only the player's actual current spot reflects live respawn/defeat state).
    neighbor = next((t for t in data["tiles"] if t["id"] != current_tile["id"]), None)
    if neighbor is not None:
        assert neighbor["beings"] == []
        assert neighbor["items"] == []


def _session_in_sub_realm_entry_room():
    stats = sg.creature_stats(1, random.Random(1))
    beings = (SpawnEntry("Cave Rat", SpawnKind.CREATURE, Disposition.HOSTILE, stats),)
    room = SubRealmRoom(
        id="room0", name="Entry Chamber", description="test", difficulty_tier=1,
        is_boss_room=False, beings=beings, items=(), exits={"north": "room1"},
    )
    quest_item = sg.quest_item("Test Quest Item", 1, random.Random(2))
    legendary_item = sg.weapon_item("Test Legendary", 1, random.Random(3), legendary=True)
    quest = SubRealmQuest(title="Test Quest", type=QuestType.DEFEAT_GUARDIAN, objective="test", quest_item=quest_item, legendary_item=legendary_item)
    realm = SubRealm(
        id="realm0", kind=RealmKind.DUNGEON, name="Test Realm", biome=Biome.MOUNTAINS,
        entrance_location_id="0_0", entry_room_id="room0", boss_room_id="room0",
        rooms={"room0": room}, quest=quest,
    )
    loc = GameLocation(
        id="0_0", x=0, y=0, biome=Biome.MOUNTAINS, name="Entrance", description="test",
        population_tier=PopulationTier.WILDERNESS, difficulty_tier=1, difficulty_score=20,
        beings=(), exits={}, portal_id=realm.id,
    )
    world = World(width=1, height=1, seed=1, locations={"0_0": loc}, sub_realms={"realm0": realm})
    player = create_player("Delver", Race.HUMAN, CharacterClass.WARRIOR, random.Random(1))
    session = GameSession(world, player, "0_0", "0_0", random.Random(1))
    from eldoria.game.session import SubRealmPosition
    session.sub_realm_position = SubRealmPosition("realm0", "room0")
    return session_store.create(session)


def test_tiles3d_returns_room_shape_inside_a_sub_realm():
    session_id = _session_in_sub_realm_entry_room()
    r = client.get(f"/api/tiles3d/{session_id}")
    assert r.status_code == 200
    data = r.json()
    assert "room" in data
    room = data["room"]
    assert room["id"] == "room0"
    assert room["biome"] == "MOUNTAINS"
    assert room["is_entry_room"] is True
    assert room["is_boss_room"] is False
    assert room["exits"] == ["north"]
    assert [b["name"] for b in room["beings"]] == ["Cave Rat"]
