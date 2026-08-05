"""Top-level orchestration: new-game/continue-game setup and the per-command entry point.

Ported from Game.kt's main()/runGameLoop(), minus the console-specific bits
(numbered race/class prompts, blocking stdin) which the web layer replaces
with a structured character-creation request and one command per HTTP call.
"""
from __future__ import annotations

import random
import time

from eldoria.game import commands
from eldoria.game.commands import Log
from eldoria.game.session import GameSession
from eldoria.models import Biome, CharacterClass, PopulationTier, Race
from eldoria.world import save_manager
from eldoria.world.player_character_factory import create as create_player
from eldoria.world.world_config import WorldConfig
from eldoria.world.world_generator import generate as generate_world

AUTOSAVE_INTERVAL_MILLIS = 10 * 60 * 1000

_world_cache: dict[int, object] = {}
_last_autosave_millis: dict[str, int] = {}

INTRO_TEXT = (
    "As a child, you were taken from your family -- stolen away by the Kingdom's own nobles, in defiance of\n"
    "the king's law, for fear that you would grow strong enough to threaten their soft, cowardly grip on\n"
    "power. Now an adult, you set out across the Kingdom of Eldoria to find the family they tore from you."
)


def _now_millis() -> int:
    return int(time.time() * 1000)


def _world_for_seed(seed: int):
    """Worlds are pure functions of their seed, so cache them across sessions -- generation takes a few seconds."""
    if seed not in _world_cache:
        _world_cache[seed] = generate_world(WorldConfig(seed=seed))
    return _world_cache[seed]


def _start_location(world):
    plains_cities = [loc for loc in world.locations.values() if loc.biome == Biome.PLAINS and loc.population_tier == PopulationTier.CITY]
    if plains_cities:
        return min(plains_cities, key=lambda loc: loc.id)
    return next(loc for loc in world.locations.values() if loc.population_tier == PopulationTier.CITY)


def new_game(name: str, race: Race, character_class: CharacterClass, seed: int | None = None) -> tuple[GameSession, Log]:
    world = _world_for_seed(seed if seed is not None else WorldConfig().seed)
    creation_rng = random.Random()
    player = create_player(name.strip() or "Wanderer", race, character_class, creation_rng)

    start_location = _start_location(world)
    session = GameSession(world, player, start_location.id, start_location.id, random.Random())
    session.discover(start_location.id)

    log = Log()
    log.bold("=== ELDORIA ===")
    log.dim("Developed by Matthew Aaron Davis in cooperation with Claude CLI. Inspired by Achaea, Dreams of Divine Lands (achaea.com). (c) 2026 Matthew Aaron Davis.")
    log.dim(INTRO_TEXT)
    log.plain("\nA text-scroll RPG. Type 'help' any time for the command list.\n")
    log.bold(player.name)
    log.plain(
        f" the {race.display_name} {character_class.display_name} awakens in "
    )
    log.yellow(start_location.name)
    log.plain(f"Wielding {player.equipped_weapon.name if player.equipped_weapon else 'nothing'}, "
               f"wearing {player.equipped_armor.name if player.equipped_armor else 'nothing'}. {player.gold}g in your pouch.\n")
    commands.describe_location(session, log)
    return session, log


def continue_game(session_id: str) -> tuple[GameSession, Log] | None:
    snap = save_manager.load(session_id)
    if snap is None:
        return None
    world = _world_for_seed(snap.seed)
    session = GameSession(world, snap.player, snap.location_id, snap.home_location_id, random.Random())
    session.restore_from(snap)
    log = Log()
    log.plain(f"\nWelcome back, {session.player.name}.")
    commands.describe_location(session, log)
    return session, log


def _maybe_autosave(session: GameSession, session_id: str) -> None:
    now = _now_millis()
    if session_id not in _last_autosave_millis:
        # First command of this session -- matches Kotlin's lastAutosaveMillis being
        # initialized to "now" at loop start, not zero (which would autosave immediately).
        _last_autosave_millis[session_id] = now
        return
    last = _last_autosave_millis[session_id]
    if now - last >= AUTOSAVE_INTERVAL_MILLIS:
        save_manager.save(session_id, session.snapshot())
        _last_autosave_millis[session_id] = now


def execute_command(session: GameSession, session_id: str, raw_input: str) -> Log:
    """One command in, one styled response log out -- the web-facing equivalent of one runGameLoop iteration."""
    session.advance_tick()
    log = Log()
    commands.check_companion_expiry(session, log)
    commands.check_property_events(session, log)
    commands.check_business_events(session, log)
    _maybe_autosave(session, session_id)

    text = raw_input.strip()
    if not text:
        return log
    parts = text.split(None, 1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("quit", "q"):
        log.plain(f"Farewell, {session.player.name}.")
    elif cmd in ("help", "?"):
        commands.print_help(log)
    elif cmd in ("look", "l"):
        commands.describe_location(session, log)
    elif cmd in ("map", "m"):
        from eldoria.game.map_renderer import render as render_map
        log.plain(render_map(session))
    elif cmd in ("character", "c", "sheet"):
        from eldoria.game.character_panel import render as render_character
        log.plain(render_character(session.player))
    elif cmd in ("inventory", "inv", "i"):
        from eldoria.game.character_panel import render_inventory
        log.plain(render_inventory(session.player))
    elif cmd in ("journal", "quests"):
        commands.print_journal(session, log)
    elif cmd in ("codex", "bestiary"):
        commands.print_codex(session, log)
    elif cmd in ("chronicle", "history"):
        commands.print_chronicle(session, log)
    elif cmd in ("north", "n", "south", "s", "east", "e", "west", "w", "up", "down"):
        commands.move(session, log, commands.canonical_direction(cmd))
    elif cmd == "go":
        commands.move(session, log, arg)
    elif cmd in ("enter", "descend"):
        commands.enter_portal(session, log)
    elif cmd in ("leave", "surface"):
        commands.leave_sub_realm(session, log)
    elif cmd == "talk":
        commands.talk(session, log, arg)
    elif cmd in ("train", "learn"):
        commands.train(session, log, arg)
    elif cmd in ("attack", "fight"):
        commands.attack(session, log, arg)
    elif cmd in ("take", "get"):
        commands.take(session, log, arg)
    elif cmd in ("equip", "wear", "wield"):
        commands.equip(session, log, arg)
    elif cmd == "craft":
        commands.craft(session, log, arg)
    elif cmd == "perk":
        commands.choose_perk(session, log, arg)
    elif cmd == "rest":
        commands.rest(session, log)
    elif cmd == "sleep":
        commands.sleep(session, log, session_id)
    elif cmd == "hire":
        if arg.lower() == "manager":
            commands.hire_manager(session, log)
        else:
            commands.hire_companion(session, log)
    elif cmd == "fire":
        commands.fire_manager(session, log)
    elif cmd in ("shop", "trade"):
        commands.open_shop(session, log)
    elif cmd == "buy":
        if arg.lower() == "boat":
            commands.buy_boat(session, log)
        elif arg.lower() == "cannons":
            commands.buy_cannons(session, log)
        elif arg.lower() in ("house", "property"):
            commands.buy_house(session, log)
        elif arg.lower() in ("reckoning", "blade", "banker's reckoning"):
            commands.buy_bankers_reckoning(session, log)
        else:
            commands.buy(session, log, arg)
    elif cmd == "sell":
        commands.sell(session, log, arg)
    elif cmd == "travel":
        commands.travel(session, log, arg)
    elif cmd == "sail":
        commands.sail(session, log, arg)
    elif cmd == "boat":
        commands.boat_status(session, log)
    elif cmd == "repair":
        if arg.lower() in ("house", "property"):
            commands.repair_house(session, log)
        else:
            commands.repair_boat(session, log)
    elif cmd == "ferry":
        commands.accept_ferry(session, log, arg)
    elif cmd in ("ride", "fly"):
        commands.ride_balloon(session, log, arg)
    elif cmd in ("bank",):
        commands.bank_status(session, log)
    elif cmd == "deposit":
        commands.deposit(session, log, arg)
    elif cmd == "withdraw":
        commands.withdraw(session, log, arg)
    elif cmd in ("property", "properties"):
        commands.list_properties(session, log)
    elif cmd in ("business", "businesses", "ventures"):
        commands.list_businesses(session, log)
    elif cmd == "invest":
        commands.invest_in_business(session, log, arg)
    elif cmd == "start":
        commands.found_business(session, log, arg)
    elif cmd == "gamble":
        commands.gamble(session, log, arg)
    elif cmd == "fence":
        commands.fence_item(session, log, arg)
    elif cmd in ("prompt", "vitals"):
        commands.print_prompt(session, log)
    elif cmd == "resolve":
        commands.resolve_side_quest(session, log, arg)
    elif cmd == "request":
        commands.request_subclass(session, log, arg)
    elif cmd == "upgrade":
        commands.request_bionic_upgrade(session, log, arg)
    elif cmd == "confront":
        commands.final_battle(session, log)
    elif cmd == "accept":
        commands.accept_prompt(session, log, arg)
    elif cmd == "decline":
        commands.decline_prompt(session, log, arg)
    else:
        log.plain("Not sure what you mean. Type 'help' for commands.")

    if not session.player.is_alive:
        commands.handle_death(session, log, session_id)

    return log
