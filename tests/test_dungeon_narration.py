"""Boss rooms and rescue captives should use their dedicated flavor lines, not the generic ones --
these were written in dialogue_content.py but never wired into commands.py."""
import random

from eldoria.data import dialogue_content
from eldoria.game.commands import Log, attack, talk
from eldoria.game.session import GameSession
from eldoria.models import Biome, CharacterClass, GameLocation, PopulationTier, Race, SpawnEntry, SpawnKind, StatBlock, World
from eldoria.world.player_character_factory import create as create_player
from eldoria.world.stat_generator import creature_stats


def _session_with_boss_room(is_rescue_captive_npc: bool = False):
    boss_stats = creature_stats(1, random.Random(1))
    beings = [SpawnEntry("Test Boss", SpawnKind.CREATURE, __import__("eldoria.models", fromlist=["Disposition"]).Disposition.HOSTILE, boss_stats)]
    if is_rescue_captive_npc:
        npc_stats = creature_stats(1, random.Random(2))
        beings.append(SpawnEntry("Trapped Villager", SpawnKind.NPC, __import__("eldoria.models", fromlist=["Disposition"]).Disposition.PASSIVE, npc_stats, is_rescue_captive=True))

    from eldoria.data.sub_realm_theme import dungeon_theme_for
    from eldoria.models import QuestType, RealmKind, SubRealm, SubRealmQuest, SubRealmRoom
    from eldoria.world import stat_generator as sg

    room = SubRealmRoom(
        id="room0", name="Boss Chamber", description="test", difficulty_tier=1,
        is_boss_room=True, beings=tuple(beings), items=(), exits={},
    )
    quest_item = sg.quest_item("Test Quest Item", 1, random.Random(3))
    legendary_item = sg.weapon_item("Test Legendary", 1, random.Random(4), legendary=True)
    quest = SubRealmQuest(title="Test Quest", type=QuestType.DEFEAT_GUARDIAN, objective="test", quest_item=quest_item, legendary_item=legendary_item)
    realm = SubRealm(
        id="realm0", kind=RealmKind.DUNGEON, name="Test Realm", biome=Biome.PLAINS,
        entrance_location_id="0_0", entry_room_id="room0", boss_room_id="room0",
        rooms={"room0": room}, quest=quest,
    )

    loc = GameLocation(
        id="0_0", x=0, y=0, biome=Biome.PLAINS, name="Entrance", description="test",
        population_tier=PopulationTier.WILDERNESS, difficulty_tier=1, difficulty_score=20,
        beings=(), exits={}, portal_id=realm.id,
    )
    world = World(width=1, height=1, seed=1, locations={"0_0": loc}, sub_realms={"realm0": realm})
    player = create_player("Test", Race.HUMAN, CharacterClass.WARRIOR, random.Random(1))
    session = GameSession(world, player, "0_0", "0_0", random.Random(1))
    from eldoria.game.session import SubRealmPosition
    session.sub_realm_position = SubRealmPosition("realm0", "room0")
    return session


def test_attacking_a_boss_room_creature_uses_the_boss_taunt_line():
    session = _session_with_boss_room()
    log = Log()
    attack(session, log, "Test Boss")
    joined = " ".join(text for _, text in log.lines)
    assert any(line.replace("{name}", "Test Boss") in joined for line in dialogue_content._BOSS_TAUNT_LINES)


def test_talking_to_a_rescue_captive_uses_the_captive_rescue_line():
    session = _session_with_boss_room(is_rescue_captive_npc=True)
    log = Log()
    talk(session, log, "Trapped Villager")
    joined = " ".join(text for _, text in log.lines)
    assert any(line.replace("{name}", "Trapped Villager") in joined for line in dialogue_content._CAPTIVE_RESCUE_LINES)
