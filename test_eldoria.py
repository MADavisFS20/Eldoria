"""Test suite for the Eldoria RPG. Run from any cwd: python test_eldoria.py

Save files are written to a throwaway temp directory so the real
savegame.pkl in the project directory is never touched.
"""
import os
import sys
import subprocess
import tempfile
from collections import deque

GAME_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GAME_DIR)
os.chdir(tempfile.mkdtemp(prefix="eldoria_test_"))

# Silence the typing effect and make output deterministic
from rpg_game import utils
utils.set_debug_mode(True)

import rpg_game.player as player_mod
import rpg_game.combat as combat_mod
import rpg_game.shop as shop_mod
import rpg_game.game as game_mod
import rpg_game.world as world_mod
import rpg_game.quests as quests_mod

from rpg_game.classes import ALL_CLASSES, WARRIOR, MAGE, NECROMANCER
from rpg_game.player import Player
from rpg_game.items import (
    RING_OF_HEALTH, AMULET_OF_MANA, AMULET_OF_STAMINA, STEEL_GREATSWORD,
    WOODEN_SHIELD, HEALTH_POTION_S, SHIP_MANIFEST, GLOWING_MUSHROOM, WAR_AXE,
)
from rpg_game.combat import Enemy, GOBLIN, GIANT_TOAD, STONE_GOLEM, start_combat, _process_enemy_status
from rpg_game.spells import DRAIN_LIFE, FROSTBITE, FIREBALL
from rpg_game.quests import ALL_QUESTS, reset_quests, get_quest_state, set_quest_state
from rpg_game.world import WORLD_MAP, reset_world, get_world_state, set_world_state
from rpg_game.shop import Shop

PASS = 0
FAIL = 0
FAILURES = []

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL: {name} {detail}")

class FakeInput:
    """Deque-backed replacement for utils.get_input / press_enter / input."""
    def __init__(self, answers):
        self.answers = deque(answers)
    def __call__(self, prompt, valid=None):
        if not self.answers:
            raise AssertionError(f"Ran out of scripted answers at prompt: {prompt!r}")
        ans = self.answers.popleft()
        if valid and ans not in [v.lower() for v in valid]:
            raise AssertionError(f"Scripted answer {ans!r} not in valid options {valid}")
        return ans

def noop(*a, **k):
    pass

# Patch pause/clear everywhere they were imported by name
for mod in (player_mod, combat_mod, shop_mod, game_mod, world_mod):
    if hasattr(mod, "press_enter_to_continue"):
        mod.press_enter_to_continue = noop
    if hasattr(mod, "clear_screen"):
        mod.clear_screen = noop

# ---------- 1. Player creation for every class ----------
for key, cls in ALL_CLASSES.items():
    p = Player(name="T", player_class=cls)
    check(f"class {cls.name} creation", p.max_health > 0 and p.current_health == p.max_health)
    check(f"class {cls.name} starting weapon equipped", p.equipment["weapon"] is cls.starting_weapon)

# ---------- 2. Accessory bonuses now apply ----------
p = Player(name="T", player_class=WARRIOR)
base_hp, base_mp, base_sp = p.max_health, p.max_magicka, p.max_stamina
p.inventory.extend([RING_OF_HEALTH, AMULET_OF_MANA, AMULET_OF_STAMINA])
p.equip(RING_OF_HEALTH, silent=True)
p.equip(AMULET_OF_MANA, silent=True)
check("ring of vitality +30 HP", p.max_health == base_hp + 30, f"{p.max_health} vs {base_hp}+30")
check("amulet of arcana +40 MP", p.max_magicka == base_mp + 40)
p.equip(AMULET_OF_STAMINA, silent=True)  # replaces the mana amulet (same slot)
check("amulet of vigor +30 SP", p.max_stamina == base_sp + 30)
check("swapped amulet removes old bonus", p.max_magicka == base_mp)
check("current HP clamped to max", p.current_health <= p.max_health)

# ---------- 3. Two-handed weapon rules ----------
p = Player(name="T", player_class=WARRIOR)  # has iron sword + wooden shield
p.inventory.append(STEEL_GREATSWORD)
p.equip(STEEL_GREATSWORD, silent=True)
check("2H weapon unequips offhand", p.equipment["offhand"] is None)
check("old shield back in inventory", WOODEN_SHIELD in p.inventory)
p.equip(WOODEN_SHIELD, silent=True)
check("offhand blocked while wielding 2H", p.equipment["offhand"] is None)

# ---------- 4. spend_perk_points no longer crashes (clear_screen import) ----------
p = Player(name="T", player_class=WARRIOR)
p.perk_points = 2
player_mod.get_input = FakeInput(["1", "back"])
builtin_input = __builtins__.input if hasattr(__builtins__, "input") else input
import builtins
builtins_input_orig = builtins.input
builtins.input = lambda *a: ""
try:
    p.spend_perk_points()
finally:
    builtins.input = builtins_input_orig
check("perk point spent", p.perks["critical_strike"] == 1 and p.perk_points == 1)

# ---------- 5. Attribute points spendable ----------
p = Player(name="T", player_class=WARRIOR)
p.attribute_points = 2
old_con = p.constitution
old_hp = p.max_health
player_mod.get_input = FakeInput(["4", "back"])  # 4 = constitution
p.spend_attribute_points()
check("attribute point raises CON", p.constitution == old_con + 1)
check("max HP grows with CON", p.max_health == old_hp + 12)
check("one attribute point left", p.attribute_points == 1)

# ---------- 6. Level-up ----------
p = Player(name="T", player_class=WARRIOR)
p.add_experience(250)  # 100 to L2, then 140 to L3 -> 250 gives L3 with 10 left
check("level up math", p.level == 3 and p.experience == 10, f"lvl={p.level} exp={p.experience}")
check("points granted", p.attribute_points == 6 and p.perk_points == 2)

# ---------- 7. Drain Life works in combat ----------
import copy as _copy
p = Player(name="Necro", player_class=NECROMANCER)
p.current_health = 50  # hurt so drain heal is visible
enemy = _copy.deepcopy(GOBLIN)
combat_mod.get_input = FakeInput(["magic", "1"])
mp_before = p.current_magicka
defeated, name = start_combat(p, enemy)
check("drain kills goblin in one cast", not enemy.is_alive(), f"enemy hp={enemy.current_health}")
check("drain costs magicka", p.current_magicka < mp_before)
check("drain heals caster", p.current_health > 50, f"hp={p.current_health}")
check("combat returns not-defeated", defeated is False)

# ---------- 8. Status effects ----------
e = _copy.deepcopy(GOBLIN)
check("freeze applies to goblin", e.apply_status("freeze"))
skipped = _process_enemy_status(e)
check("frozen enemy skips turn", skipped is True)
e2 = _copy.deepcopy(GIANT_TOAD)
check("toad resists burn", e2.apply_status("burn") is False)
e3 = _copy.deepcopy(STONE_GOLEM)
check("golem resists poison", e3.apply_status("poison") is False)
e4 = _copy.deepcopy(GOBLIN)
e4.apply_status("burn")
hp_before = e4.current_health
_process_enemy_status(e4)
check("burn ticks damage", e4.current_health == hp_before - 5)

# ---------- 9. Perk effects in combat ----------
p = Player(name="Mage", player_class=MAGE)
p.perks["mana_efficiency"] = 5   # fireball cost 20 -> 10
p.perks["spell_power"] = 2       # +10 power
enemy = _copy.deepcopy(STONE_GOLEM)
combat_mod.get_input = FakeInput(["magic", "1", "run"])  # cast fireball once then flee
import random as _random
_random.seed(1)  # make the flee roll deterministic-ish; retry loop below handles failure
combat_mod.get_input = FakeInput(["magic", "1"] + ["run"] * 20)
mp_before = p.current_magicka
start_combat(p, enemy)
spent = mp_before - p.current_magicka
check("mana efficiency reduces cost", spent == 10, f"spent={spent}")
# fireball power 30 + int16*2 + perk10 = 72; golem def 20 -> 52 damage, plus burn resisted (golem)
check("spell power perk adds damage", enemy.current_health <= 150 - 52, f"hp={enemy.current_health}")

# ---------- 10. Quests: required items, reset, state roundtrip ----------
reset_quests()
q = ALL_QUESTS["alchemical_fungi"]
p = Player(name="T", player_class=WARRIOR)
q.activate(1)
check("fungi quest now has requirements", q.required_items.get(GLOWING_MUSHROOM) == 2)
check("incomplete without mushrooms", q.complete(p) is False)
p.inventory.extend([GLOWING_MUSHROOM, GLOWING_MUSHROOM])
check("completes with 2 mushrooms", q.complete(p) is True)
check("mushrooms consumed", p.inventory.count(GLOWING_MUSHROOM) == 0)
state = get_quest_state()
check("quest state captured", state["alchemical_fungi"]["is_completed"] is True)
reset_quests()
check("reset_quests clears flags", not ALL_QUESTS["alchemical_fungi"].is_completed)
set_quest_state(state)
check("set_quest_state restores", ALL_QUESTS["alchemical_fungi"].is_completed)
reset_quests()

# ---------- 11. World state: reset + roundtrip ----------
reset_world()
caves = WORLD_MAP["shadow_caves"]
check("two mushrooms exist in caves", caves.items.count(GLOWING_MUSHROOM) == 2)
caves.items.clear()
oak_shop = WORLD_MAP["oakhaven_village"].shop
stock_before = len(oak_shop.inventory)
oak_shop.inventory.pop()
snap = get_world_state()
reset_world()
check("reset_world restores ground items", caves.items.count(GLOWING_MUSHROOM) == 2)
check("reset_world restores shop stock", len(oak_shop.inventory) == stock_before)
set_world_state(snap)
check("set_world_state applies snapshot", len(caves.items) == 0 and len(oak_shop.inventory) == stock_before - 1)
reset_world()

# ---------- 12. Orphan quests now have givers ----------
oak = WORLD_MAP["oakhaven_village"]
p = Player(name="T", player_class=WARRIOR)
world_mod.get_input = FakeInput(["elder theron", "no", "no", "yes"])  # decline relic, decline poison, accept goblins
oak.handle_action(p, "talk", {"goblins_defeated": 0})
check("goblin quest acceptable from Theron", ALL_QUESTS["goblin_menace"].is_active)
# retroactive completion when count already >= 3
reset_quests()
world_mod.get_input = FakeInput(["elder theron", "no", "no", "yes"])
oak.handle_action(p, "talk", {"goblins_defeated": 3})
check("goblin quest completes retroactively", ALL_QUESTS["goblin_menace"].is_completed)
reset_quests()
check("Mountain Guide placed in world", "Mountain Guide" in WORLD_MAP["ironstone_foothills"].npcs)
world_mod.get_input = FakeInput(["mountain guide", "no", "yes"])  # decline miner, accept dragon
WORLD_MAP["ironstone_foothills"].handle_action(p, "talk", {})
check("dragon quest acceptable from Guide", ALL_QUESTS["slay_the_wyrm"].is_active)
reset_quests()
world_mod.get_input = FakeInput(["arcane vendor", "yes"])
WORLD_MAP["sunken_citadel"].handle_action(p, "talk", {})
check("fungi quest acceptable from Vendor", ALL_QUESTS["alchemical_fungi"].is_active)
reset_quests()

# ---------- 13. Dragon kill completes quest ----------
ALL_QUESTS["slay_the_wyrm"].is_active = True
p = Player(name="T", player_class=WARRIOR)
p.strength = 500  # one-shot the dragon
peak = WORLD_MAP["dragons_peak"]
combat_mod.get_input = FakeInput(["attack"] * 30)
_real_random_mod = world_mod.random
world_mod.random = type("R", (), {"random": staticmethod(lambda: 0.0)})()  # force the encounter
try:
    res = peak.check_for_encounter(p, {})
finally:
    world_mod.random = _real_random_mod
check("check_for_encounter returns 3-tuple", len(res) == 3)
check("dragon slain completes quest", ALL_QUESTS["slay_the_wyrm"].is_completed)
reset_quests()

# ---------- 14. Shop: buy, sell, quest-item protection ----------
shop = Shop("Test Shop", [WAR_AXE])
p = Player(name="T", player_class=WARRIOR)
p.gold = 100
p.inventory.append(SHIP_MANIFEST)  # value 0 quest item
shop_mod.get_input = FakeInput(["buy", "1", "sell", "1", "exit"])
shop.enter_shop(p)
check("bought war axe", WAR_AXE in p.inventory and p.gold == 20)
check("quest item not sellable", SHIP_MANIFEST in p.inventory)

# ---------- 15. Save / load roundtrip (in test dir, not the game dir) ----------
game_mod.get_input = FakeInput([])  # save_game takes no input
g = game_mod.Game()
g.player = Player(name="Saver", player_class=MAGE)
g.player.gold = 777
g.current_location_key = "coastal_town"
g.game_state = {"goblins_defeated": 2}
ALL_QUESTS["lost_cargo"].is_active = True
WORLD_MAP["shadow_caves"].items.clear()
g.save_game()
check("savegame.pkl written", os.path.exists("savegame.pkl"))
# scramble state, then load
reset_quests()
reset_world()
g2 = game_mod.Game()
g2.game_loop = noop  # don't enter the loop
g2.load_game()
check("player restored", g2.player.name == "Saver" and g2.player.gold == 777)
check("location restored", g2.current_location_key == "coastal_town")
check("game_state restored", g2.game_state.get("goblins_defeated") == 2)
check("quest state restored", ALL_QUESTS["lost_cargo"].is_active)
check("world state restored", len(WORLD_MAP["shadow_caves"].items) == 0)
reset_quests()
reset_world()

# ---------- 16. AI engine disabled gracefully without key ----------
env_key = os.environ.pop("GEMINI_API_KEY", None)
from rpg_game.ai_engine import AIEngine
ai = AIEngine()
check("AI disabled without key", ai.enabled is False)
check("AI generate returns None when disabled", ai.generate_backstory("a", "b", "c") is None)
if env_key:
    os.environ["GEMINI_API_KEY"] = env_key

# ---------- 17. End-to-end subprocess smoke test ----------
e2e_input = (
    "4\n\n"            # enable debug mode (fast output) + press enter
    "1\nTester\n1\n\n"  # new game, name, warrior, press enter
    "look\n\n"
    "stats\n\n"
    "inventory\n\n"
    "equip\n\n"        # no equippable items -> message + enter
    "use\n\n"          # no potions -> message + enter
    "talk\nelder theron\nno\nno\nno\n\n"  # decline all three quests + final enter
    "save\n\n"
    "quit\n"
    "5\n"
)
env = dict(os.environ)
env.pop("GEMINI_API_KEY", None)
r = subprocess.run(
    [sys.executable, os.path.join(GAME_DIR, "main.py")],
    input=e2e_input, capture_output=True, text=True, timeout=60,
    cwd=os.getcwd(), env=env,
)
check("E2E new game exits cleanly", r.returncode == 0, f"rc={r.returncode} stderr={r.stderr[-500:]}")
out = r.stdout
check("E2E shows village", "Oakhaven Village" in out)
check("E2E shows character sheet", "CHARACTER SHEET: TESTER" in out)
check("E2E talk works", "Elder Theron" in out)
check("E2E save works", "Game saved" in out)
check("E2E farewell", "Farewell, adventurer." in out)

# E2E load test (uses the save written above)
e2e_load = "4\n\n2\n\nlook\n\nquit\n5\n"
r2 = subprocess.run(
    [sys.executable, os.path.join(GAME_DIR, "main.py")],
    input=e2e_load, capture_output=True, text=True, timeout=60,
    cwd=os.getcwd(), env=env,
)
check("E2E load exits cleanly", r2.returncode == 0, f"rc={r2.returncode} stderr={r2.stderr[-500:]}")
check("E2E load succeeds", "Game save loaded successfully" in r2.stdout)

print(f"\n{'='*40}\nRESULTS: {PASS} passed, {FAIL} failed")
for f in FAILURES:
    print(f"  - {f}")
sys.exit(1 if FAIL else 0)
