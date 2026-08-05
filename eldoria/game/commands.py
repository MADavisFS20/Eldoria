"""The game's verbs -- ported from the console engine's Game.kt.

Every command function takes (session, log, arg) and appends styled lines to
`log` instead of printing to stdout, so a single call maps cleanly onto one
web request/response. The original's blocking yes/no quest-accept prompt
(inside handle_home_region_npc) becomes an explicit two-step flow: the offer
is logged and `session.pending_prompt` is set, and a later 'accept'/'decline'
command (see accept_prompt/decline_prompt) resolves it.
"""
from __future__ import annotations

import time
from dataclasses import replace

from eldoria.data import ai_companion_lore, biome_content, crafting_material_content, dialogue_content, family_content, finance_lore, home_region_content, skill_trainer_content, world_history_lore
from eldoria.game.session import GameSession, SubRealmPosition
from eldoria.models import (
    ArtifactKind,
    Biome,
    Business,
    DiceFormula,
    DieType,
    Disposition,
    GameLocation,
    HiredCompanion,
    Item,
    ItemKind,
    Perk,
    PlayerCharacter,
    PopulationTier,
    RealmKind,
    RentalProperty,
    SideQuestKind,
    SkillType,
    SpawnKind,
    StatBlock,
    TerrainKind,
)
from eldoria.world import bank, boat_generator, business as business_gen, crime as crime_gen, level_progression, perk_effects, real_estate, shop_generator, skill_progression
from eldoria.world import stat_generator as sg

MAIN_QUEST_ID = "MAIN_QUEST_FAMILY"
BIONIC_UPGRADE_COST = 75
CANNON_COST = 150
BIG_KAHOONA_NAME = "Big Kahoon-a"
PIRATE_SHIP_NAMES = ["The Black Gull", "Crimson Tide Raider", "The Drowned Fang", "Widow's Wake"]
COMPANION_LINES = [
    "\"Good to have company on a road like this,\" they say.",
    "\"Been a while since I trusted someone at my back this much.\"",
    "\"Wherever you're headed, I'm in. Been enjoying this more than I expected.\"",
    "\"Don't go getting yourself killed. I'd have to explain that back home.\"",
]
BANKER_RECKONING_NAME = "Banker's Reckoning"
BANKER_RECKONING_COST = 500
BANKER_RECKONING_MAX_STREAK = 5
"""Damage doubles per consecutive hit, capped at 2^5 = 32x -- even compound growth hits a real-world ceiling eventually."""


def _now_millis() -> int:
    return int(time.time() * 1000)


class Log:
    """Accumulates styled lines for one command's response (replaces Game.kt's say()/AnsiText combo)."""

    def __init__(self):
        self.lines: list[tuple[str, str]] = []

    def _add(self, style: str, text: str) -> None:
        self.lines.append((style, text))

    def plain(self, text: str) -> None:
        self._add("plain", text)

    def white(self, text: str) -> None:
        self._add("white", text)

    def yellow(self, text: str) -> None:
        self._add("yellow", text)

    def red(self, text: str) -> None:
        self._add("red", text)

    def blue(self, text: str) -> None:
        self._add("blue", text)

    def cyan(self, text: str) -> None:
        self._add("cyan", text)

    def green(self, text: str) -> None:
        self._add("green", text)

    def bold(self, text: str) -> None:
        self._add("bold", text)

    def dim(self, text: str) -> None:
        self._add("dim", text)


def _list_minus_unique(items: tuple, to_remove) -> tuple:
    """Mirrors Kotlin's `list - iterable`: removes the first occurrence of each *unique* value in to_remove."""
    result = list(items)
    seen = []
    for e in to_remove:
        if e in seen:
            continue
        seen.append(e)
        if e in result:
            result.remove(e)
    return tuple(result)


def _remove_one(items: tuple, item) -> tuple:
    result = list(items)
    if item in result:
        result.remove(item)
    return tuple(result)


def canonical_direction(cmd: str) -> str:
    return {"n": "north", "s": "south", "e": "east", "w": "west"}.get(cmd, cmd)


def weapon_skill_for(item: Item | None) -> SkillType:
    if item is None:
        return SkillType.UNARMED
    n = item.name.lower()
    if "bow" in n:
        return SkillType.ARCHERY
    if "staff" in n or "mace" in n:
        return SkillType.ONE_HANDED
    if "great" in n or "maul" in n or "warhammer" in n:
        return SkillType.TWO_HANDED
    return SkillType.ONE_HANDED


def apply_item_bonus(player: PlayerCharacter, item: Item, sign: int) -> PlayerCharacter:
    """Adds (sign=1) or removes (sign=-1) an equipped item's passive bonus."""
    p = player
    if item.armor_class_bonus is not None:
        p = replace(p, armor_class=p.armor_class + item.armor_class_bonus * sign)
    if item.magic_effect is not None:
        effect = item.magic_effect
        delta = effect.magnitude * (1 if effect.beneficial else -1) * sign
        trait = effect.affected_trait
        if trait == "strength":
            p = replace(p, strength=p.strength + delta)
        elif trait == "agility":
            p = replace(p, agility=p.agility + delta)
        elif trait == "willpower":
            p = replace(p, willpower=p.willpower + delta)
        elif trait == "armorClass":
            p = replace(p, armor_class=p.armor_class + delta)
        elif trait == "speed":
            p = replace(p, speed=p.speed + delta)
    return p


_EQUIPPABLE_KINDS = {ItemKind.WEAPON, ItemKind.ARMOR, ItemKind.OFFHAND, ItemKind.HEAD, ItemKind.RING, ItemKind.AMULET}


def is_clear_of_hostiles(beings) -> bool:
    return not any(b.disposition == Disposition.HOSTILE for b in beings)


def buy_discount_percent(player: PlayerCharacter) -> int:
    return (15 if Perk.MASTER_TRADER in player.perks else 0) + (20 if ArtifactKind.COERCION_DEVICE in player.artifacts else 0)


def sell_bonus_percent(player: PlayerCharacter) -> int:
    return (25 if Perk.MASTER_TRADER in player.perks else 0) + (20 if ArtifactKind.COERCION_DEVICE in player.artifacts else 0)


def is_sea_port(session: GameSession) -> bool:
    return session.current_location.biome == Biome.SEA and session.current_location.population_tier != PopulationTier.WILDERNESS


def broker_hint(session: GameSession) -> str:
    family_loc = next((loc for loc in session.world.locations.values() if any(b.is_family_member for b in loc.beings)), None)
    family_biome = family_loc.biome.display_name if family_loc else None
    hints = [h for h in [
        f"Word is a certain someone you've been looking for is somewhere in the {family_biome}." if family_biome else None,
        "There's a homeless tinkerer in one of the cities who'll bolt something remarkable onto you, for a price.",
        "Sailors mutter about something enormous in the deep sea -- the Big Kahoon-a, they call it. Best have a strong boat, and better cannons.",
        "Not every curse is a bad trade. Ask around the wilder corners of the Kingdom if you're feeling reckless -- a bite or a bargain, your pick.",
        "Rivers cut clean through this Kingdom now. A boat gets you across, or so I hear, something stranger might too.",
    ] if h is not None]
    return session.rng.choice(hints)


def find_being(session: GameSession, query: str):
    if not query.strip():
        return None
    q = query.lower()
    for i, b in session.current_beings():
        if q in b.name.lower():
            return (i, b)
    return None


# --- Location / movement ---------------------------------------------------

def describe_location(session: GameSession, log: Log) -> None:
    session.discover(session.location_id)
    room = session.current_room()
    if room is not None:
        log.bold(room.name)
        log.white(room.description)
        log.white("Exits: " + ", ".join(room.exits.keys()))
    else:
        loc = session.current_location
        log.bold(loc.name)
        log.white(loc.description)
        log.white("Exits: " + ", ".join(loc.exits.keys()))
        if loc.portal_id is not None:
            kind = "dungeon entrance" if loc.portal_kind == RealmKind.DUNGEON else "beanstalk into the sky"
            log.white(f"There is a {kind} here. (enter)")

    beings = session.current_beings()
    if beings:
        log.plain("You see:")
        for _, b in beings:
            session.record_seen(b.name)
            if b.disposition == Disposition.HOSTILE:
                label = ("red", f"{b.name} [hostile]")
            elif b.kind == SpawnKind.NPC:
                label = ("blue", b.name)
            else:
                label = ("white", b.name)
            trainer_tag = f" (trainer: {b.teaches_skill.display_name})" if b.teaches_skill is not None else ""
            family_tag = " (something about them feels familiar...)" if (b.is_family_member and MAIN_QUEST_ID not in session.completed_quests) else ""
            companion_tag = " (will travel with you, for a price -- 'hire')" if b.offers_companionship else ""
            log.lines.append((label[0], f"  - {label[1]}{trainer_tag}{family_tag}{companion_tag}"))

    items = session.current_items()
    if items:
        log.plain("Items here:")
        for _, item in items:
            log.yellow(f"  - {item.name}")

    if session.player.companion is not None:
        log.cyan(f"{session.player.companion.name} is at your side.")


def resolve_hazard(session: GameSession, log: Log, dest: GameLocation) -> None:
    """Natural dangers are a survivable AGI check on arrival, not a monster fight."""
    hazard = dest.hazard
    if hazard is None:
        return
    log.red(f"\n{hazard.display_name}: {hazard.encounter_line}")
    agi_mod = StatBlock.modifier_of(session.player.agility)
    roll = sg.attack_roll(session.rng, agi_mod)
    dc = 10 + dest.difficulty_tier
    if roll >= dc:
        log.white(hazard.avoid_line)
        return
    log.red(hazard.fail_line)
    if hazard.hits_gear:
        wear_amount = session.rng.randint(2, 5)
        boat = session.player.owned_boat
        if dest.terrain == TerrainKind.WATERWAY and boat is not None:
            session.player = replace(session.player, owned_boat=boat.worn(wear_amount))
            log.dim("Your boat takes the worst of it.")
        elif session.player.equipped_armor is not None:
            session.player = replace(session.player, equipped_armor=session.player.equipped_armor.worn(wear_amount))
            log.dim("Your armor takes the worst of it.")
        else:
            dmg = max(1, DiceFormula(dest.difficulty_tier, DieType.D6, 0).roll(session.rng))
            session.player = replace(session.player, current_health=session.player.current_health - dmg)
            log.dim(f"You take {dmg} damage.")
    else:
        dmg = max(1, DiceFormula(dest.difficulty_tier, DieType.D6, 0).roll(session.rng))
        session.player = replace(session.player, current_health=session.player.current_health - dmg)
        log.dim(f"You take {dmg} damage.")


def maybe_street_crime(session: GameSession, log: Log) -> None:
    """The rougher, lower-tier parts of town carry real robbery risk if you're flush with cash on hand."""
    loc = session.current_location
    if loc.population_tier == PopulationTier.WILDERNESS or loc.difficulty_tier > 2:
        return
    stolen = crime_gen.maybe_rob_player(session.player.gold, session.rng)
    if stolen <= 0:
        return
    session.player = replace(session.player, gold=session.player.gold - stolen)
    log.red(f"\nA quick hand brushes past you in the crowd -- {stolen}g gone before you even feel it. This part of town has a reputation for a reason.")
    log.dim("(Gold on hand is what's at risk on the street -- gold in the bank isn't. That's a real reason people bank more than they carry.)")


def gamble(session: GameSession, log: Log, arg: str) -> None:
    """An illegal back-room game, found only in the wealthier, higher-tier cities."""
    loc = session.current_location
    if loc.population_tier != PopulationTier.CITY or loc.difficulty_tier < 3:
        log.plain("There's no gambling den here -- word is the back-room games run in the bigger, wealthier cities.")
        return
    amount = int(arg) if arg.strip().isdigit() else None
    if amount is None or amount <= 0:
        log.plain("gamble <amount> -- how much are you willing to risk?")
        return
    if session.player.gold < amount:
        log.plain(f"You don't have {amount}g on hand to wager.")
        return
    won, delta = crime_gen.gamble(amount, session.rng)
    session.player = replace(session.player, gold=session.player.gold + delta, reputation=max(-100, min(100, session.player.reputation - 1)))
    if won:
        log.yellow(f"The cards fall your way -- you win {amount}g!")
    else:
        log.red(f"The house wins again -- you lose {amount}g.")
    log.dim(f"(Illegal, and rigged in the house's favor by design -- an {crime_gen.GAMBLING_HOUSE_EDGE_PERCENT}% house edge means the longer you play, the more certain the house comes out ahead. Gambling isn't an investment strategy.)")


def fence_item(session: GameSession, log: Log, arg: str) -> None:
    """A black-market fence in wealthier cities -- moves suspect goods for a steep cut, no questions asked."""
    loc = session.current_location
    if loc.population_tier != PopulationTier.CITY or loc.difficulty_tier < 3:
        log.plain("No one here deals in that sort of business.")
        return
    item = next((i for i in session.player.inventory if arg.lower() in i.name.lower()), None)
    if item is None:
        log.plain("You don't have that.")
        return
    p = session.player
    if item in (p.equipped_weapon, p.equipped_armor, p.equipped_offhand, p.equipped_head, p.equipped_ring, p.equipped_amulet):
        log.plain("You can't fence what you have equipped.")
        return
    price = crime_gen.fence_price(item.value)
    session.player = replace(session.player, gold=session.player.gold + price, inventory=_remove_one(session.player.inventory, item), reputation=max(-100, min(100, session.player.reputation - 2)))
    log.yellow(f"The fence turns {item.name} over once, names a price of {price}g, and doesn't ask where it came from.")
    log.dim("(Well under honest market value -- moving goods through someone who doesn't ask questions always costs a steep cut. That's the real price of 'no questions asked.')")


def _maybe_ai_biome_narration(session: GameSession, log: Log, previous_biome, dest) -> None:
    """Mr. Davis's invisible AI companion narrates real-world facts on the wind whenever the biome changes -- but only after you've met him."""
    if not session.met_time_traveler:
        return
    if previous_biome == dest.biome:
        return
    facts = ai_companion_lore.AI_BIOME_LINES.get(dest.biome)
    if not facts:
        return
    log.cyan(f"\n(a voice rides the wind, flat and toneless) {session.rng.choice(facts)}")


TIME_TRAVELER_INTERCEPT_MAX_MOVES = 10
"""Mr. Davis is guaranteed to intercept every player by their 10th move, if they haven't met him some other way first."""


def maybe_time_traveler_intercept(session: GameSession, log: Log) -> None:
    if session.met_time_traveler:
        return
    if session.move_count >= TIME_TRAVELER_INTERCEPT_MAX_MOVES or session.rng.randrange(100) < 20:
        log.plain("")
        log.dim("A man falls into step beside you, seemingly from nowhere.")
        _deliver_mr_davis_first_meeting(session, log)


def move(session: GameSession, log: Log, direction: str) -> None:
    room = session.current_room()
    if room is not None:
        dest_id = room.exits.get(direction)
        if dest_id is None:
            log.plain("You can't go that way.")
            return
        session.sub_realm_position = SubRealmPosition(session.sub_realm_position.sub_realm_id, dest_id)
        describe_location(session, log)
        return

    loc = session.current_location
    dest_id = loc.exits.get(direction)
    if dest_id is None:
        log.plain("You can't go that way.")
        return
    dest = session.world.locations[dest_id]

    if dest.terrain == TerrainKind.WATERWAY and not session.player.has_gills:
        boat = session.player.owned_boat
        if boat is None:
            log.white("Deep water blocks your path here. You'd need a boat, or find a bridge.")
            return
        if boat.is_broken:
            log.white("The water blocks your path, and your wrecked boat won't carry you across.")
            return
        session.player = replace(session.player, owned_boat=boat.worn(session.rng.randint(1, 2)))
        if session.player.owned_boat.is_broken:
            log.red("Your boat groans and takes on water -- it won't survive much more of this.")
    elif dest.terrain == TerrainKind.WATERWAY:
        log.cyan("You slip beneath the surface and swim across effortlessly, gills flaring in the current.")

    previous_biome = loc.biome
    session.record_overworld_departure(session.location_id)
    session.location_id = dest_id
    session.discover(dest_id)
    session.move_count += 1
    describe_location(session, log)
    _maybe_ai_biome_narration(session, log, previous_biome, dest)
    resolve_hazard(session, log, dest)
    maybe_street_crime(session, log)
    maybe_ferry_encounter(session, log, dest)
    maybe_balloon_encounter(session, log, dest)
    maybe_time_traveler_intercept(session, log)


def enter_portal(session: GameSession, log: Log) -> None:
    if session.in_sub_realm:
        log.plain("You're already inside.")
        return
    loc = session.current_location
    sub_realm_id = loc.portal_id
    if sub_realm_id is None:
        log.plain("There's nothing to enter here.")
        return
    realm = session.world.sub_realms[sub_realm_id]
    session.sub_realm_position = SubRealmPosition(realm.id, realm.entry_room_id)
    session.discovered_quests.add(realm.id)
    log.bold(f"You enter {realm.name}.")
    log.white(f"Quest: {realm.quest.objective}")
    log.dim(dialogue_content.quest_flavor_line(realm.quest.type, session.rng))
    describe_location(session, log)


def leave_sub_realm(session: GameSession, log: Log) -> None:
    realm = session.current_sub_realm()
    if realm is None:
        log.plain("You're not inside anywhere you can leave.")
        return
    session.record_sub_realm_departure(realm)
    session.sub_realm_position = None
    log.white(f"You climb back out into {session.current_location.name}.")
    describe_location(session, log)


# --- Home region NPC dialogue trees -----------------------------------------

def _consume_items(session: GameSession, name: str, count: int) -> bool:
    matching = [i for i in session.player.inventory if i.name == name]
    if len(matching) < count:
        return False
    session.player = replace(session.player, inventory=_list_minus_unique(session.player.inventory, matching[:count]))
    return True


def _offer_home_region_quest(session: GameSession, log: Log, quest_id: str, hook_line: str) -> None:
    log.blue(f"\"{hook_line}\"")
    if session.pending_prompt is not None:
        return  # only one offer pending at a time -- see module docstring
    log.dim(f"(type 'accept' or 'decline' -- {home_region_content.QUEST_TITLES[quest_id]})")
    session.pending_prompt = {"type": "home_region_quest", "quest_id": quest_id}


def _complete_home_region_quest(session: GameSession, log: Log, quest_id: str, xp: int, gold: int, line: str) -> None:
    session.active_home_region_quests.discard(quest_id)
    session.completed_side_quests.add(quest_id)
    session.player = level_progression.apply_experience(replace(session.player, gold=session.player.gold + gold), xp, session.rng)
    log.blue(f"\"{line}\"")
    log.bold(f"[QUEST COMPLETE]: {home_region_content.QUEST_TITLES[quest_id]} (+{xp} XP, +{gold}g)")


def accept_prompt(session: GameSession, log: Log, arg: str) -> None:
    prompt = session.pending_prompt
    if prompt is None or prompt.get("type") != "home_region_quest":
        log.plain("There's nothing to accept right now.")
        return
    quest_id = prompt["quest_id"]
    session.pending_prompt = None
    session.active_home_region_quests.add(quest_id)
    log.bold(f"[QUEST ACCEPTED]: {home_region_content.QUEST_TITLES[quest_id]}")


def decline_prompt(session: GameSession, log: Log, arg: str) -> None:
    prompt = session.pending_prompt
    if prompt is None:
        log.plain("There's nothing to decline right now.")
        return
    session.pending_prompt = None
    log.dim("You decide against it, for now.")


def _deliver_mr_davis_first_meeting(session: GameSession, log: Log) -> None:
    """Shared by both the manual 'talk mr. davis' path and the proactive intercept within the first 10 moves."""
    for style, text in ai_companion_lore.MR_DAVIS_FIRST_MEETING:
        getattr(log, style)(text)
    session.met_time_traveler = True
    log.dim("(You'll hear that voice again, out on the wind, whenever you cross into unfamiliar country.)")


def _handle_home_region_npc(session: GameSession, log: Log, being) -> bool:
    hrc = home_region_content
    name = being.name

    if name == hrc.ELDER_THERON:
        log.blue(f"You approach {being.name}.")
        relic = hrc.QUEST_ANCIENT_RELIC
        if relic in session.completed_side_quests:
            pass
        elif relic in session.active_home_region_quests:
            if _consume_items(session, hrc.ITEM_ANCIENT_RELIC, 1):
                _complete_home_region_quest(session, log, relic, 150, 100, "You have returned the relic! Oakhaven is safer thanks to you, hero.")
            else:
                log.blue("\"Have you found the ancient relic yet? The village depends on it.\"")
        else:
            _offer_home_region_quest(session, log, relic, "The Whispering Woods hide an ancient relic, vital to our village's protection. Will you seek it out?")

        poison = hrc.QUEST_POISONED_WATERS
        if poison in session.completed_side_quests:
            pass
        elif poison in session.active_home_region_quests:
            if _consume_items(session, hrc.ITEM_SWAMP_HERB, hrc.SWAMP_HERB_REQUIRED):
                _complete_home_region_quest(session, log, poison, 180, 120, "Excellent! These herbs will surely help. Thank you, adventurer.")
            else:
                log.blue("\"The waters still run foul. Have you found enough Swamp Herbs yet?\"")
        else:
            _offer_home_region_quest(session, log, poison, f"Our water supply from the swamps has become tainted. If you could gather {hrc.SWAMP_HERB_REQUIRED} Swamp Herbs, it might help purify it.")

        goblins = hrc.QUEST_GOBLIN_OUTBREAK
        goblins_slain = session.quest_counters.get("Goblin Scavenger", 0)
        if goblins in session.completed_side_quests:
            pass
        elif goblins in session.active_home_region_quests:
            if goblins_slain >= hrc.GOBLINS_REQUIRED:
                _complete_home_region_quest(session, log, goblins, 120, 80, "The roads are safer already. You have our thanks, goblin-slayer.")
            else:
                log.blue(f"\"The goblins still prowl. {hrc.GOBLINS_REQUIRED - goblins_slain} more must fall.\"")
        else:
            _offer_home_region_quest(session, log, goblins, f"Goblins have been raiding the roads and woods. Cull at least {hrc.GOBLINS_REQUIRED} of them and Oakhaven will reward you.")
        return True

    if name == hrc.FISHERMAN_FINN:
        log.blue(f"You approach {being.name}.")
        cargo = hrc.QUEST_LOST_CARGO
        if cargo in session.completed_side_quests:
            log.blue("\"Bless yer soul, still keeping the coast safe, are ye?\"")
        elif cargo in session.active_home_region_quests:
            if _consume_items(session, hrc.ITEM_SHIP_MANIFEST, 1):
                _complete_home_region_quest(session, log, cargo, 250, 150, "Bless yer soul! Me manifest! Now I can sort out this mess. Here's a little something for yer trouble.")
            else:
                log.blue("\"Any luck with me manifest, eh? It's down in that sunken wreck, I reckon.\"")
        else:
            _offer_home_region_quest(session, log, cargo, "Me cargo, lost in the shipwreck! If ye could find me manifest, I'd be mighty grateful.")
        return True

    if name == hrc.MOUNTAIN_GUIDE:
        log.blue(f"You approach {being.name}.")
        rescue = hrc.QUEST_MOUNTAIN_RESCUE
        if rescue in session.completed_side_quests:
            pass
        elif rescue in session.active_home_region_quests:
            if _consume_items(session, hrc.ITEM_LOST_MINER_NOTE, 1):
                _complete_home_region_quest(session, log, rescue, 300, 200, "A note from poor old Borin... at least we know what happened. Thank you for bringing closure.")
            else:
                log.blue("\"Still no sign of the lost miner? Be careful up there, it's treacherous.\"")
        else:
            _offer_home_region_quest(session, log, rescue, "A miner went missing in the northern pass. If you find him, or at least a note from him, I'd pay handsomely.")

        dragon = hrc.QUEST_SLAY_THE_WYRM
        if dragon in session.completed_side_quests:
            pass
        elif dragon in session.active_home_region_quests:
            log.blue("\"The wyrm still lives -- I can see its smoke from here. Take the pass up to the peak, and gods be with you.\"")
        else:
            _offer_home_region_quest(session, log, dragon, "An ancient dragon slumbers atop Dragon's Peak. Slay it, and your name will be sung for generations. Few return from that summit...")
        return True

    if name == hrc.ARCANE_VENDOR:
        log.blue(f"You approach {being.name}.")
        fungi = hrc.QUEST_ALCHEMICAL_FUNGI
        if fungi in session.completed_side_quests:
            log.blue("\"Our transaction was complete. Was there something else?\"")
        elif fungi in session.active_home_region_quests:
            if _consume_items(session, hrc.ITEM_GLOWING_MUSHROOM, hrc.GLOWING_MUSHROOM_REQUIRED):
                _complete_home_region_quest(session, log, fungi, 100, 60, "Ahh, they still glow with cave-light. Perfect. Our transaction is complete.")
            else:
                log.blue("\"No mushrooms yet? The Shadow Caves lie west of here.\"")
        else:
            _offer_home_region_quest(session, log, fungi, f"I require reagents... Glowing Mushrooms from the Shadow Caves. Bring me {hrc.GLOWING_MUSHROOM_REQUIRED} and I shall make it worth your while.")
        return True

    if name == hrc.ANCIENT_SCHOLAR:
        log.blue(f"You approach {being.name}.")
        compass = hrc.QUEST_ANCIENT_COMPASS
        if compass in session.completed_side_quests:
            pass
        elif compass in session.active_home_region_quests:
            if _consume_items(session, hrc.ITEM_ANCIENT_COMPASS, 1):
                _complete_home_region_quest(session, log, compass, 400, 300, "Incredible! The Ancient Compass! Its magic is palpable. You have done a great service!")
            else:
                log.blue("\"The compass... it must be here somewhere. Keep searching the crypts.\"")
        else:
            _offer_home_region_quest(session, log, compass, "The legends speak of an Ancient Compass, hidden deep within these ruins. It holds immense power. Will you brave the dangers to find it?")
        _unlock_chronicle(session, log, world_history_lore.LIBRARY_KEY)
        return True

    if name == hrc.LOST_MINER:
        log.blue(f"You approach {being.name}.")
        rescue = hrc.QUEST_MOUNTAIN_RESCUE
        if rescue in session.active_home_region_quests and rescue not in session.completed_side_quests:
            log.blue("\"Oh, thank the heavens! I'm trapped! I dropped my note somewhere nearby, please take it to the guide in the south!\"")
            if not any(i.name == hrc.ITEM_LOST_MINER_NOTE for i in session.player.inventory):
                note = Item(name=hrc.ITEM_LOST_MINER_NOTE, kind=ItemKind.QUEST_ITEM, tier=1, value=0, max_durability=1)
                session.player = replace(session.player, inventory=session.player.inventory + (note,))
                log.yellow(f"You received the {hrc.ITEM_LOST_MINER_NOTE}.")
        else:
            log.blue("\"Just need to rest a bit... then I'll try to find my way out.\"")
        return True

    if name == ai_companion_lore.MR_DAVIS_NAME:
        if session.met_time_traveler:
            log.blue(session.rng.choice(ai_companion_lore.MR_DAVIS_REPEAT))
        else:
            _deliver_mr_davis_first_meeting(session, log)
        return True

    return False


# --- Talk / train ------------------------------------------------------------

def talk(session: GameSession, log: Log, arg: str) -> None:
    companion = session.player.companion
    if companion is not None and arg.strip() and arg.lower() in companion.name.lower():
        log.cyan(session.rng.choice(COMPANION_LINES))
        return
    found = find_being(session, arg)
    if found is None:
        log.plain("There's no one here by that name.")
        return
    _, being = found
    if being.disposition == Disposition.HOSTILE:
        log.plain(dialogue_content.hostile_line(being.name, session.rng))
        if ArtifactKind.TELEPATH_DEVICE in session.player.artifacts:
            log.cyan(f"You brush against their surface thoughts: roughly {being.stats.max_health} health, armor rated about {being.stats.armor_class}.")
        return
    if being.is_rescue_captive:
        log.blue(dialogue_content.captive_rescue_line(being.name, session.rng))
        return
    if _handle_home_region_npc(session, log, being):
        return
    if being.is_family_member:
        if MAIN_QUEST_ID in session.completed_quests:
            log.blue("\"Every day you're still here is a good day,\" they say, smiling.")
            return
        log.bold(session.rng.choice(family_content.REUNION_LINES).replace("{name}", being.name))
        session.completed_quests.add(MAIN_QUEST_ID)
        rep_delta = 25
        session.player = replace(session.player, reputation=max(-100, min(100, session.player.reputation + rep_delta)))
        log.bold("MAIN QUEST COMPLETE: after all these years, you've found your family.")
        log.dim("Your reputation rises -- word travels fast of the stolen child who came home.")
        check_endgame_trigger(session, log)
        return
    trainer = None
    if being.teaches_skill is not None:
        trainer = next((t for t in skill_trainer_content.all_trainers() if t.name == being.name), None)
    if trainer is not None:
        log.blue(trainer.greeting)
        if not session.player.knows_skill(trainer.skill):
            log.blue(trainer.teach_offer)
            log.dim(f" (type 'train {trainer.skill.display_name.lower()}')")
        else:
            log.dim(f"(You already know {trainer.skill.display_name}.)")
        return
    if being.offers_subclass is not None:
        offer = being.offers_subclass
        if session.player.subclass == offer:
            log.dim(f"You already carry {offer.display_name}'s curse. There's nothing more they can give you.")
        elif session.player.subclass is not None:
            log.blue(f"\"{offer.display_name}'s curse and your own don't mix,\" they say, almost pitying. \"You made your choice already.\"")
        else:
            weakness = offer.weakness_description
            weakness = weakness[:1].lower() + weakness[1:] if weakness else weakness
            log.blue(f"\"You want what I have,\" they say, studying you. \"{offer.strength_description} But know this -- {weakness}\"")
            log.dim(f"(type 'request {offer.name.lower()}' to accept -- this cannot be undone, and you can never take the other path)")
        return
    if being.offers_bionic_upgrade:
        if session.player.bionic_upgrade_used:
            log.blue("\"Only got the one working rig, friend. Already used yours.\"")
        else:
            log.blue(
                "\"Heh heh -- steel, ore, and a bit of GENIUS, that's all it takes!\" the old man cackles, tapping a crude "
                "bionic contraption strapped to his own arm. \"Modest price, and I'll wire one basic ability of yours up "
                "PAST what nature gave you. Strength, quickness, or wits -- your choice, permanent, +5. One customer, one rig, no refunds!\""
            )
            log.dim(f"(type 'upgrade strength', 'upgrade agility', or 'upgrade willpower' for {BIONIC_UPGRADE_COST}g)")
        return
    if being.offers_side_quest is not None:
        quest = being.offers_side_quest
        if quest.name in session.completed_side_quests:
            log.blue("\"Good on you for helping, back there,\" they say, with the easy warmth of someone who still remembers what you did.")
        else:
            log.bold(quest.title)
            log.blue(quest.hook_line)
            for r in quest.resolutions:
                log.dim(f"  (type 'resolve {r.keyword}' -- {r.label})")
        return
    loc_name = (session.current_room().name if session.current_room() else session.current_location.name)
    biome = session.current_sub_realm().biome if session.current_sub_realm() else session.current_location.biome
    log.blue(dialogue_content.civilian_line(being.name, loc_name, biome, session.rng))
    if ArtifactKind.TELEPATH_DEVICE in session.player.artifacts:
        log.cyan(f"You catch their surface thoughts: {dialogue_content.telepathy_line(session.rng)}")


def train(session: GameSession, log: Log, arg: str) -> None:
    trainer_being = next((b for _, b in session.current_beings() if b.teaches_skill is not None), None)
    if trainer_being is None:
        log.plain("No one here can train you.")
        return
    trainer = next(t for t in skill_trainer_content.all_trainers() if t.name == trainer_being.name)
    if session.player.knows_skill(trainer.skill):
        log.plain(f"You already know {trainer.skill.display_name}.")
        return
    session.player = skill_progression.learn_skill_from_trainer(session.player, trainer.skill)
    log.blue(trainer.teach_offer)
    log.bold(f"You have learned {trainer.skill.display_name}! (starting level {session.player.skill_level(trainer.skill)})")
    log.dim("(In the old tongue of Achaea's tutors, this first taste of a skill was called a 'lesson' -- mastery from here on is earned through use, not bought.)")


# --- Side quests --------------------------------------------------------------

def _fight_arena_gauntlet(session: GameSession, log: Log) -> bool:
    """Three back-to-back bouts against generated pit fighters, difficulty rising with the city's tier."""
    tier = max(1, session.current_location.difficulty_tier)
    for round_num in range(1, 4):
        foe_name = f"Pit Fighter {session.rng.choice(['Grimjaw', 'Blackscar', 'Ironhide', 'Stonefist'])}"
        foe_stats = sg.creature_stats(min(5, tier + round_num - 1), session.rng)
        log.red(f"\nBout {round_num}: {foe_name} steps into the pit.")
        foe_hp = foe_stats.max_health
        combat_round = 0
        while foe_hp > 0 and session.player.is_alive and combat_round < 20:
            combat_round += 1
            player_roll = sg.attack_roll(session.rng, session.player.attack_bonus)
            if sg.is_hit(player_roll, foe_stats.armor_class):
                weapon = session.player.equipped_weapon
                dmg = max(1, (weapon.damage if weapon else session.player.unarmed_damage).roll(session.rng))
                foe_hp -= dmg
                log.plain(f"  You hit {foe_name} for {dmg} damage.")
            else:
                log.dim(f"  You miss {foe_name}.")
            if foe_hp <= 0:
                break
            foe_roll = sg.attack_roll(session.rng, foe_stats.attack_bonus)
            if sg.is_hit(foe_roll, session.player.armor_class):
                dmg = max(1, foe_stats.damage.roll(session.rng))
                session.player = replace(session.player, current_health=session.player.current_health - dmg)
                log.red(f"  {foe_name} hits you for {dmg} damage.")
            else:
                log.dim(f"  {foe_name} misses.")
        if not session.player.is_alive:
            handle_death(session, log)
            return False
        if foe_hp > 0:
            return False
        log.bold(f"  {foe_name} goes down!")
    return True


def resolve_side_quest(session: GameSession, log: Log, arg: str) -> None:
    being = next((b for _, b in session.current_beings() if b.offers_side_quest is not None), None)
    if being is None:
        log.plain("There's no one here with unfinished business for you.")
        return
    quest = being.offers_side_quest
    if quest.name in session.completed_side_quests:
        log.plain(f"You've already settled things with {being.name}.")
        return
    resolution = next((r for r in quest.resolutions if r.keyword.lower() == arg.lower()), None)
    if resolution is None:
        log.plain("That's not one of the choices " + being.name + " gave you. Options: " + ", ".join(r.keyword for r in quest.resolutions))
        return

    if quest == SideQuestKind.UNDERGROUND_DICE_DEN:
        if session.player.gold < 20:
            log.plain("You need 20g on hand to sit at this table.")
            return
        roll = DiceFormula(1, DieType.D20).roll(session.rng)
        won = roll >= 11
        session.player = replace(session.player, gold=session.player.gold + (20 if won else -20))
        log.bold(f"The die shows {roll}. " + ("You win -- the table groans as the gambler pays out double." if won else "You lose -- the gambler sweeps your coin away without a flicker of sympathy."))
        session.completed_side_quests.add(quest.name)
    elif quest == SideQuestKind.THE_COLLECTOR:
        positive = [(k, v) for k, v in session.player.materials.items() if v > 0]
        if not positive:
            log.plain("\"Come back when you've actually got something interesting on you,\" the collector sighs.")
            return
        material_key, material_value = max(positive, key=lambda kv: kv[1])
        payout = session.rng.randint(30, 80)
        new_materials = dict(session.player.materials)
        new_materials[material_key] = material_value - 1
        session.player = replace(session.player, materials=new_materials, gold=session.player.gold + payout)
        log.bold(f"The collector pays {payout}g for your {material_key}, practically vibrating with excitement.")
        session.completed_side_quests.add(quest.name)
    elif quest == SideQuestKind.THE_BROKER:
        if session.player.gold < 20:
            log.plain("\"Twenty gold, or don't waste my time,\" the broker says flatly.")
            return
        hint = broker_hint(session)
        session.player = replace(session.player, gold=session.player.gold - 20)
        log.bold(f"The broker leans in close: \"{hint}\"")
        session.completed_side_quests.add(quest.name)
    elif quest == SideQuestKind.UNDERGROUND_ARENA:
        won = _fight_arena_gauntlet(session, log)
        if not session.player.is_alive:
            return
        if won:
            session.player = replace(
                session.player,
                reputation=max(-100, min(100, session.player.reputation + resolution.reputation_delta)),
                gold=session.player.gold + resolution.gold_delta,
            )
            log.bold(resolution.outcome_line)
            session.completed_side_quests.add(quest.name)
        else:
            log.red("You're beaten before the gauntlet's done. The pit boss shrugs and shows you the door -- no shame in it, but no purse either.")
    else:
        if resolution.gold_delta < 0 and session.player.gold + resolution.gold_delta < 0:
            log.plain(f"You can't afford that right now ({-resolution.gold_delta}g needed).")
            return
        session.player = replace(
            session.player,
            reputation=max(-100, min(100, session.player.reputation + resolution.reputation_delta)),
            gold=session.player.gold + resolution.gold_delta,
        )
        if resolution.material_reward is not None:
            new_materials = dict(session.player.materials)
            mat = resolution.material_reward
            new_materials[mat] = new_materials.get(mat, 0) + 1
            session.player = replace(session.player, materials=new_materials)
        log.bold(resolution.outcome_line)
        session.completed_side_quests.add(quest.name)


def request_subclass(session: GameSession, log: Log, arg: str) -> None:
    """Vampire or Werewolf -- permanent, one-time, and mutually exclusive."""
    giver = next((b for _, b in session.current_beings() if b.offers_subclass is not None), None)
    if giver is None:
        log.plain("No one here can offer you that.")
        return
    offer = giver.offers_subclass
    if offer.name.lower() not in arg.lower() and arg.strip() and arg.lower() not in offer.display_name.lower():
        log.plain(f"Ask them plainly -- 'request {offer.display_name.lower()}'.")
        return
    if session.player.subclass == offer:
        log.plain("You already carry that curse.")
        return
    if session.player.subclass is not None:
        log.plain(f"You've already given yourself to {session.player.subclass.display_name}'s curse -- there's no room for another.")
        return

    session.player = replace(
        session.player,
        subclass=offer,
        strength=session.player.strength + offer.strength_bonus,
        agility=session.player.agility + offer.agility_bonus,
        willpower=session.player.willpower + offer.willpower_bonus,
        max_health=max(1, session.player.max_health + offer.max_health_bonus),
        current_health=max(1, session.player.current_health + offer.max_health_bonus),
        armor_class=session.player.armor_class + offer.armor_class_bonus,
    )
    log.bold(offer.lore)
    log.bold(f"You are now a {offer.display_name}.")
    log.dim(f"Strength: {offer.strength_description}")
    log.dim(f"Weakness: {offer.weakness_description}")


def request_bionic_upgrade(session: GameSession, log: Log, arg: str) -> None:
    """The Mad Scientist's one-time +5 ability bionic implant -- permanent, once per character."""
    scientist = next((b for _, b in session.current_beings() if b.offers_bionic_upgrade), None)
    if scientist is None:
        log.plain("There's no one here who can do that.")
        return
    if session.player.bionic_upgrade_used:
        log.plain("\"Told you -- one rig, one customer. That's you, already done.\"")
        return
    if session.player.gold < BIONIC_UPGRADE_COST:
        log.plain(f"\"Come back with {BIONIC_UPGRADE_COST}g and we'll talk business.\"")
        return

    a = arg.lower()
    if "str" in a:
        updated = replace(session.player, strength=session.player.strength + 5)
    elif "agi" in a:
        updated = replace(session.player, agility=session.player.agility + 5)
    elif "wil" in a:
        updated = replace(session.player, willpower=session.player.willpower + 5)
    else:
        log.plain("Choose one: 'upgrade strength', 'upgrade agility', or 'upgrade willpower'.")
        return
    session.player = replace(updated, gold=updated.gold - BIONIC_UPGRADE_COST, bionic_upgrade_used=True)
    log.red("Rusty tools whir and spark against your skin -- it hurts more than you expected, then it doesn't hurt at all.")
    log.bold("\"Steel and ore, friend. Steel and ore.\" The bionic upgrade takes hold, permanently.")


# --- Combat -------------------------------------------------------------------

def attack(session: GameSession, log: Log, arg: str) -> None:
    if session.player.companion is not None and arg.strip() and arg.lower() in session.player.companion.name.lower():
        log.plain("You can't attack your own companion.")
        return
    found = find_being(session, arg)
    if found is None:
        log.plain("There's nothing here by that name to fight.")
        return
    index, target = found
    target_hp = target.stats.max_health
    weapon_skill = weapon_skill_for(session.player.equipped_weapon)
    tier = session.current_room().difficulty_tier if session.current_room() else session.current_location.difficulty_tier
    crit_threshold = max(15, 20 - session.player.perk_rank(Perk.CRITICAL_FOCUS))

    target_status = None
    target_status_turns = 0
    compound_streak = 0
    """Consecutive-hit counter for The Banker's Reckoning -- see BANKER_RECKONING_MAX_STREAK's doc."""

    room = session.current_room()
    if target.disposition != Disposition.HOSTILE:
        log.red(f"You raise your weapon against {target.name}! This will not go unnoticed.")
    elif room is not None and room.is_boss_room and target.kind == SpawnKind.CREATURE:
        log.red(dialogue_content.boss_taunt_line(target.name, session.rng))
    else:
        log.red(dialogue_content.hostile_line(target.name, session.rng))

    round_num = 0
    while target_hp > 0 and session.player.is_alive and round_num < 30:
        round_num += 1
        session.player = replace(session.player, current_stamina=max(0, session.player.current_stamina - 1))
        exhausted = session.player.is_exhausted
        exhaustion_penalty = 2 if exhausted else 0
        player_roll = sg.attack_roll_detailed(session.rng, session.player.attack_bonus - exhaustion_penalty, crit_threshold)
        if exhausted and round_num == 1:
            log.dim("  You're exhausted -- your strikes are slower and less sure.")
        if player_roll.is_fumble:
            log.dim("  You fumble badly and swing at nothing. (natural 1)")
            compound_streak = 0
        elif sg.is_hit(player_roll, target.stats.armor_class):
            subclass = session.player.subclass
            rage = subclass.low_health_rage_bonus if (subclass is not None and session.player.current_health * 2 < session.player.max_health) else 0
            weapon = session.player.equipped_weapon
            weapon_damage = weapon.damage if weapon else session.player.unarmed_damage
            base_dmg = sg.critical_damage(weapon_damage, session.rng) if player_roll.is_critical else weapon_damage.roll(session.rng)
            dmg = max(1, base_dmg) + rage
            if weapon is not None and weapon.is_compounding:
                multiplier = 2 ** min(compound_streak, BANKER_RECKONING_MAX_STREAK)
                dmg *= multiplier
                if compound_streak >= BANKER_RECKONING_MAX_STREAK:
                    log.dim(f"  The Reckoning's compounding hits its ceiling at {multiplier}x -- even exponential growth runs into real-world limits eventually.")
                elif compound_streak > 0:
                    log.yellow(f"  The Reckoning compounds: {multiplier}x damage from {compound_streak + 1} consecutive hits.")
                compound_streak += 1
            target_hp -= dmg
            rage_note = f" (rage +{rage})" if rage > 0 else ""
            crit_note = " CRITICAL HIT!" if player_roll.is_critical else ""
            log.plain(f"  You strike {target.name} for {dmg} damage.{rage_note}{crit_note} (roll {player_roll.total} vs AC {target.stats.armor_class})")
            session.player = skill_progression.gain_skill_use(session.player, weapon_skill, session.rng)
            if subclass is not None and subclass.lifesteal_percent > 0:
                healed = max(1, int(dmg * subclass.lifesteal_percent / 100.0))
                new_health = min(session.player.max_health, session.player.current_health + healed)
                session.player = replace(session.player, current_health=new_health)
                log.dim(f"  The wound feeds you -- you recover {healed} health.")
            if weapon is not None and weapon.inflicts_status is not None:
                effect = weapon.inflicts_status
                if effect in target.stats.status_resistances:
                    log.dim(f"  {target.name} resists the {effect.display_name.lower()}.")
                else:
                    target_status = effect
                    target_status_turns = effect.default_turns
                    log.red(f"  {target.name} is afflicted with {effect.display_name}!")
        else:
            log.dim(f"  You swing at {target.name} and miss. (roll {player_roll.total} vs AC {target.stats.armor_class})")
            compound_streak = 0
        if target_hp <= 0:
            break

        comp = session.player.companion
        if comp is not None:
            comp_roll = sg.attack_roll(session.rng, comp.attack_bonus)
            if sg.is_hit(comp_roll, target.stats.armor_class):
                comp_dmg = max(1, comp.damage.roll(session.rng))
                target_hp -= comp_dmg
                log.cyan(f"  {comp.name} strikes {target.name} for {comp_dmg} damage.")
            else:
                log.dim(f"  {comp.name} attacks {target.name} and misses.")
        if target_hp <= 0:
            break

        foe_skips_turn = False
        if target_status is not None:
            status = target_status
            if status.per_turn_damage > 0:
                target_hp -= status.per_turn_damage
                log.red(f"  {target.name} suffers {status.per_turn_damage} {status.display_name.lower()} damage!")
            foe_skips_turn = status.skips_turn
            if foe_skips_turn:
                log.cyan(f"  {target.name} is frozen solid and cannot act!")
            target_status_turns -= 1
            if target_status_turns <= 0:
                log.dim(f"  The {status.display_name.lower()} on {target.name} fades.")
                target_status = None
        if target_hp <= 0:
            break

        if not foe_skips_turn:
            foe_roll = sg.attack_roll_detailed(session.rng, target.stats.attack_bonus)
            if foe_roll.is_fumble:
                log.dim(f"  {target.name} fumbles and misses badly. (natural 1)")
            elif sg.is_hit(foe_roll, session.player.armor_class):
                dmg = sg.critical_damage(target.stats.damage, session.rng) if foe_roll.is_critical else target.stats.damage.roll(session.rng)
                dmg = max(1, dmg)
                if target.stats.magic_damage is not None:
                    dmg += target.stats.magic_damage.roll(session.rng)
                resisted = int(dmg * session.player.race.magic_resistance_percent / 100.0)
                dmg = max(1, dmg - resisted)
                session.player = replace(session.player, current_health=session.player.current_health - dmg)
                crit_note = " CRITICAL HIT!" if foe_roll.is_critical else ""
                log.plain(f"  {target.name} hits you for {dmg} damage.{crit_note} (roll {foe_roll.total} vs your AC {session.player.armor_class})")
            else:
                log.dim(f"  {target.name} attacks and misses. (roll {foe_roll.total} vs your AC {session.player.armor_class})")
        if not session.player.is_alive:
            return

    if target_hp <= 0:
        log.bold(f"You have defeated {target.name}!")
        session.mark_defeated(index, target.name)
        session.increment_quest_counter(target.name)
        if target.name == "Ancient Flame Dragon" and home_region_content.QUEST_SLAY_THE_WYRM in session.active_home_region_quests:
            session.active_home_region_quests.discard(home_region_content.QUEST_SLAY_THE_WYRM)
            session.completed_side_quests.add(home_region_content.QUEST_SLAY_THE_WYRM)
            trophy = Item(name="Dragon Scale Trophy", kind=ItemKind.TRINKET, tier=5, value=750, max_durability=1, is_legendary=True)
            session.player = replace(session.player, inventory=session.player.inventory + (trophy,), gold=session.player.gold + 1000)
            session.player = level_progression.apply_experience(session.player, 1000, session.rng)
            log.bold("[QUEST COMPLETE]: Slay the Wyrm (+1000 XP, +1000g, Dragon Scale Trophy)")
        xp = level_progression.xp_for_defeating(tier, session.rng)
        before = session.player.level
        session.player = level_progression.apply_experience(session.player, xp, session.rng)
        log.plain(f"You gain {xp} experience.")
        if session.player.level > before:
            log.bold(f"You reached level {session.player.level}!")
        if session.player.pending_perk_choices > 0:
            log.cyan("You have a perk choice available! Type 'perk' to choose.")

        rep_delta = session.rng.randint(1, 3) if target.disposition == Disposition.HOSTILE else -20
        session.player = replace(session.player, reputation=max(-100, min(100, session.player.reputation + rep_delta)))
        if rep_delta < 0:
            log.red("Word of this will spread. Your reputation suffers.")

        if target.kind == SpawnKind.CREATURE and target.disposition == Disposition.HOSTILE and session.rng.randrange(100) < 30:
            biome = session.current_sub_realm().biome if session.current_sub_realm() else session.current_location.biome
            material = session.rng.choice(crafting_material_content.materials_for(biome))
            new_materials = dict(session.player.materials)
            new_materials[material.name] = new_materials.get(material.name, 0) + 1
            session.player = replace(session.player, materials=new_materials)
            log.yellow(f"{target.name} dropped: {material.name}")

        realm = session.current_sub_realm()
        if realm is not None:
            boss_room = realm.rooms[realm.boss_room_id]
            room = session.current_room()
            if target in boss_room.beings and room is not None and room.is_boss_room:
                log.bold(f"The way to {realm.quest.title}'s treasures lies open.")


# --- Items / equipment / crafting --------------------------------------------

def take(session: GameSession, log: Log, arg: str) -> None:
    items = session.current_items()
    indexed = next((pair for pair in items if arg.lower() in pair[1].name.lower()), None)
    if indexed is None:
        log.plain("You don't see that here.")
        return
    idx, item = indexed
    session.mark_taken(idx)

    artifact = next((a for a in ArtifactKind if a.item_name == item.name), None)
    if artifact is not None:
        log.bold(artifact.activation_line)
        session.player = replace(
            session.player,
            artifacts=session.player.artifacts | {artifact},
            attack_bonus=session.player.attack_bonus + artifact.attack_bonus,
            armor_class=session.player.armor_class + artifact.armor_class_bonus,
        )
        log.dim(f"({item.name} is now a permanent part of you.)")
        return

    session.player = replace(session.player, inventory=session.player.inventory + (item,))
    log.yellow(f"You take the {item.name}.")
    if item.kind == ItemKind.TRINKET and item.is_legendary and item.value > 0:
        _unlock_chronicle(session, log, world_history_lore.ANTIKYTHERA_KEY)
    realm = session.current_sub_realm()
    room = session.current_room()
    if realm is not None and room is not None and room.is_boss_room and item.name == realm.quest.quest_item.name:
        session.completed_quests.add(realm.id)
        log.bold(f"Quest complete: {realm.quest.title}!")
        rep_delta = session.rng.randint(5, 10)
        session.player = replace(session.player, reputation=max(-100, min(100, session.player.reputation + rep_delta)))
        check_endgame_trigger(session, log)


def equip(session: GameSession, log: Log, arg: str) -> None:
    item = next((i for i in session.player.inventory if arg.lower() in i.name.lower()), None)
    if item is None:
        log.plain("You don't have that.")
        return
    if item.kind not in _EQUIPPABLE_KINDS:
        log.plain("You can't equip that.")
        return

    player = session.player
    previous = player.equipped_in_slot(item.kind)
    if previous is not None:
        player = apply_item_bonus(player, previous, -1)
        player = replace(player, inventory=player.inventory + (previous,))
    player = player.with_equipped_in_slot(item.kind, item)
    player = replace(player, inventory=_remove_one(player.inventory, item))
    player = apply_item_bonus(player, item, 1)

    session.player = player
    swap_note = f" ({previous.name} returned to your pack)" if previous is not None else ""
    log.yellow(f"You equip the {item.name}.{swap_note}")
    if item.magic_effect is not None:
        note = finance_lore.MAGIC_EFFECT_NOTES.get(item.magic_effect.name)
        if note is not None:
            log.cyan(f"  (You sense something of its nature: {note})")


def craft(session: GameSession, log: Log, arg: str) -> None:
    skill = next((s for s in SkillType if s.category.name == "CRAFTING" and arg.lower() in s.display_name.lower()), None)
    if skill is None:
        log.plain("Craft what? Try: blacksmithing, alchemy, enchanting, woodworking, leatherworking.")
        return
    if not session.player.knows_skill(skill):
        log.plain(f"You haven't learned {skill.display_name} yet.")
        return
    material_entry = next(
        ((name, count) for name, count in session.player.materials.items()
         if count >= 2 and any(m.name == name and m.feeds_skill == skill for m in crafting_material_content.all_materials())),
        None,
    )
    if material_entry is None:
        log.plain(f"You need at least 2 of a matching material for {skill.display_name}.")
        return
    material_name, material_count = material_entry

    tier = max(1, min(5, session.player.skill_level(skill) // 20 + 1))
    ore_stripped = material_name.removesuffix("Ore").strip() if material_name.endswith("Ore") else material_name.strip()
    if skill == SkillType.BLACKSMITHING:
        crafted = sg.weapon_item(f"Handforged {ore_stripped} Blade", tier, session.rng)
    elif skill == SkillType.LEATHERWORKING:
        crafted = sg.armor_item(f"Tailored {material_name} Armor", tier, session.rng)
    elif skill == SkillType.ENCHANTING:
        crafted = sg.weapon_item(f"Enchanted {material_name} Charm", tier, session.rng, legendary=True)
    elif skill == SkillType.WOODWORKING:
        crafted = sg.weapon_item(f"Carved {material_name} Bow", tier, session.rng)
    elif skill == SkillType.ALCHEMY:
        crafted = sg.quest_item(f"{material_name} Elixir", tier, session.rng)
    else:
        log.plain("Can't craft that.")
        return

    new_materials = dict(session.player.materials)
    new_materials[material_name] = material_count - 2
    session.player = replace(session.player, materials=new_materials, inventory=session.player.inventory + (crafted,))
    session.player = skill_progression.gain_skill_use(session.player, skill, session.rng)
    log.bold(f"Using {material_name}, you craft: {crafted.name}!")
    log.dim(f"{skill.display_name} is now level {session.player.skill_level(skill)}.")
    if skill == SkillType.ENCHANTING and session.rng.randrange(100) < 30:
        _unlock_chronicle(session, log, world_history_lore.LOVELACE_KEY)


def choose_perk(session: GameSession, log: Log, arg: str) -> None:
    if session.player.pending_perk_choices <= 0:
        log.plain("You have no perk choices banked right now.")
        return
    available = list(Perk)
    choice = int(arg) if arg.strip().lstrip("-").isdigit() else None
    if choice is None or not (1 <= choice <= len(available)):
        log.plain("Choose a perk (type 'perk <number>'):")
        for i, p in enumerate(available):
            rank = session.player.perk_rank(p)
            rank_note = f" (rank {rank})" if rank > 0 else ""
            log.plain(f"  {i + 1}) {p.display_name}{rank_note} -- {p.description}")
        return
    session.player = perk_effects.apply_perk(session.player, available[choice - 1])
    log.bold(f"You gained the perk: {available[choice - 1].display_name}!")


# --- Rest / sleep / companion ------------------------------------------------

def rest(session: GameSession, log: Log) -> None:
    from eldoria.game.session import RESPAWN_DELAY_TICKS
    session.player = replace(session.player, current_health=session.player.max_health, current_stamina=session.player.max_stamina, second_wind_ready=True)
    for _ in range(RESPAWN_DELAY_TICKS):
        session.advance_tick()
    log.white("You rest and recover to full health and stamina. Time passes.")


def sleep(session: GameSession, log: Log, session_id: str) -> None:
    from eldoria.game.session import RESPAWN_DELAY_TICKS
    from eldoria.world import save_manager

    here_clear = is_clear_of_hostiles([b for _, b in session.current_beings()])
    room = session.current_room()
    if room is not None:
        neighbors_clear = all(
            is_clear_of_hostiles((session.current_sub_realm().rooms[room_id].beings if session.current_sub_realm() and room_id in session.current_sub_realm().rooms else []))
            for room_id in room.exits.values()
        )
    else:
        neighbors_clear = all(
            is_clear_of_hostiles(session.world.locations[loc_id].beings if loc_id in session.world.locations else [])
            for loc_id in session.current_location.exits.values()
        )
    if not here_clear or not neighbors_clear:
        log.red("You can't risk sleeping -- there's danger too close by, here or just beyond.")
        return
    session.player = replace(session.player, current_health=session.player.max_health, current_stamina=session.player.max_stamina, second_wind_ready=True)
    for _ in range(RESPAWN_DELAY_TICKS):
        session.advance_tick()
    log.white("You find a safe spot and sleep. You wake with your health and stamina fully restored.")
    save_manager.save(session_id, session.snapshot())
    log.dim("(game saved)")


def hire_companion(session: GameSession, log: Log) -> None:
    if session.player.companion is not None:
        log.plain("You've already got company. They'll wander off eventually.")
        return
    candidate = next((b for _, b in session.current_beings() if b.offers_companionship), None)
    if candidate is None:
        log.plain("No one here is looking for work.")
        return
    cost = session.current_location.difficulty_tier * 25
    if session.player.gold < cost:
        log.plain(f"{candidate.name} wants {cost}g to travel with you -- you're short.")
        return
    session.player = replace(
        session.player,
        gold=session.player.gold - cost,
        companion=HiredCompanion(
            name=candidate.name,
            attack_bonus=candidate.stats.attack_bonus,
            armor_class=candidate.stats.armor_class,
            damage=candidate.stats.damage,
            origin_location_id=session.location_id,
            hired_at_millis=_now_millis(),
        ),
    )
    log.bold(f"{candidate.name} shoulders their gear and falls in beside you. \"Lead the way.\"")


def check_companion_expiry(session: GameSession, log: Log) -> None:
    from eldoria.models import EMPLOYMENT_DURATION_MILLIS

    companion = session.player.companion
    if companion is None:
        return
    if _now_millis() - companion.hired_at_millis >= EMPLOYMENT_DURATION_MILLIS:
        origin = session.world.locations.get(companion.origin_location_id)
        origin_name = origin.name if origin else "home"
        log.dim(f"\n{companion.name} claps you on the shoulder. \"That's my time up -- I'm heading back.\" They turn back toward {origin_name}.")
        session.player = replace(session.player, companion=None)


# --- Shop ---------------------------------------------------------------------

def open_shop(session: GameSession, log: Log) -> None:
    trader = next(
        (b for _, b in session.current_beings() if b.disposition == Disposition.PASSIVE and dialogue_content.archetype_for(b.name) == dialogue_content.NpcArchetype.TRADER),
        None,
    )
    if trader is None:
        log.plain("There's no merchant here.")
        session.last_shop_trader = None
        session.last_shop_stock = []
        return
    stock = shop_generator.inventory_for(trader.name, session.location_id, session.current_location.difficulty_tier, session.world.seed)
    discount = buy_discount_percent(session.player)
    log.blue(f"{trader.name} shows you their wares:")
    for i, it in enumerate(stock):
        log.plain(f"  {i + 1}) {it.name} -- {shop_generator.buy_price(it, discount)}g")
    log.dim("(buy <#> to purchase, sell <#> to sell one of your own items)")
    session.last_shop_trader = trader.name
    session.last_shop_stock = stock


def buy(session: GameSession, log: Log, arg: str) -> None:
    trader_name = session.last_shop_trader
    stock = session.last_shop_stock
    idx = int(arg) if arg.strip().lstrip("-").isdigit() else None
    if trader_name is None or idx is None or not (1 <= idx <= len(stock)):
        log.plain("Open a shop first ('shop'), then buy <#>.")
        return
    item = stock[idx - 1]
    price = shop_generator.buy_price(item, buy_discount_percent(session.player))
    if session.player.gold < price:
        log.plain(f"You can't afford that (need {price}g).")
        return
    session.player = replace(session.player, gold=session.player.gold - price, inventory=session.player.inventory + (item,))
    log.yellow(f"You buy the {item.name} for {price}g.")


def sell(session: GameSession, log: Log, arg: str) -> None:
    if arg.strip().lower() in ("house", "property"):
        sell_house(session, log)
        return
    if arg.strip().lower() in ("business", "venture"):
        sell_business(session, log)
        return
    idx = int(arg) if arg.strip().lstrip("-").isdigit() else None
    if idx is None or not (1 <= idx <= len(session.player.inventory)):
        log.plain("sell <#> -- check 'inventory' for numbers. (or 'sell house' / 'sell business')")
        return
    item = session.player.inventory[idx - 1]
    p = session.player
    if item in (p.equipped_weapon, p.equipped_armor, p.equipped_offhand, p.equipped_head, p.equipped_ring, p.equipped_amulet):
        log.plain("You can't sell what you have equipped.")
        return
    price = shop_generator.sell_back_price(item, sell_bonus_percent(session.player))
    session.player = replace(session.player, gold=session.player.gold + price, inventory=_remove_one(session.player.inventory, item))
    log.yellow(f"You sell the {item.name} for {price}g.")


# --- The Bank: compound interest, an honest side-by-side with simple interest, and the Banker's Reckoning. ---

def bank_status(session: GameSession, log: Log) -> None:
    if session.current_location.population_tier != PopulationTier.CITY:
        log.plain("There's no bank here -- try a city.")
        return
    p = session.player
    new_balance, new_last_tick, compound_gain, simple_gain = bank.settle_interest(p.bank_gold, p.bank_last_interest_tick, session.game_tick)
    if new_last_tick != p.bank_last_interest_tick or new_balance != p.bank_gold:
        session.player = replace(p, bank_gold=new_balance, bank_last_interest_tick=new_last_tick)
        p = session.player
        if compound_gain > 0:
            log.green(f"Interest posts to your account: +{compound_gain}g (compound interest, {bank.RATE_PER_CYCLE * 100:.0f}% per cycle).")
            if compound_gain > simple_gain:
                log.dim(f"  Simple interest over the same stretch would have earned only {simple_gain}g -- compounding earns interest on your interest, not just your original deposit.")
    log.bold(f"Bank of Eldoria -- {session.current_location.name} branch")
    log.plain(f"  On hand: {p.gold}g")
    log.plain(f"  In the bank: {p.bank_gold}g")
    log.dim(f"  ({bank.WITHDRAWAL_FEE_PERCENT}% withdrawal fee -- moving money isn't free, here or anywhere.)")
    log.cyan(session.rng.choice(finance_lore.FINANCE_TIPS))
    if not p.banker_reckoning_purchased:
        log.dim(f"  A ledger on the counter advertises a curious old blade: '{BANKER_RECKONING_NAME}' -- {BANKER_RECKONING_COST}g. ('buy reckoning')")


def deposit(session: GameSession, log: Log, arg: str) -> None:
    if session.current_location.population_tier != PopulationTier.CITY:
        log.plain("There's no bank here -- try a city.")
        return
    amount = int(arg) if arg.strip().isdigit() else None
    if amount is None or amount <= 0:
        log.plain("deposit <amount> -- how much gold do you want to put in the bank?")
        return
    p = session.player
    if p.gold < amount:
        log.plain(f"You don't have {amount}g on hand.")
        return
    new_balance, new_last_tick, _, _ = bank.settle_interest(p.bank_gold, p.bank_last_interest_tick, session.game_tick)
    if p.bank_gold <= 0:
        new_last_tick = session.game_tick  # the compounding clock starts now, not whenever the account last happened to be empty
    session.player = replace(p, gold=p.gold - amount, bank_gold=new_balance + amount, bank_last_interest_tick=new_last_tick)
    log.yellow(f"You deposit {amount}g. Bank balance: {session.player.bank_gold}g.")


def withdraw(session: GameSession, log: Log, arg: str) -> None:
    if session.current_location.population_tier != PopulationTier.CITY:
        log.plain("There's no bank here -- try a city.")
        return
    p = session.player
    new_balance, new_last_tick, _, _ = bank.settle_interest(p.bank_gold, p.bank_last_interest_tick, session.game_tick)
    session.player = replace(p, bank_gold=new_balance, bank_last_interest_tick=new_last_tick)
    amount = int(arg) if arg.strip().isdigit() else None
    if amount is None or amount <= 0:
        log.plain("withdraw <amount> -- how much do you want to take out?")
        return
    if amount > new_balance:
        log.plain(f"You only have {new_balance}g in the bank.")
        return
    fee = bank.withdrawal_fee(amount)
    session.player = replace(session.player, gold=session.player.gold + amount - fee, bank_gold=new_balance - amount)
    log.yellow(f"You withdraw {amount}g. A {fee}g withdrawal fee is deducted -- you pocket {amount - fee}g.")


def buy_bankers_reckoning(session: GameSession, log: Log) -> None:
    if session.current_location.population_tier != PopulationTier.CITY:
        log.plain("There's no bank here -- try a city.")
        return
    if session.player.banker_reckoning_purchased:
        log.plain(f"The bank ledger notes you already own {BANKER_RECKONING_NAME}.")
        return
    if session.player.gold < BANKER_RECKONING_COST:
        log.plain(f"{BANKER_RECKONING_NAME} costs {BANKER_RECKONING_COST}g -- you're short.")
        return
    blade = Item(
        name=BANKER_RECKONING_NAME, kind=ItemKind.WEAPON, tier=3,
        damage=DiceFormula(1, DieType.D4, 1), value=BANKER_RECKONING_COST, max_durability=40,
        is_legendary=True, is_compounding=True,
    )
    session.player = replace(
        session.player, gold=session.player.gold - BANKER_RECKONING_COST,
        inventory=session.player.inventory + (blade,), banker_reckoning_purchased=True,
    )
    log.bold(f"You purchase {BANKER_RECKONING_NAME} for {BANKER_RECKONING_COST}g -- an unassuming old dagger that strikes harder the longer a fight runs.")
    log.dim("(Each consecutive hit on the same foe doubles the last one's damage, up to a point -- a lesson in compounding, and in its limits.)")


# --- Real estate: rental property, tenants good and bad, and honest vacancy risk. ---

def list_properties(session: GameSession, log: Log) -> None:
    if not session.player.owned_properties:
        log.plain("You don't own any property yet. Look for a house to buy in a city or village ('buy house').")
        return
    log.bold("Your properties:")
    for prop in session.player.owned_properties:
        if prop.is_condemned:
            status = "condemned"
        elif prop.is_occupied:
            status = f"rented to {prop.tenant_name}"
        else:
            status = "vacant"
        log.plain(f"  {prop.location_name}: condition {prop.condition}/100, {status}, lifetime rent {prop.lifetime_rent_collected}g")


def buy_house(session: GameSession, log: Log) -> None:
    loc = session.current_location
    if loc.population_tier == PopulationTier.WILDERNESS:
        log.plain("There's no property for sale out in the wilderness.")
        return
    if any(prop.location_id == session.location_id for prop in session.player.owned_properties):
        log.plain("You already own property here.")
        return
    price = real_estate.purchase_price_for(loc.population_tier, loc.difficulty_tier)
    if session.player.gold < price:
        log.plain(f"A house here runs {price}g -- you're short.")
        return
    prop = RentalProperty(location_id=session.location_id, location_name=loc.name, purchase_price=price, last_event_tick=session.game_tick)
    session.player = replace(session.player, gold=session.player.gold - price, owned_properties=session.player.owned_properties + (prop,))
    log.bold(f"You buy a house in {loc.name} for {price}g.")
    log.dim("It's empty for now -- a vacant property earns nothing until a tenant moves in. Check back with 'property'.")


def sell_house(session: GameSession, log: Log) -> None:
    prop = next((p for p in session.player.owned_properties if p.location_id == session.location_id), None)
    if prop is None:
        log.plain("You don't own property here.")
        return
    price = real_estate.sell_price(prop)
    session.player = replace(
        session.player, gold=session.player.gold + price,
        owned_properties=tuple(p for p in session.player.owned_properties if p.location_id != session.location_id),
    )
    log.yellow(f"You sell your house in {prop.location_name} for {price}g.")
    log.dim("A well-kept property holds its value; a neglected one doesn't -- condition mattered.")


def repair_house(session: GameSession, log: Log) -> None:
    prop = next((p for p in session.player.owned_properties if p.location_id == session.location_id), None)
    if prop is None:
        log.plain("You don't own property here.")
        return
    if prop.condition >= 100:
        log.plain("Your property here is already in full repair.")
        return
    cost = real_estate.repair_cost(prop)
    if session.player.gold < cost:
        log.plain(f"Repairs would cost {cost}g -- you can't afford that yet.")
        return
    updated = replace(prop, condition=100, lifetime_repair_spent=prop.lifetime_repair_spent + cost)
    session.player = replace(
        session.player, gold=session.player.gold - cost,
        owned_properties=tuple(updated if p.location_id == session.location_id else p for p in session.player.owned_properties),
    )
    log.yellow(f"You pay {cost}g to fully repair your property in {prop.location_name}.")


def check_property_events(session: GameSession, log: Log) -> None:
    if not session.player.owned_properties:
        return
    updated = []
    for prop in session.player.owned_properties:
        new_prop, lines, gold_delta = real_estate.process_cycle(prop, session.game_tick, session.rng)
        updated.append(new_prop)
        for line in lines:
            if gold_delta > 0:
                log.cyan(line)
            elif gold_delta < 0:
                log.red(line)
            else:
                log.dim(line)
        if gold_delta:
            session.player = replace(session.player, gold=session.player.gold + gold_delta)
    session.player = replace(session.player, owned_properties=tuple(updated))


# --- Business: a passive stake for a share of profit, or founding your own and hiring a manager. ---

def list_businesses(session: GameSession, log: Log) -> None:
    if not session.player.owned_businesses:
        log.plain("You have no stake in any business yet. 'invest <amount>' for a passive share, or 'start <type>' to found your own.")
        return
    log.bold("Your business interests:")
    for biz in session.player.owned_businesses:
        if biz.is_failed:
            log.plain(f"  {biz.name} ({biz.location_name}): failed -- total loss.")
            continue
        if biz.is_fully_owned:
            if not biz.has_manager:
                mgr = "no manager"
            elif biz.manager_revealed:
                mgr = f"managed by {biz.manager_name} ({biz.manager_quality})"
            else:
                mgr = f"managed by {biz.manager_name} (still getting to know them)"
            log.plain(f"  {biz.name} ({biz.location_name}), {biz.business_type}, full owner, {mgr}, lifetime profit {biz.lifetime_profit_collected}g, losses {biz.lifetime_losses}g")
        else:
            log.plain(f"  {biz.name} ({biz.location_name}), {biz.business_type}, {biz.ownership_percent}% stake, lifetime profit {biz.lifetime_profit_collected}g, losses {biz.lifetime_losses}g")


def invest_in_business(session: GameSession, log: Log, arg: str) -> None:
    loc = session.current_location
    if loc.population_tier != PopulationTier.CITY:
        log.plain("There's no established business scene to invest in here -- try a city.")
        return
    amount = int(arg) if arg.strip().isdigit() else None
    if amount is None or amount <= 0:
        log.plain("invest <amount> -- how much gold do you want to put in?")
        return
    if session.player.gold < amount:
        log.plain(f"You don't have {amount}g on hand.")
        return

    existing = next((b for b in session.player.owned_businesses if b.location_id == session.location_id and not b.is_fully_owned), None)
    if existing is not None:
        gained = business_gen.stake_percent_for_investment(amount, existing.ownership_percent)
        if gained <= 0:
            log.plain("You already hold as much of this business as a passive investor is allowed (49%).")
            return
        updated = replace(existing, investment=existing.investment + amount, ownership_percent=existing.ownership_percent + gained)
        session.player = replace(
            session.player, gold=session.player.gold - amount,
            owned_businesses=tuple(updated if b.id == existing.id else b for b in session.player.owned_businesses),
        )
        log.bold(f"You invest another {amount}g in {existing.name}, bringing your stake to {updated.ownership_percent}%.")
        return

    biz_type = session.rng.choice(business_gen.BUSINESS_TYPES)
    name = f"{loc.name} {biz_type}"
    percent = business_gen.stake_percent_for_investment(amount)
    biz = Business(
        id=f"{session.location_id}_stake_{session.game_tick}", location_id=session.location_id,
        location_name=loc.name, name=name, business_type=biz_type, investment=amount,
        ownership_percent=percent, last_event_tick=session.game_tick,
    )
    session.player = replace(session.player, gold=session.player.gold - amount, owned_businesses=session.player.owned_businesses + (biz,))
    log.bold(f"You buy a {percent}% passive stake in {name} for {amount}g.")
    log.dim("You have no say in how it's run -- a passive stake means sharing the profit, and the risk, with zero control.")


def found_business(session: GameSession, log: Log, arg: str) -> None:
    loc = session.current_location
    if loc.population_tier != PopulationTier.CITY:
        log.plain("You can only found a business in a city.")
        return
    if any(b.location_id == session.location_id and b.is_fully_owned for b in session.player.owned_businesses):
        log.plain("You already own a business here.")
        return
    biz_type = next((t for t in business_gen.BUSINESS_TYPES if arg.strip().lower() in t.lower()), None) if arg.strip() else None
    if biz_type is None:
        biz_type = session.rng.choice(business_gen.BUSINESS_TYPES)
    cost = business_gen.founding_cost_for(loc.population_tier, loc.difficulty_tier)
    if session.player.gold < cost:
        log.plain(f"Founding a {biz_type} here costs {cost}g -- you're short. Options: " + ", ".join(business_gen.BUSINESS_TYPES))
        return
    name = f"{loc.name} {biz_type}"
    biz = Business(
        id=f"{session.location_id}_owned_{session.game_tick}", location_id=session.location_id, location_name=loc.name,
        name=name, business_type=biz_type, investment=cost, ownership_percent=100, last_event_tick=session.game_tick,
    )
    session.player = replace(session.player, gold=session.player.gold - cost, owned_businesses=session.player.owned_businesses + (biz,))
    log.bold(f"You found {name} for {cost}g. It's yours outright -- but someone has to run it.")
    log.dim("'hire manager' when you're ready -- until then, it earns nothing sitting idle.")


_MANAGER_FIRST_NAMES = ["Alden", "Brynn", "Cass", "Doran", "Ester", "Finn", "Greta", "Hollis", "Iris", "Jorah"]
_MANAGER_LAST_NAMES = ["Ashford", "Birch", "Coldwell", "Drummond", "Everly", "Falk", "Grimshaw", "Hartley"]


def hire_manager(session: GameSession, log: Log) -> None:
    biz = next((b for b in session.player.owned_businesses if b.location_id == session.location_id and b.is_fully_owned), None)
    if biz is None:
        log.plain("You don't own a business here to manage.")
        return
    if biz.has_manager:
        log.plain(f"{biz.manager_name} already manages {biz.name}. 'fire manager' first if you want someone else.")
        return
    description, quality = business_gen.roll_manager_candidate(session.rng)
    name = f"{session.rng.choice(_MANAGER_FIRST_NAMES)} {session.rng.choice(_MANAGER_LAST_NAMES)}"
    updated = replace(biz, manager_name=name, manager_quality=quality, manager_revealed=False, manager_cycles_observed=0)
    session.player = replace(session.player, owned_businesses=tuple(updated if b.id == biz.id else b for b in session.player.owned_businesses))
    log.bold(f"You hire {name} -- {description} -- to manage {biz.name}.")
    log.dim("You won't really know what you've got until you've seen them work for a while.")


def fire_manager(session: GameSession, log: Log) -> None:
    biz = next((b for b in session.player.owned_businesses if b.location_id == session.location_id and b.is_fully_owned), None)
    if biz is None:
        log.plain("You don't own a business here.")
        return
    if not biz.has_manager:
        log.plain(f"{biz.name} has no manager to let go.")
        return
    old_name = biz.manager_name
    updated = replace(biz, manager_name=None, manager_quality=None, manager_revealed=False, manager_cycles_observed=0)
    session.player = replace(session.player, owned_businesses=tuple(updated if b.id == biz.id else b for b in session.player.owned_businesses))
    log.plain(f"You let {old_name} go from {biz.name}. It sits without a manager until you hire again.")


def sell_business(session: GameSession, log: Log) -> None:
    biz = next((b for b in session.player.owned_businesses if b.location_id == session.location_id), None)
    if biz is None:
        log.plain("You have no stake in a business here.")
        return
    price = business_gen.sell_price(biz)
    session.player = replace(
        session.player, gold=session.player.gold + price,
        owned_businesses=tuple(b for b in session.player.owned_businesses if b.id != biz.id),
    )
    log.yellow(f"You divest your interest in {biz.name} for {price}g.")


def check_business_events(session: GameSession, log: Log) -> None:
    if not session.player.owned_businesses:
        return
    updated = []
    for biz in session.player.owned_businesses:
        new_biz, lines, gold_delta = business_gen.process_cycle(biz, session.game_tick, session.rng)
        updated.append(new_biz)
        for line in lines:
            if gold_delta > 0:
                log.cyan(line)
            elif gold_delta < 0:
                log.red(line)
            else:
                log.dim(line)
        if gold_delta:
            session.player = replace(session.player, gold=session.player.gold + gold_delta)
    session.player = replace(session.player, owned_businesses=tuple(updated))


def print_prompt(session: GameSession, log: Log) -> None:
    """A compact one-line vitals readout, styled after Achaea's iconic HP/mana prompt line."""
    p = session.player
    log.bold(
        f"{p.name} ({p.race.display_name} {p.character_class.display_name}) "
        f"HP:{p.current_health}/{p.max_health} SP:{p.current_stamina}/{p.max_stamina} "
        f"AC:{p.armor_class} Lv:{p.level} Gold:{p.gold}g Bank:{p.bank_gold}g>"
    )


def travel(session: GameSession, log: Log, arg: str) -> None:
    if not arg.strip():
        log.plain("Travel where? Name a city you've discovered.")
        return
    dest = next(
        (loc for loc_id in session.discovered_locations if (loc := session.world.locations.get(loc_id)) is not None
         and loc.population_tier == PopulationTier.CITY and arg.lower() in loc.name.lower()),
        None,
    )
    if dest is None:
        log.plain("You haven't discovered a city by that name.")
        return
    previous_biome = session.current_location.biome
    session.sub_realm_position = None
    session.record_overworld_departure(session.location_id)
    session.location_id = dest.id
    log.white(f"You make the long journey to {dest.name}, the road blurring past in a montage of travel.")
    describe_location(session, log)
    _maybe_ai_biome_narration(session, log, previous_biome, dest)


# --- Death / journal / endgame -----------------------------------------------

def handle_death(session: GameSession, log: Log, session_id: str | None = None) -> None:
    from eldoria.world import save_manager

    log.red("You have fallen...")

    companion = session.player.companion
    if companion is not None and not companion.revive_used:
        healed = max(1, int(session.player.max_health * 0.4))
        session.player = replace(session.player, current_health=healed, companion=replace(companion, revive_used=True))
        log.bold(f"{companion.name} hauls you back from the brink! \"Not on my watch. Not today.\"")
        log.dim(f"({companion.name} can't do that again this employment.)")
        return
    if Perk.SECOND_WIND in session.player.perks and session.player.second_wind_ready:
        session.player = replace(session.player, current_health=1, second_wind_ready=False)
        log.bold("Second Wind saves you at the last moment! You stand at 1 health.")
        return

    snapshot = save_manager.load(session_id) if session_id else None
    if snapshot is not None:
        session.restore_from(snapshot)
        log.red("Darkness takes you... and the world reforms around your last save.")
        log.dim(f"You wake in {session.current_location.name}.")
        describe_location(session, log)
        return

    lost_gold = session.player.gold // 2
    session.player = replace(
        session.player,
        current_health=session.player.max_health,
        gold=session.player.gold - lost_gold,
        reputation=max(-100, min(100, session.player.reputation - 5)),
    )
    session.sub_realm_position = None
    session.location_id = session.home_location_id
    session.discover(session.home_location_id)
    log.red(f"(No save found yet.) You wake in {session.current_location.name}, having lost {lost_gold}g.")
    describe_location(session, log)


def print_journal(session: GameSession, log: Log) -> None:
    log.bold("Journal:")
    main_status = "[complete]" if MAIN_QUEST_ID in session.completed_quests else "[active]"
    log.plain(f"  {main_status} Find Your Family: stolen as a child by the Kingdom's nobles, you search Eldoria for the family they tore you from.")
    if session.final_battle_won:
        log.plain("  [complete] Confront the Nobles: the throne has answered for what it did to your family.")
    elif session.final_battle_unlocked:
        log.plain("  [active] Confront the Nobles: your family is safe and waiting. Type 'confront' when ready.")
    home_quests = [qid for qid in home_region_content.QUEST_TITLES if qid in session.active_home_region_quests or qid in session.completed_side_quests]
    if home_quests:
        log.bold("Home region quests:")
        for qid in home_quests:
            status = "[complete]" if qid in session.completed_side_quests else "[active]"
            log.plain(f"  {status} {home_region_content.QUEST_TITLES[qid]}")
    if not session.discovered_quests:
        log.plain("No dungeon/sky-realm quests discovered yet -- find a portal and 'enter' it.")
        return
    for qid in session.discovered_quests:
        realm = session.world.sub_realms[qid]
        status = "[complete]" if qid in session.completed_quests else "[active]"
        log.plain(f"  {status} {realm.quest.title}: {realm.quest.objective}")


def check_endgame_trigger(session: GameSession, log: Log) -> None:
    """Checked after every quest-completing action."""
    if session.final_battle_unlocked:
        return
    if MAIN_QUEST_ID not in session.completed_quests:
        return
    if not session.discovered_quests:
        return
    if not all(sid in session.completed_quests for sid in session.discovered_quests):
        return

    session.final_battle_unlocked = True
    log.bold("\n" + "*" * 60)
    log.bold(family_content.GRAND_REUNION_SCENE)
    log.plain("")
    log.bold(family_content.THRONE_CALL_TO_ACTION)
    log.bold("*" * 60 + "\n")


def final_battle(session: GameSession, log: Log) -> None:
    """The scripted finale: three named nobles, fought in sequence, ending in a scripted (not dice-rolled) finishing strike."""
    if not session.final_battle_unlocked:
        log.plain("There is nothing to confront yet -- finish every quest first.")
        return
    if session.final_battle_won:
        log.dim("The throne has already answered for its crimes. Your story is told.")
        return

    log.bold("You march on the capital. Three nobles bar your way to the throne.")
    nobles = family_content.NOBLES
    for i, noble in enumerate(nobles):
        if not session.player.is_alive:
            return
        log.red(f"\n{noble.name}, {noble.title}, steps forward to meet you.")
        base_stats = sg.creature_stats(5, session.rng)
        stats = replace(base_stats, max_health=base_stats.max_health + i * 15, attack_bonus=base_stats.attack_bonus + i)
        hp = stats.max_health
        round_num = 0
        while hp > 0 and session.player.is_alive and round_num < 40:
            round_num += 1
            player_roll = sg.attack_roll(session.rng, session.player.attack_bonus)
            if sg.is_hit(player_roll, stats.armor_class):
                weapon = session.player.equipped_weapon
                dmg = max(1, (weapon.damage if weapon else session.player.unarmed_damage).roll(session.rng))
                hp -= dmg
                log.plain(f"  You strike {noble.name} for {dmg} damage.")
            else:
                log.dim(f"  You attack {noble.name} and miss.")
            if hp <= 0:
                break

            foe_roll = sg.attack_roll(session.rng, stats.attack_bonus)
            if sg.is_hit(foe_roll, session.player.armor_class):
                dmg = max(1, stats.damage.roll(session.rng))
                if stats.magic_damage is not None:
                    dmg += stats.magic_damage.roll(session.rng)
                dmg = max(1, dmg - int(dmg * session.player.race.magic_resistance_percent / 100.0))
                session.player = replace(session.player, current_health=session.player.current_health - dmg)
                log.red(f"  {noble.name} strikes you for {dmg} damage.")
            else:
                log.dim(f"  {noble.name} attacks and misses.")
            if not session.player.is_alive:
                handle_death(session, log)
                return

        if i < len(nobles) - 1:
            log.bold(family_content.NOBLE_FALL_LINES[i % len(family_content.NOBLE_FALL_LINES)].replace("{name}", noble.name))
        else:
            log.bold(session.rng.choice(family_content.FINAL_STRIKE_LINES).replace("{name}", noble.name))

    session.final_battle_won = True
    session.player = replace(session.player, reputation=100)
    log.plain("\n" + family_content.VICTORY_EPILOGUE)


def print_codex(session: GameSession, log: Log) -> None:
    if not session.bestiary:
        log.plain("You haven't encountered anyone or anything yet.")
        return
    log.bold(f"Bestiary/Codex ({len(session.bestiary)} encountered):")
    for n in sorted(session.bestiary):
        log.plain(f"  - {n}")


# --- The Chronicle: real-world history, discovered through play. -----------

def _unlock_chronicle(session: GameSession, log: Log, key: str) -> None:
    """Shows one not-yet-seen fact from a chronicle entry and marks it discovered. No-op once fully read."""
    title, facts = world_history_lore.ALL_CHRONICLE_ENTRIES[key]
    already_seen = key in session.chronicle_discovered
    fact = session.rng.choice(facts) if already_seen else facts[0]
    log.cyan(fact)
    if not already_seen:
        session.chronicle_discovered.add(key)
        log.dim(f"(New chronicle entry: {title} -- type 'chronicle' to review what you've learned.)")


def print_chronicle(session: GameSession, log: Log) -> None:
    if not session.chronicle_discovered:
        log.plain("Your chronicle is empty so far -- history turns up in unexpected corners of the world. Keep exploring.")
        return
    log.bold(f"Chronicle ({len(session.chronicle_discovered)}/{len(world_history_lore.ALL_CHRONICLE_ENTRIES)} entries discovered):")
    for key in sorted(session.chronicle_discovered):
        title, facts = world_history_lore.ALL_CHRONICLE_ENTRIES[key]
        log.bold(f"  {title}")
        for fact in facts:
            log.plain(f"    {fact}")


# --- Boats / sailing ------------------------------------------------------

def grant_gills_from_big_kahoona(session: GameSession, log: Log) -> None:
    if session.player.has_gills:
        return
    session.player = replace(session.player, has_gills=True, defeated_big_kahoona=True)
    log.bold(f"\nAs the {BIG_KAHOONA_NAME} sinks back into the deep, something changes in you -- your neck stings, and when you touch it you feel slits there that weren't there before. Gills.")
    log.bold("You can breathe underwater now. Every river and every sea in the Kingdom is open to you, boat or no boat.")


def buy_boat(session: GameSession, log: Log) -> None:
    if not is_sea_port(session):
        log.plain("You need to be at a coastal settlement to buy a boat.")
        return
    if session.player.owned_boat is not None:
        log.plain("You already own a boat. Sell it to the shipwright before buying another (not yet supported -- just keep it).")
        return
    boat = boat_generator.buy(session.rng)
    if session.player.gold < boat.value:
        log.plain(f"The shipwright offers you the {boat.name} for {boat.value}g -- you can't afford it yet.")
        return
    session.player = replace(session.player, gold=session.player.gold - boat.value, owned_boat=boat)
    log.bold(f"You buy the {boat.name} for {boat.value}g. She's yours now -- try not to sink her.")


def boat_status(session: GameSession, log: Log) -> None:
    boat = session.player.owned_boat
    if boat is None:
        log.plain("You don't own a boat. Buy one at a coastal settlement ('buy boat').")
        return
    cannon_note = " [cannons fitted]" if boat.has_cannons else ""
    wreck_note = " -- WRECKED, needs repair" if boat.is_broken else ""
    log.plain(f"{boat.name}{cannon_note}: {boat.current_durability}/{boat.max_durability} hull integrity{wreck_note}")


def buy_cannons(session: GameSession, log: Log) -> None:
    boat = session.player.owned_boat
    if boat is None:
        log.plain("You need a boat before you can fit cannons to it.")
        return
    if not is_sea_port(session):
        log.plain("You need to be at a coastal settlement to have cannons fitted.")
        return
    if boat.has_cannons:
        log.plain(f"The {boat.name} already has cannons fitted.")
        return
    if session.player.gold < CANNON_COST:
        log.plain(f"The shipwright wants {CANNON_COST}g to fit cannons -- you're short.")
        return
    session.player = replace(session.player, gold=session.player.gold - CANNON_COST, owned_boat=replace(boat, has_cannons=True))
    log.bold(f"A pair of iron cannons are bolted to the {boat.name}'s hull. Sea monsters beware.")


def repair_boat(session: GameSession, log: Log) -> None:
    boat = session.player.owned_boat
    if boat is None:
        log.plain("You don't own a boat.")
        return
    if not is_sea_port(session):
        log.plain("You need to be at a coastal settlement to find a shipwright.")
        return
    if boat.current_durability >= boat.max_durability:
        log.plain("Your boat is already in full repair.")
        return
    cost = boat_generator.repair_cost(boat)
    if session.player.gold < cost:
        log.plain(f"Repairs would cost {cost}g -- you can't afford that yet.")
        return
    session.player = replace(session.player, gold=session.player.gold - cost, owned_boat=boat.repaired())
    log.yellow(f"The shipwright patches up the {boat.name} for {cost}g. Good as new.")
    if session.rng.randrange(100) < 25:
        _unlock_chronicle(session, log, world_history_lore.ARCHIMEDES_KEY)


def _ship_encounter(session: GameSession, log: Log, foe_name: str, foe_stats: StatBlock) -> str:
    """Combat at sea: each enemy hit has a chance to wound the boat instead of the sailor. Returns CONTINUE/BOAT_LOST/PLAYER_DOWN."""
    foe_hp = foe_stats.max_health
    round_num = 0
    while foe_hp > 0 and session.player.is_alive and round_num < 30:
        round_num += 1
        player_roll = sg.attack_roll(session.rng, session.player.attack_bonus)
        if sg.is_hit(player_roll, foe_stats.armor_class):
            weapon = session.player.equipped_weapon
            dmg = max(1, (weapon.damage if weapon else session.player.unarmed_damage).roll(session.rng))
            foe_hp -= dmg
            log.plain(f"  You strike the {foe_name} for {dmg} damage.")
        else:
            log.dim(f"  You attack the {foe_name} and miss.")
        if foe_hp <= 0:
            break

        if session.player.owned_boat is not None and session.player.owned_boat.has_cannons:
            cannon_dmg = DiceFormula(2, DieType.D10, 0).roll(session.rng)
            foe_hp -= cannon_dmg
            log.yellow(f"  Your cannons roar! {cannon_dmg} damage to the {foe_name}.")
            if foe_hp <= 0:
                break

        foe_roll = sg.attack_roll(session.rng, foe_stats.attack_bonus)
        hits_boat = session.player.owned_boat is not None and session.rng.choice([True, False])
        if hits_boat:
            dmg = max(1, foe_stats.damage.roll(session.rng))
            boat = session.player.owned_boat.worn(dmg)
            session.player = replace(session.player, owned_boat=boat)
            log.red(f"  The {foe_name} slams into your hull for {dmg} damage! ({boat.current_durability}/{boat.max_durability} hull left)")
            if boat.is_broken:
                return "BOAT_LOST"
        elif sg.is_hit(foe_roll, session.player.armor_class):
            dmg = max(1, foe_stats.damage.roll(session.rng))
            resisted = int(dmg * session.player.race.magic_resistance_percent / 100.0)
            dmg = max(1, dmg - resisted)
            session.player = replace(session.player, current_health=session.player.current_health - dmg)
            log.red(f"  The {foe_name} strikes you for {dmg} damage.")
        else:
            log.dim(f"  The {foe_name} attacks and misses.")
    if not session.player.is_alive:
        handle_death(session, log)
        return "PLAYER_DOWN"
    if foe_hp <= 0:
        session.record_seen(foe_name)
        xp = level_progression.xp_for_defeating(4, session.rng)
        session.player = level_progression.apply_experience(session.player, xp, session.rng)
        log.plain(f"You gain {xp} experience.")
    return "CONTINUE"


def sail(session: GameSession, log: Log, arg: str) -> None:
    """Sailing is a separate fast-travel network: any Sea settlement can be sailed to directly, discovered or not."""
    if not is_sea_port(session):
        log.plain("You need to be at a coastal settlement to set sail.")
        return
    boat = session.player.owned_boat
    if boat is None:
        log.plain("You don't own a boat. Buy one here first ('buy boat').")
        return
    if boat.is_broken:
        log.plain("Your boat is wrecked and needs repairs before it can sail.")
        return
    if not arg.strip():
        log.plain("Sail where? Name a Sea settlement.")
        return
    dest = next(
        (loc for loc in session.world.locations.values()
         if loc.biome == Biome.SEA and loc.population_tier != PopulationTier.WILDERNESS and arg.lower() in loc.name.lower()),
        None,
    )
    if dest is None:
        log.plain("No such Sea settlement is known.")
        return
    if dest.id == session.location_id:
        log.plain("You're already there.")
        return

    log.white(f"You cast off aboard the {boat.name}, bound for {dest.name}.")
    session.player = replace(session.player, owned_boat=boat.worn(session.rng.randint(1, 3)))

    if session.rng.randrange(100) < 40:
        is_big_kahoona = session.rng.randrange(100) < 5
        tier = 5 if is_big_kahoona else session.rng.randint(2, 5)
        is_pirate = (not is_big_kahoona) and session.rng.choice([True, False])
        if is_big_kahoona:
            foe_name = BIG_KAHOONA_NAME
        elif is_pirate:
            foe_name = session.rng.choice(PIRATE_SHIP_NAMES)
        else:
            hostile_creatures = [c for c in biome_content.get(Biome.SEA).creatures_for(tier) if c.disposition == Disposition.HOSTILE]
            foe_name = session.rng.choice(hostile_creatures).name
        if is_big_kahoona:
            log.bold(f"\nThe water churns and boils, and something impossibly vast rises from beneath -- the {BIG_KAHOONA_NAME}, a squid the size of a ship, has found you!")
        else:
            log.red(f"A {foe_name} rises out of the waves ahead!")
        base_stats = sg.creature_stats(tier, session.rng)
        stats = replace(base_stats, max_health=base_stats.max_health * 2, attack_bonus=base_stats.attack_bonus + 2) if is_big_kahoona else base_stats
        outcome = _ship_encounter(session, log, foe_name, stats)
        if outcome == "BOAT_LOST":
            log.red(f"The {boat.name} breaks apart beneath you! You swim for it, washing up battered at {dest.name}, your boat lost to the deep.")
            session.player = replace(session.player, owned_boat=None, current_health=max(1, session.player.max_health // 3))
        elif outcome == "PLAYER_DOWN":
            return
        else:
            log.bold(f"You drive off the {foe_name} and continue on to {dest.name}.")
            if is_big_kahoona:
                grant_gills_from_big_kahoona(session, log)
    elif session.rng.randrange(100) < 12:
        _unlock_chronicle(session, log, world_history_lore.VIKING_KEY)

    if session.player.is_alive:
        session.location_id = dest.id
        session.discover(dest.id)
        log.white(f"You make port at {dest.name}.")
        describe_location(session, log)


def maybe_ferry_encounter(session: GameSession, log: Log, dest: GameLocation) -> None:
    if session.in_sub_realm or session.player.owned_boat is None or session.ferryman_available:
        return
    neighbor_terrains = [
        loc.terrain for loc in (
            session.world.location_at(dest.x, dest.y - 1),
            session.world.location_at(dest.x, dest.y + 1),
            session.world.location_at(dest.x - 1, dest.y),
            session.world.location_at(dest.x + 1, dest.y),
        ) if loc is not None
    ]
    near_water = dest.terrain != TerrainKind.LAND or any(t != TerrainKind.LAND for t in neighbor_terrains)
    if not near_water:
        return
    if session.rng.randrange(100) >= 12:
        return

    session.ferryman_available = True
    log.cyan(
        "\nA weathered fisherman poles a small skiff past, and slows when he spots you. "
        "\"Rough way to travel, on foot. I can run you to port, for a coin or a favor.\" (type 'ferry' or 'ferry favor')"
    )


def accept_ferry(session: GameSession, log: Log, arg: str) -> None:
    if not session.ferryman_available:
        log.plain("There's no ferryman here right now.")
        return
    candidates = [loc for loc in session.world.locations.values() if loc.biome == Biome.SEA and loc.population_tier != PopulationTier.WILDERNESS]
    if not candidates:
        log.plain("The fisherman scratches his head. \"Truth told, I don't rightly know a port from here.\"")
        return
    dest = min(candidates, key=lambda loc: abs(loc.x - session.current_location.x) + abs(loc.y - session.current_location.y))

    if arg.lower() == "favor":
        positive = next(((k, v) for k, v in session.player.materials.items() if v > 0), None)
        if positive is None:
            log.plain("\"A favor, you said? You've nothing on you worth my while.\"")
            return
        key, value = positive
        new_materials = dict(session.player.materials)
        new_materials[key] = value - 1
        session.player = replace(session.player, materials=new_materials)
        log.cyan(f"You hand over {key} in trade. \"Fair enough. Climb aboard.\"")
    else:
        fee = session.rng.randint(10, 25)
        if session.player.gold < fee:
            log.plain(f"The fisherman wants {fee}g -- you're short. Try 'ferry favor' instead if you've goods to trade.")
            return
        session.player = replace(session.player, gold=session.player.gold - fee)
        log.cyan(f"You pay {fee}g. \"Climb aboard, then.\"")

    previous_biome = session.current_location.biome
    session.ferryman_available = False
    session.sub_realm_position = None
    session.record_overworld_departure(session.location_id)
    session.location_id = dest.id
    session.discover(dest.id)
    log.white(f"The skiff cuts across the water and puts you ashore at {dest.name}.")
    describe_location(session, log)
    _maybe_ai_biome_narration(session, log, previous_biome, dest)


def maybe_balloon_encounter(session: GameSession, log: Log, dest: GameLocation) -> None:
    """A strange flying machine, found by luck in any village -- unlike 'travel', it goes anywhere, discovered or not."""
    if session.in_sub_realm or dest.population_tier != PopulationTier.COUNTRYSIDE or session.balloon_man_available:
        return
    if session.rng.randrange(100) >= 8:
        return

    session.balloon_man_available = True
    log.cyan(
        "\nA strange, buzzing contraption of wood, wire, and canvas descends out of the clouds -- a flying machine! "
        "A wind-burned man in cracked goggles leans out of it. \"Name's Wright,\" he says. \"Orville Wright. I'm out "
        "hunting for my brother Wilbur, lost somewhere in this kingdom -- care for a lift while I search? This old "
        "Flyer can set you down anywhere in the realm.\" (type 'ride <city name>' or 'fly <city name>')"
    )


def ride_balloon(session: GameSession, log: Log, arg: str) -> None:
    if not session.balloon_man_available:
        log.plain("There's no flying machine here right now.")
        return
    if not arg.strip():
        log.plain("Fly where? Name any city in the Kingdom.")
        return
    dest = next((loc for loc in session.world.locations.values() if loc.population_tier == PopulationTier.CITY and arg.lower() in loc.name.lower()), None)
    if dest is None:
        log.plain("\"Never heard of the place,\" Mr. Wright says. \"Name a real city.\"")
        return

    previous_biome = session.current_location.biome
    session.balloon_man_available = False
    session.sub_realm_position = None
    session.record_overworld_departure(session.location_id)
    session.location_id = dest.id
    session.discover(dest.id)
    log.white("You climb aboard the Flyer's flimsy wooden frame and grip tight. The engine sputters, the wings catch the wind, and the ground falls away beneath you.")
    log.cyan(session.rng.choice(finance_lore.WRIGHT_FACTS))
    log.white(f"The kingdom rolls by below, and the Flyer sets down gently in {dest.name}.")
    describe_location(session, log)
    _maybe_ai_biome_narration(session, log, previous_biome, dest)


def print_help(log: Log) -> None:
    log.plain("Movement: north/n, south/s, east/e, west/w, up, down, go <exit>")
    log.plain("Look:      look/l, map/m, character/c, inventory/inv, journal, codex, chronicle, prompt")
    log.plain("People:    talk <name>, train <name>, attack <name>")
    log.plain("Items:     take <item>, equip <item>, craft <skill>")
    log.plain("Places:    enter (a dungeon/sky portal), leave (a sub-realm), travel <city>")
    log.plain("Shop:      shop, buy <#>, sell <#>")
    log.plain("Boats:     buy boat, buy cannons, boat, sail <sea port>, repair (at a Sea settlement), ferry (if a fisherman happens by)")
    log.plain("Flight:    ride/fly <city> (if Mr. Wright happens by a village -- goes anywhere, discovered or not)")
    log.plain("Bank:      bank, deposit <#>, withdraw <#> (any city -- compound interest, real 0.5% withdrawal fee), buy reckoning")
    log.plain("Property:  buy house, sell house, repair house, property (any city or village)")
    log.plain("Business:  invest <#> (passive stake), start <type>, hire manager, fire manager, sell business, business (any city)")
    log.plain("Underworld: gamble <#>, fence <item> (rougher parts of wealthier cities only -- illegal, and it shows in your reputation)")
    log.plain("Endgame:   confront (once every quest is complete and it's been unlocked)")
    log.plain("Curses:    request vampire/werewolf (from the one who offers it, one-time, mutually exclusive)")
    log.plain("Side quests: talk <name> to hear an offer, then resolve <keyword> to settle it -- always pays out something")
    log.plain("Bionics:   upgrade strength/agility/willpower (Mad Scientist only, once per character)")
    log.plain("Companion: hire (from a willing city local), talk/attack <name> also affects them")
    log.plain("Prompts:   accept/decline (answer a pending yes/no offer, e.g. a home-region quest)")
    log.plain("Other:     rest, sleep (safe rest only, heals stamina too, autosaves), perk, help")
