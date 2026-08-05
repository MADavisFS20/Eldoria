"""The Chronicle: real-world history discovered through play, and its five wired-in moments."""
import random
from dataclasses import replace

from eldoria.data import world_history_lore
from eldoria.game import commands, engine
from eldoria.game.commands import Log
from eldoria.models import Biome, CharacterClass, Item, ItemKind, PopulationTier, Race, Skill, SkillType
from eldoria.world import boat_generator


def test_world_history_lore_entries_are_well_formed():
    assert len(world_history_lore.ALL_CHRONICLE_ENTRIES) == 5
    for key, (title, facts) in world_history_lore.ALL_CHRONICLE_ENTRIES.items():
        assert title and isinstance(title, str)
        assert len(facts) >= 2, f"{key} should have more than one fact to rotate through"
        assert all(isinstance(f, str) and f for f in facts)


def _session_with_gold():
    session, _ = engine.new_game("Historian", Race.HUMAN, CharacterClass.WARRIOR)
    session.player = replace(session.player, gold=5000)
    return session


def test_unlock_chronicle_shows_first_fact_and_marks_discovered():
    session = _session_with_gold()
    log = Log()
    commands._unlock_chronicle(session, log, world_history_lore.ARCHIMEDES_KEY)
    assert world_history_lore.ARCHIMEDES_KEY in session.chronicle_discovered
    assert log.lines[0][1] == world_history_lore.ARCHIMEDES_FACTS[0]
    assert any("New chronicle entry" in text for _, text in log.lines)


def test_unlock_chronicle_is_idempotent_after_first_discovery():
    session = _session_with_gold()
    log = Log()
    commands._unlock_chronicle(session, log, world_history_lore.ARCHIMEDES_KEY)
    log2 = Log()
    commands._unlock_chronicle(session, log2, world_history_lore.ARCHIMEDES_KEY)
    assert not any("New chronicle entry" in text for _, text in log2.lines), "shouldn't announce a 'new' entry twice"


def test_print_chronicle_lists_discovered_entries():
    session = _session_with_gold()
    log = Log()
    commands.print_chronicle(session, log)
    assert any("empty" in text.lower() for _, text in log.lines)

    commands._unlock_chronicle(session, log, world_history_lore.VIKING_KEY)
    log2 = Log()
    commands.print_chronicle(session, log2)
    assert any(world_history_lore.VIKING_TITLE in text for _, text in log2.lines)


def test_archimedes_can_be_discovered_via_boat_repair():
    session = _session_with_gold()
    sea_port = next(loc for loc in session.world.locations.values() if loc.biome == Biome.SEA and loc.population_tier != PopulationTier.WILDERNESS)
    session.discover(sea_port.id)
    session.location_id = sea_port.id
    boat = boat_generator.buy(random.Random(1))

    found = False
    for seed in range(100):
        session.rng = random.Random(seed)
        session.player = replace(session.player, owned_boat=replace(boat, current_durability=1))  # re-damage every time -- a fully-repaired boat short-circuits repair_boat()
        session.chronicle_discovered = set()
        log = Log()
        commands.repair_boat(session, log)
        if world_history_lore.ARCHIMEDES_KEY in session.chronicle_discovered:
            found = True
            break
    assert found, "Archimedes chronicle entry should be reachable through repeated boat repairs"


def test_library_of_alexandria_discovered_via_ancient_scholar():
    session = _session_with_gold()
    scholar_loc = next(loc for loc in session.world.locations.values() if any(b.name == "Ancient Scholar" for b in loc.beings))
    session.discover(scholar_loc.id)
    session.location_id = scholar_loc.id
    log = Log()
    commands.talk(session, log, "ancient scholar")
    assert world_history_lore.LIBRARY_KEY in session.chronicle_discovered


def test_ada_lovelace_reachable_via_enchanting():
    session = _session_with_gold()
    session.player = replace(
        session.player,
        skills={**session.player.skills, SkillType.ENCHANTING: Skill(SkillType.ENCHANTING, 20)},
    )
    found = False
    for seed in range(60):
        session.rng = random.Random(seed)
        session.player = replace(session.player, materials={"Raw Gemstone": 5})
        session.chronicle_discovered = set()
        log = Log()
        commands.craft(session, log, "enchanting")
        if world_history_lore.LOVELACE_KEY in session.chronicle_discovered:
            found = True
            break
    assert found, "Ada Lovelace chronicle entry should be reachable through repeated enchanting"


def test_antikythera_discovered_from_sunken_treasure():
    session = _session_with_gold()
    treasure_loc = next(
        (loc for loc in session.world.locations.values() if any(i.kind == ItemKind.TRINKET and i.is_legendary and i.value > 0 for i in loc.items)),
        None,
    )
    assert treasure_loc is not None, "world generation should always place at least one sunken treasure"
    session.discover(treasure_loc.id)
    session.location_id = treasure_loc.id
    treasure_item = next(i for i in treasure_loc.items if i.kind == ItemKind.TRINKET and i.is_legendary and i.value > 0)
    log = Log()
    commands.take(session, log, treasure_item.name)
    assert world_history_lore.ANTIKYTHERA_KEY in session.chronicle_discovered


def test_leif_erikson_reachable_via_sailing():
    session = _session_with_gold()
    sea_ports = [loc for loc in session.world.locations.values() if loc.biome == Biome.SEA and loc.population_tier != PopulationTier.WILDERNESS]
    a, b = sea_ports[0], sea_ports[1]
    session.discover(a.id)
    session.discover(b.id)

    found = False
    for seed in range(500):
        session.location_id = a.id  # sail() short-circuits with "already there" if not reset each try
        session.rng = random.Random(seed)
        session.player = replace(session.player, owned_boat=boat_generator.buy(session.rng))
        session.chronicle_discovered = set()
        log = Log()
        commands.sail(session, log, b.name.split()[0])
        if world_history_lore.VIKING_KEY in session.chronicle_discovered:
            found = True
            break
    assert found, "Leif Erikson chronicle entry should be reachable through repeated sailing"


def test_chronicle_survives_snapshot_round_trip():
    session = _session_with_gold()
    log = Log()
    commands._unlock_chronicle(session, log, world_history_lore.LOVELACE_KEY)
    snap = session.snapshot()

    session2 = _session_with_gold()
    session2.restore_from(snap)
    assert session2.chronicle_discovered == {world_history_lore.LOVELACE_KEY}


def test_chronicle_command_is_wired_into_engine():
    session = _session_with_gold()
    log = engine.execute_command(session, "chronicle-test", "chronicle")
    assert any("chronicle" in text.lower() or "empty" in text.lower() for _, text in log.lines)
