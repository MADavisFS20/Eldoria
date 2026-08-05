import pickle
from rpg_game.classes import ALL_CLASSES
from rpg_game.player import Player
from rpg_game.world import WORLD_MAP, reset_world, get_world_state, set_world_state
from rpg_game.utils import (
    clear_screen, display_message, get_input, press_enter_to_continue,
    set_debug_mode, draw_box, Color, get_movement_input_from_arrows
)
from rpg_game.quests import ALL_QUESTS, reset_quests, get_quest_state, set_quest_state
from rpg_game.ai_engine import AIEngine

class Game:
    def __init__(self, player: Player = None, current_location_key: str = "oakhaven_village", game_state: dict = None):
        self.player = player if player else Player(name="Hero", player_class=ALL_CLASSES["1"])
        self.current_location_key = current_location_key
        self.game_state = game_state if game_state is not None else {'goblins_defeated': 0}
        self.quests = ALL_QUESTS
        self.debug_mode = False
        self.ai_engine = AIEngine()

    def run(self):
        while self.show_main_menu():
            pass

    def show_main_menu(self):
        """Displays the main menu. Returns False when the player chooses to exit."""
        clear_screen()
        menu_lines = [
            "1. Start New Adventure",
            "2. Load Saved Game",
            f"3. Toggle AI Integration (Currently: {'Enabled' if self.ai_engine.enabled else 'Disabled'})",
            f"4. Toggle Developer Debug Mode (Currently: {'Enabled' if self.debug_mode else 'Disabled'})",
            "5. Exit Game"
        ]
        draw_box("ELDORIA: EXPANDED REALM", menu_lines, width=64, border_color=Color.CYAN)

        choice = get_input("Select Menu Option (1-5):", ['1', '2', '3', '4', '5'])
        if choice == '1':
            self.start_new_game()
        elif choice == '2':
            self.load_game()
        elif choice == '3':
            self.toggle_ai_mode()
        elif choice == '4':
            self.toggle_debug_mode()
        elif choice == '5':
            display_message("Farewell, adventurer.")
            return False
        return True

    def toggle_ai_mode(self):
        if self.ai_engine.enabled:
            self.ai_engine.enabled = False
            display_message("AI subsystem toggled OFF.")
        else:
            self.ai_engine = AIEngine()
            if self.ai_engine.enabled:
                display_message("AI subsystem initialized successfully!")
            else:
                display_message("Initialization failed. Check if GEMINI_API_KEY environment variable is set.")
        press_enter_to_continue()

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        set_debug_mode(self.debug_mode)
        display_message(f"Debug Mode set to: {self.debug_mode}")
        press_enter_to_continue()

    def start_new_game(self):
        clear_screen()
        display_message(f"=== {Color.BOLD}CHARACTER CREATION{Color.RESET} ===")
        hero_name = get_input("Enter your hero's name:")

        class_lines = [f"{k}. {c.name} - {c.description}" for k, c in ALL_CLASSES.items()]
        draw_box("CHOOSE YOUR CLASS", class_lines, width=68)

        class_choice = get_input("Select Class (1-5):", ['1', '2', '3', '4', '5'])
        selected_class = ALL_CLASSES[class_choice]

        self.player = Player(name=hero_name, player_class=selected_class)
        self.current_location_key = "oakhaven_village"
        self.game_state = {'goblins_defeated': 0}
        reset_quests()
        reset_world()

        display_message(f"\nWelcome to Eldoria, {Color.BOLD}{self.player.name}{Color.RESET} the {selected_class.name}!")
        
        if self.ai_engine.enabled:
            backstory = self.ai_engine.generate_backstory(self.player.name, selected_class.name, selected_class.description)
            if backstory:
                display_message(f"\n{Color.PURPLE}Your legend begins: {backstory}{Color.RESET}")

        press_enter_to_continue()
        self.game_loop()

    def load_game(self):
        try:
            with open("savegame.pkl", "rb") as f:
                data = pickle.load(f)
                self.player = data['player']
                self.current_location_key = data['location']
                self.game_state = data['game_state']
                # Older saves may not carry quest/world state
                set_quest_state(data.get('quests', {}))
                set_world_state(data.get('world', {}))
            display_message(f"{Color.GREEN}Game save loaded successfully!{Color.RESET}")
            press_enter_to_continue()
            self.game_loop()
        except Exception as e:
            display_message(f"{Color.RED}Error loading save: {e}{Color.RESET}")
            press_enter_to_continue()

    def save_game(self):
        try:
            with open("savegame.pkl", "wb") as f:
                pickle.dump({
                    'player': self.player,
                    'location': self.current_location_key,
                    'game_state': self.game_state,
                    'quests': get_quest_state(),
                    'world': get_world_state(),
                }, f)
            display_message(f"{Color.GREEN}Game saved to savegame.pkl.{Color.RESET}")
        except Exception as e:
            display_message(f"{Color.RED}Failed saving game: {e}{Color.RESET}")
        press_enter_to_continue()

    def game_loop(self):
        location_changed = True
        while self.player.is_alive():
            current_loc = WORLD_MAP[self.current_location_key]

            if location_changed:
                clear_screen()
                current_loc.display_info(self.player, self.ai_engine)
                location_changed = False

            is_player_defeated, defeated_by_enemy, encounter_happened = current_loc.check_for_encounter(self.player, self.game_state, self.ai_engine)
            if is_player_defeated:
                if self.ai_engine.enabled and defeated_by_enemy:
                    game_over_flavor = self.ai_engine.generate_game_over_flavor(self.player.name, defeated_by_enemy, current_loc.name)
                    if game_over_flavor:
                        display_message(f"\n{Color.RED}{Color.BOLD}{game_over_flavor}{Color.RESET}")
                    else:
                        display_message(f"\n{Color.RED}{Color.BOLD}GAME OVER - Your journey ends here.{Color.RESET}")
                else:
                    display_message(f"\n{Color.RED}{Color.BOLD}GAME OVER - Your journey ends here.{Color.RESET}")
                press_enter_to_continue()
                break
            if encounter_happened:
                # Redraw the location after combat so the player regains context
                clear_screen()
                current_loc.display_info(self.player, self.ai_engine)

            all_valid_actions = []
            action_display_names = []

            for direction, dest_key in current_loc.exits.items():
                all_valid_actions.append(direction.lower())
                action_display_names.append(f"{direction.capitalize()} ({WORLD_MAP[dest_key].name})")

            base_actions = ['look', 'inventory', 'equip', 'use', 'stats', 'upgrade', 'save', 'quit']
            if current_loc.npcs: base_actions.append('talk')
            if current_loc.items: base_actions.append('take')
            if current_loc.shop: base_actions.append('shop')
            
            all_valid_actions.extend(base_actions)
            action_display_names.extend([a.capitalize() for a in base_actions])

            # --- NEW: Check for arrow key input first ---
            action = get_movement_input_from_arrows()
            if action is None: # No arrow key pressed, or it was another key
                display_message(f"\n{Color.BOLD}Actions:{Color.RESET} {', '.join(action_display_names)}")
                action = get_input("Command:", all_valid_actions)
            # --- END NEW ---

            if action in current_loc.exits:
                self.current_location_key = current_loc.exits[action]
                location_changed = True
            elif action == 'stats':
                self.player.display_stats()
                press_enter_to_continue()
            elif action == 'inventory':
                self.player.display_inventory(self.ai_engine) # Pass AI engine for item flavor
                press_enter_to_continue()
            elif action == 'equip':
                self.player.choose_equipment_to_wear()
                press_enter_to_continue()
            elif action == 'use':
                self.player.use_item_from_inventory()
                press_enter_to_continue()
            elif action == 'upgrade':
                upgrade_choice = get_input("Upgrade what? (perks/attributes/back)", ['perks', 'attributes', 'back'])
                if upgrade_choice == 'perks':
                    self.player.spend_perk_points(self.ai_engine) # Pass AI engine for perk flavor
                elif upgrade_choice == 'attributes':
                    self.player.spend_attribute_points()
                    press_enter_to_continue()
            elif action == 'save':
                self.save_game()
            elif action == 'quit':
                break
            elif action in ['look', 'take', 'talk', 'shop']:
                current_loc.handle_action(self.player, action, self.game_state, self.ai_engine)
                if action != 'talk': # Only pause after non-talk actions
                    press_enter_to_continue()
