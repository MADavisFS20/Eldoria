import random
import copy
from rpg_game.combat import start_combat, GOBLIN, DIRE_WOLF, BANDIT_LEADER, SHADOW_CULTIST, STONE_GOLEM, ANCIENT_DRAGON
from rpg_game.items import ANCIENT_RELIC, GLOWING_MUSHROOM, HEALTH_POTION_M, MANA_POTION_M, IRON_HELMET, RING_OF_HEALTH, AMULET_OF_MANA
from rpg_game.utils import clear_screen, display_message, press_enter_to_continue, get_input
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

    def display_info(self):
        display_message(f"\n=== {self.name} ===")
        display_message(self.description)
        if self.items:
            display_message("Ground Items: " + ", ".join([i.name for i in self.items]))
        if self.npcs:
            display_message("NPCs present: " + ", ".join(self.npcs))
        display_message("Exits: " + ", ".join([f"{direction.capitalize()} -> {WORLD_MAP[dest].name}" for direction, dest in self.exits.items()]))

    def handle_action(self, player, action, game_state, ai_engine=None):
        if action == 'look':
            self.display_info()
            return True
        elif action == 'take':
            if not self.items:
                display_message("Nothing to pick up.")
                return True
            for item in list(self.items):
                player.inventory.append(item)
                display_message(f"Picked up {item.name}.")
                self.items.remove(item)
            return True
        elif action == 'talk':
            if not self.npcs:
                display_message("No one to talk to.")
                return True
            npc = self.npcs[0]
            display_message(f"\nYou approach {npc}.")
            if ai_engine and ai_engine.enabled:
                prompt = get_input(f"Talk to {npc} (or press Enter for standard quest script):")
                if prompt.strip():
                    resp = ai_engine.generate_npc_response(npc, "Local guild resident", player.name, prompt)
                    if resp:
                        display_message(f"{npc}: \"{resp}\"")
                        press_enter_to_continue()
                        return True

            if npc == "Elder Theron":
                q = ALL_QUESTS["the_lost_relic"]
                if not q.is_active and not q.is_completed:
                    q.activate()
                elif q.is_active:
                    relic = next((i for i in player.inventory if i.name == ANCIENT_RELIC.name), None)
                    if relic:
                        player.inventory.remove(relic)
                        q.complete(player)
            press_enter_to_continue()
            return True
        elif action == 'shop':
            if self.shop:
                self.shop.enter_shop(player)
            return True
        return False

    def check_for_encounter(self, player, game_state, ai_engine=None):
        for enemy_type, chance in self.encounters:
            if random.random() < chance:
                clear_screen()
                active_enemy = copy.deepcopy(enemy_type)
                display_message(f"An enemy approaches in {self.name}!")
                is_dead = start_combat(player, active_enemy, ai_engine)
                if not is_dead and player.is_alive():
                    if active_enemy.name == GOBLIN.name:
                        game_state['goblins_defeated'] = game_state.get('goblins_defeated', 0) + 1
                        if game_state['goblins_defeated'] >= 3 and ALL_QUESTS["goblin_menace"].is_active:
                            ALL_QUESTS["goblin_menace"].complete(player)
                return not player.is_alive()
        return False

# --- EXPANDED MAP LOCATIONS ---
oakhaven_shop = Shop("Oakhaven General Merchant", [HEALTH_POTION_M, MANA_POTION_M, IRON_HELMET])
citadel_shop = Shop("Citadel High Arcane Emporium", [RING_OF_HEALTH, AMULET_OF_MANA])

WORLD_MAP = {
    "oakhaven_village": Location("Oakhaven Village", "A serene village surrounding a central square.", {'north': 'whispering_woods', 'east': 'old_road'}, npcs=["Elder Theron"], shop=oakhaven_shop),
    "whispering_woods": Location("Whispering Woods", "Dense forest with howling wind through misty trees.", {'south': 'oakhaven_village', 'north': 'deep_woods', 'east': 'shadow_caves'}, encounters=[(DIRE_WOLF, 0.3)]),
    "deep_woods": Location("Deep Whispering Woods", "Pitch dark canopy where sunlight cannot reach.", {'south': 'whispering_woods'}, encounters=[(GOBLIN, 0.4)], items=[ANCIENT_RELIC]),
    "shadow_caves": Location("Shadow Caves", "Damp limestone cave network dripping with glowing flora.", {'west': 'whispering_woods', 'east': 'sunken_citadel'}, encounters=[(GOBLIN, 0.3)], items=[GLOWING_MUSHROOM]),
    "old_road": Location("Old Forest Road", "Long dirt path connecting distant provinces.", {'west': 'oakhaven_village', 'east': 'ironstone_foothills'}, encounters=[(GOBLIN, 0.25)]),
    "ironstone_foothills": Location("Ironstone Foothills", "Rocky ascending terrain surrounded by jagged cliff faces.", {'west': 'old_road', 'north': 'ironstone_pass'}, encounters=[(BANDIT_LEADER, 0.3)]),
    "ironstone_pass": Location("Ironstone Mountain Pass", "Freezing mountain path with howling blizzards.", {'south': 'ironstone_foothills', 'up': 'dragons_peak'}, encounters=[(STONE_GOLEM, 0.4)]),
    "dragons_peak": Location("Dragon's Peak Summit", "High volcanic summit covered in ancient scorch marks.", {'down': 'ironstone_pass'}, encounters=[(ANCIENT_DRAGON, 0.8)]),
    "sunken_citadel": Location("Sunken Citadel Courtyard", "Ancient flooded stone fortress radiating dark power.", {'west': 'shadow_caves'}, npcs=["Arcane Vendor"], shop=citadel_shop, encounters=[(SHADOW_CULTIST, 0.5)])
}
