import random
import copy
from rpg_game.combat import (
    start_combat, GOBLIN, DIRE_WOLF, BANDIT_LEADER, SHADOW_CULTIST, 
    STONE_GOLEM, ANCIENT_DRAGON, GIANT_TOAD, MOUNTAIN_GOAT, GIANT_CRAB, SKELETAL_WARRIOR
)
from rpg_game.items import (
    AMULET_OF_MANA, AMULET_OF_STAMINA, ANCIENT_COMPASS, ANCIENT_RELIC,
    CHAINMAIL_ARMOR, ELIXIR_OF_LIFE, GLOWING_MUSHROOM, HEALTH_POTION_L,
    HEALTH_POTION_M, HEALTH_POTION_S, IRON_HELMET, LEATHER_HELMET,
    LOST_MINER_NOTE, MANA_POTION_M, MANA_POTION_S, RING_OF_DEFENSE,
    RING_OF_HEALTH, RUNIC_WARHAMMER, SHIP_MANIFEST, SHORT_BOW,
    STAMINA_POTION_S, STEEL_PLATE, SWAMP_HERB, TOWER_SHIELD, WAR_AXE
)
from rpg_game.utils import (
    clear_screen, display_message, press_enter_to_continue, get_input,
    c_item, c_enemy, c_location, c_npc, c_quest, Color
)
from rpg_game.quests import ALL_QUESTS
from rpg_game.shop import Shop

class Location:
    def __init__(self, name, description, exits, encounters=None, items=None, npcs=None, shop=None):
        self.name = name
        self.description = description
        self.exits = exits
        self.encounters = encounters if encounters is not None else []
        self.items = items if items is not None else []
        self.npcs = npcs if npcs is not None else []
        self.shop = shop
        self.visited = False

    def display_info(self, player=None, ai_engine=None):
        display_message(f"\n=== {c_location(self.name)} ===")
        
        if ai_engine and ai_engine.enabled and player:
            dynamic_desc = ai_engine.generate_location_flavor(self.name, self.description, player.level)
            display_message(f"{Color.PURPLE}{dynamic_desc}{Color.RESET}" if dynamic_desc else self.description)
        else:
            display_message(self.description)

        if self.items:
            item_descriptions = []
            for item in self.items:
                if ai_engine and ai_engine.enabled:
                    ai_flavor = ai_engine.generate_item_flavor(item.name, item.description, type(item).__name__)
                    item_descriptions.append(f"{c_item(item.name)} ({Color.GRAY}{ai_flavor if ai_flavor else item.description}{Color.RESET})")
                else:
                    item_descriptions.append(f"{c_item(item.name)} ({Color.GRAY}{item.description}{Color.RESET})")
            display_message(f"Ground Items: {', '.join(item_descriptions)}")
        if self.npcs:
            npc_list = ", ".join([c_npc(npc) for npc in self.npcs])
            display_message(f"NPCs present: {npc_list}")
        
        display_message(f"\n--- {Color.BOLD}Exits{Color.RESET} ---")
        for direction, dest_key in self.exits.items():
            display_message(f"  - {Color.GREEN}{direction.capitalize()}{Color.RESET}: {c_location(WORLD_MAP[dest_key].name)}")

    def handle_action(self, player, action, game_state, ai_engine=None):
        if action == 'look':
            self.display_info(player, ai_engine)
            return True

        elif action == 'take':
            if not self.items:
                display_message("Nothing to pick up.")
                return True
            
            if len(self.items) == 1:
                item_to_take = self.items[0]
                player.inventory.append(item_to_take)
                display_message(f"Picked up {c_item(item_to_take.name)}.")
                self.items.remove(item_to_take)
            else:
                item_names = [item.name for item in self.items]
                choice = get_input(f"Which item to take? ({'/'.join(item_names)}/all/back)", item_names + ['all', 'back'])
                if choice == 'back':
                    return True
                elif choice == 'all':
                    for item in list(self.items):
                        player.inventory.append(item)
                        display_message(f"Picked up {c_item(item.name)}.")
                        self.items.remove(item)
                else:
                    item_to_take = next((item for item in self.items if item.name.lower() == choice), None)
                    if item_to_take:
                        player.inventory.append(item_to_take)
                        display_message(f"Picked up {c_item(item_to_take.name)}.")
                        self.items.remove(item_to_take)
                    else:
                        display_message("That item is not here.")
            return True

        elif action == 'talk':
            if not self.npcs:
                display_message("No one to talk to.")
                return True
            
            npc_choice = get_input(f"Talk to whom? ({'/'.join(self.npcs)}/back)", self.npcs + ['back'])
            if npc_choice == 'back':
                return True

            # get_input lowercases the answer; map it back to the canonical NPC name
            npc = next((n for n in self.npcs if n.lower() == npc_choice), npc_choice)
            display_message(f"\nYou approach {c_npc(npc)}.")

            if ai_engine and ai_engine.enabled:
                prompt = get_input(f"Talk to {c_npc(npc)} (or press Enter for standard quest script):")
                if prompt.strip():
                    persona_map = {
                        "Elder Theron": "The wise, worried elder of Oakhaven Village.",
                        "Fisherman Finn": "A gruff but kind old fisherman at Port Eldoria.",
                        "Mountain Guide": "A rugged guide who knows the hazardous Ironstone mountain pass.",
                        "Arcane Vendor": "A cryptic merchant dealing in forbidden artifacts.",
                        "Lost Miner": "A desperate miner, lost and injured in the mountains.",
                        "Ancient Scholar": "An eccentric scholar obsessed with ancient lore."
                    }
                    npc_persona = persona_map.get(npc, "A resident of Eldoria.")
                    resp = ai_engine.generate_npc_response(npc, npc_persona, player, prompt, self.name)
                    if resp:
                        display_message(f"{c_npc(npc)}: \"{resp}\"")
                        press_enter_to_continue()
                        return True

            if npc == "Elder Theron":
                q_relic = ALL_QUESTS["the_lost_relic"]
                q_poison = ALL_QUESTS["poisoned_waters"]

                if not q_relic.is_active and not q_relic.is_completed:
                    display_message(f"{c_npc('Elder Theron')}: \"The Whispering Woods hide an ancient relic, vital to our village's protection. Will you seek it out?\"")
                    if get_input(f"Accept quest '{c_quest('The Ancient Relic')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_relic.activate(player.level, ai_engine)
                elif q_relic.is_active:
                    relic = next((i for i in player.inventory if i.name == ANCIENT_RELIC.name), None)
                    if relic:
                        player.inventory.remove(relic)
                        q_relic.complete(player, ai_engine)
                        display_message(f"{c_npc('Elder Theron')}: \"You have returned the relic! Oakhaven is safer thanks to you, hero.\"")
                    else:
                        display_message(f"{c_npc('Elder Theron')}: \"Have you found the ancient relic yet? The village depends on it.\"")
                
                if not q_poison.is_active and not q_poison.is_completed:
                    display_message(f"{c_npc('Elder Theron')}: \"Our water supply from the swamps has become tainted. If you could gather 3 Swamp Herbs, it might help purify it.\"")
                    if get_input(f"Accept quest '{c_quest('The Poisoned Waters')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_poison.activate(player.level, ai_engine)
                elif q_poison.is_active:
                    if q_poison.complete(player, ai_engine): # complete handles item removal
                        display_message(f"{c_npc('Elder Theron')}: \"Excellent! These herbs will surely help. Thank you, adventurer.\"")
                    else:
                        display_message(f"{c_npc('Elder Theron')}: \"The waters still run foul. Have you found enough Swamp Herbs yet?\"")

                q_goblin = ALL_QUESTS["goblin_menace"]
                if not q_goblin.is_active and not q_goblin.is_completed:
                    display_message(f"{c_npc('Elder Theron')}: \"Goblins have been raiding the roads and woods. Cull at least 3 of them and Oakhaven will reward you.\"")
                    if get_input(f"Accept quest '{c_quest('Goblin Outbreak')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_goblin.activate(player.level, ai_engine)
                        if game_state.get('goblins_defeated', 0) >= 3:
                            q_goblin.complete(player, ai_engine)
                elif q_goblin.is_active:
                    if game_state.get('goblins_defeated', 0) >= 3:
                        q_goblin.complete(player, ai_engine)
                        display_message(f"{c_npc('Elder Theron')}: \"The roads are safer already. You have our thanks, goblin-slayer.\"")
                    else:
                        remaining = 3 - game_state.get('goblins_defeated', 0)
                        display_message(f"{c_npc('Elder Theron')}: \"The goblins still prowl. {remaining} more must fall.\"")

            elif npc == "Fisherman Finn":
                q_cargo = ALL_QUESTS["lost_cargo"]
                if not q_cargo.is_active and not q_cargo.is_completed:
                    display_message(f"{c_npc('Fisherman Finn')}: \"Me cargo, lost in the shipwreck! If ye could find me manifest, I'd be mighty grateful.\"")
                    if get_input(f"Accept quest '{c_quest('Lost Cargo')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_cargo.activate(player.level, ai_engine)
                elif q_cargo.is_active:
                    if q_cargo.complete(player, ai_engine):
                        display_message(f"{c_npc('Fisherman Finn')}: \"Bless yer soul! Me manifest! Now I can sort out this mess. Here's a little something for yer trouble.\"")
                    else:
                        display_message(f"{c_npc('Fisherman Finn')}: \"Any luck with me manifest, eh? It's down in that sunken wreck, I reckon.\"")

            elif npc == "Mountain Guide":
                q_miner = ALL_QUESTS["mountain_rescue"]
                if not q_miner.is_active and not q_miner.is_completed:
                    display_message(f"{c_npc('Mountain Guide')}: \"A miner went missing in the northern pass. If you find him, or at least a note from him, I'd pay handsomely.\"")
                    if get_input(f"Accept quest '{c_quest('Mountain Rescue')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_miner.activate(player.level, ai_engine)
                elif q_miner.is_active:
                    if q_miner.complete(player, ai_engine):
                        display_message(f"{c_npc('Mountain Guide')}: \"A note from poor old Borin... at least we know what happened. Thank you for bringing closure.\"")
                    else:
                        display_message(f"{c_npc('Mountain Guide')}: \"Still no sign of the lost miner? Be careful up there, it's treacherous.\"")

                q_dragon = ALL_QUESTS["slay_the_wyrm"]
                if not q_dragon.is_active and not q_dragon.is_completed:
                    display_message(f"{c_npc('Mountain Guide')}: \"An ancient dragon slumbers atop Dragon's Peak. Slay it, and your name will be sung for generations. Few return from that summit...\"")
                    if get_input(f"Accept quest '{c_quest('Slay the Wyrm')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_dragon.activate(player.level, ai_engine)
                elif q_dragon.is_active:
                    display_message(f"{c_npc('Mountain Guide')}: \"The wyrm still lives — I can see its smoke from here. Take the pass up to the peak, and gods be with you.\"")
            
            elif npc == "Lost Miner": # NPC for the Mountain Rescue quest
                q_miner = ALL_QUESTS["mountain_rescue"]
                if q_miner.is_active and not q_miner.is_completed:
                    display_message(f"{c_npc('Lost Miner')}: \"Oh, thank the heavens! I'm trapped! I dropped my note somewhere nearby, please take it to the guide in the south!\"")
                    if LOST_MINER_NOTE not in player.inventory:
                        player.inventory.append(LOST_MINER_NOTE)
                        display_message(f"You received the {c_item(LOST_MINER_NOTE.name)}.")
                else:
                    display_message(f"{c_npc('Lost Miner')}: \"Just need to rest a bit... then I'll try to find my way out.\"")

            elif npc == "Arcane Vendor":
                q_fungi = ALL_QUESTS["alchemical_fungi"]
                if not q_fungi.is_active and not q_fungi.is_completed:
                    display_message(f"{c_npc('Arcane Vendor')}: \"I require reagents... Glowing Mushrooms from the Shadow Caves. Bring me 2 and I shall make it worth your while.\"")
                    if get_input(f"Accept quest '{c_quest('Alchemical Fungi')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_fungi.activate(player.level, ai_engine)
                elif q_fungi.is_active:
                    if q_fungi.complete(player, ai_engine):
                        display_message(f"{c_npc('Arcane Vendor')}: \"Ahh, they still glow with cave-light. Perfect. Our transaction is complete.\"")
                    else:
                        display_message(f"{c_npc('Arcane Vendor')}: \"No mushrooms yet? The Shadow Caves lie west of here, through the woods.\"")

            elif npc == "Ancient Scholar": # NPC for Ancient Compass quest
                q_compass = ALL_QUESTS["ancient_compass"]
                if not q_compass.is_active and not q_compass.is_completed:
                    display_message(f"{c_npc('Ancient Scholar')}: \"The legends speak of an Ancient Compass, hidden deep within these ruins. It holds immense power. Will you brave the dangers to find it?\"")
                    if get_input(f"Accept quest '{c_quest('The Ancient Compass')}'? (yes/no)", ['yes', 'no']) == 'yes':
                        q_compass.activate(player.level, ai_engine)
                elif q_compass.is_active:
                    if q_compass.complete(player, ai_engine):
                        display_message(f"{c_npc('Ancient Scholar')}: \"Incredible! The Ancient Compass! Its magic is palpable. You have done a great service!\"")
                    else:
                        display_message(f"{c_npc('Ancient Scholar')}: \"The compass... it must be here somewhere. Keep searching the crypts.\"")

            press_enter_to_continue()
            return True

        elif action == 'shop':
            if self.shop:
                self.shop.enter_shop(player)
            else:
                display_message("There is no shop here.")
            return True

        return False

    def check_for_encounter(self, player, game_state, ai_engine=None):
        """Returns (is_player_defeated, defeated_by_enemy_name, encounter_happened)."""
        for enemy_type, chance in self.encounters:
            if random.random() < chance:
                clear_screen()
                active_enemy = copy.deepcopy(enemy_type)
                # start_combat returns (is_player_defeated, enemy_name_if_defeated)
                is_player_defeated, defeated_enemy_name = start_combat(player, active_enemy, ai_engine)

                if not is_player_defeated and player.is_alive() and not active_enemy.is_alive():
                    if active_enemy.name == GOBLIN.name:
                        game_state['goblins_defeated'] = game_state.get('goblins_defeated', 0) + 1
                        if game_state['goblins_defeated'] >= 3 and ALL_QUESTS["goblin_menace"].is_active:
                            ALL_QUESTS["goblin_menace"].complete(player, ai_engine) # Pass ai_engine to quest completion
                    elif active_enemy.name == ANCIENT_DRAGON.name and ALL_QUESTS["slay_the_wyrm"].is_active:
                        ALL_QUESTS["slay_the_wyrm"].complete(player, ai_engine)
                return is_player_defeated, defeated_enemy_name, True
        return False, None, False # No encounter

# --- SHOPS & LOCATIONS ---
oakhaven_shop = Shop("Oakhaven General Merchant", [HEALTH_POTION_M, MANA_POTION_M, IRON_HELMET, WAR_AXE, LEATHER_HELMET])
citadel_shop = Shop("Citadel High Arcane Emporium", [RING_OF_HEALTH, AMULET_OF_MANA, AMULET_OF_STAMINA, CHAINMAIL_ARMOR, STAMINA_POTION_S])
coastal_shop = Shop("Coastal Market", [HEALTH_POTION_S, MANA_POTION_S, SHORT_BOW, RING_OF_DEFENSE, HEALTH_POTION_M])
mountain_shop = Shop("Mountain Outpost Supplies", [HEALTH_POTION_L, ELIXIR_OF_LIFE, RUNIC_WARHAMMER, STEEL_PLATE, TOWER_SHIELD])

WORLD_MAP = {
    "oakhaven_village": Location("Oakhaven Village", "A serene village surrounding a central square. The air smells of fresh bread and damp earth.", {'north': 'whispering_woods', 'east': 'old_road', 'south': 'eastern_swamps'}, npcs=["Elder Theron"], shop=oakhaven_shop),
    "whispering_woods": Location("Whispering Woods", "Dense forest with howling wind through misty trees. Ancient, gnarled trees loom overhead.", {'south': 'oakhaven_village', 'north': 'deep_woods', 'east': 'shadow_caves'}, encounters=[(DIRE_WOLF, 0.3), (GOBLIN, 0.1)]),
    "deep_woods": Location("Deep Whispering Woods", "Pitch dark canopy where sunlight cannot reach. Strange sounds echo from the shadows.", {'south': 'whispering_woods', 'west': 'ancient_ruins'}, encounters=[(GOBLIN, 0.4), (DIRE_WOLF, 0.2)], items=[ANCIENT_RELIC]),
    "shadow_caves": Location("Shadow Caves", "Damp limestone cave network dripping with glowing flora. The air is cool and still.", {'west': 'whispering_woods', 'east': 'sunken_citadel'}, encounters=[(GOBLIN, 0.3), (GIANT_TOAD, 0.2)], items=[GLOWING_MUSHROOM, GLOWING_MUSHROOM]),
    "old_road": Location("Old Forest Road", "Long dirt path connecting distant provinces. Wagon tracks are faintly visible.", {'west': 'oakhaven_village', 'east': 'ironstone_foothills', 'south': 'coastal_town'}, encounters=[(GOBLIN, 0.25), (BANDIT_LEADER, 0.1)]),
    "ironstone_foothills": Location("Ironstone Foothills", "Rocky ascending terrain surrounded by jagged cliff faces. The wind picks up here.", {'west': 'old_road', 'north': 'ironstone_pass', 'east': 'mountain_pass_north'}, encounters=[(BANDIT_LEADER, 0.3), (MOUNTAIN_GOAT, 0.2)], npcs=["Mountain Guide"]),
    "ironstone_pass": Location("Ironstone Mountain Pass", "Freezing mountain path with howling blizzards. The air is thin and cold.", {'south': 'ironstone_foothills', 'up': 'dragons_peak'}, encounters=[(STONE_GOLEM, 0.4), (MOUNTAIN_GOAT, 0.3)]),
    "dragons_peak": Location("Dragon's Peak Summit", "High volcanic summit covered in ancient scorch marks. A faint smell of sulfur lingers.", {'down': 'ironstone_pass'}, encounters=[(ANCIENT_DRAGON, 0.8)]),
    "sunken_citadel": Location("Sunken Citadel Courtyard", "Ancient flooded stone fortress radiating dark power. Water laps at crumbling walls.", {'west': 'shadow_caves'}, npcs=["Arcane Vendor"], shop=citadel_shop, encounters=[(SHADOW_CULTIST, 0.5), (SKELETAL_WARRIOR, 0.3)]),
    "eastern_swamps": Location("Eastern Swamps", "A murky, humid marshland. Strange plants and buzzing insects fill the air.", {'north': 'oakhaven_village'}, encounters=[(GIANT_TOAD, 0.4), (DIRE_WOLF, 0.1)], items=[SWAMP_HERB, SWAMP_HERB, SWAMP_HERB]),
    "coastal_town": Location("Coastal Town of Port Eldoria", "A bustling port town with the scent of salt and fish. Ships dock constantly.", {'north': 'old_road', 'east': 'sunken_shipwreck'}, npcs=["Fisherman Finn"], shop=coastal_shop),
    "sunken_shipwreck": Location("Sunken Shipwreck", "The remains of a grand ship, half-submerged in shallow waters.", {'west': 'coastal_town'}, encounters=[(GIANT_CRAB, 0.5)], items=[SHIP_MANIFEST, HEALTH_POTION_S]),
    "mountain_pass_north": Location("Northern Mountain Pass", "A narrow, icy path winding through towering peaks.", {'west': 'ironstone_foothills', 'north': 'forgotten_crypt'}, encounters=[(MOUNTAIN_GOAT, 0.4), (STONE_GOLEM, 0.2)], npcs=["Lost Miner"], items=[LOST_MINER_NOTE]),
    "ancient_ruins": Location("Ancient Ruins", "Crumbling stone structures overgrown with vines.", {'east': 'deep_woods', 'north': 'forgotten_crypt'}, encounters=[(SKELETAL_WARRIOR, 0.4), (SHADOW_CULTIST, 0.2)], npcs=["Ancient Scholar"], items=[ANCIENT_RELIC]),
    "forgotten_crypt": Location("Forgotten Crypt", "A dark, musty crypt beneath the ancient ruins.", {'south': 'ancient_ruins', 'west': 'mountain_pass_north'}, encounters=[(SKELETAL_WARRIOR, 0.6), (SHADOW_CULTIST, 0.3)], items=[ANCIENT_COMPASS, MANA_POTION_M])
}

# Pristine copies of mutable world state, captured at import time, so a new
# game can start fresh even after a previous playthrough in the same session.
_INITIAL_LOCATION_ITEMS = {key: list(loc.items) for key, loc in WORLD_MAP.items()}
_INITIAL_SHOP_STOCK = {key: list(loc.shop.inventory) for key, loc in WORLD_MAP.items() if loc.shop}

def reset_world():
    """Restores ground items and shop stock to their initial state (new game)."""
    for key, loc in WORLD_MAP.items():
        loc.items = list(_INITIAL_LOCATION_ITEMS[key])
        loc.visited = False
        if loc.shop:
            loc.shop.inventory = list(_INITIAL_SHOP_STOCK[key])

def get_world_state():
    """Snapshot of mutable world state for saving."""
    return {
        'location_items': {key: list(loc.items) for key, loc in WORLD_MAP.items()},
        'shop_stock': {key: list(loc.shop.inventory) for key, loc in WORLD_MAP.items() if loc.shop},
    }

def set_world_state(state):
    """Restores mutable world state from a save snapshot."""
    for key, items in state.get('location_items', {}).items():
        if key in WORLD_MAP:
            WORLD_MAP[key].items = list(items)
    for key, stock in state.get('shop_stock', {}).items():
        if key in WORLD_MAP and WORLD_MAP[key].shop:
            WORLD_MAP[key].shop.inventory = list(stock)
