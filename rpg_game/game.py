import pickle
from rpg_game.classes import ALL_CLASSES
from rpg_game.player import Player
from rpg_game.world import WORLD_MAP
from rpg_game.utils import clear_screen, display_message, get_input, press_enter_to_continue, set_debug_mode
from rpg_game.quests import ALL_QUESTS

class Game:
    def __init__(self):
        self.player = None
        self.current_location_key = "oakhaven_village"
        self.game_state = {'goblins_defeated': 0}
        self.quests = ALL_QUESTS
        self.debug_mode = False

    def run(self):
        self.show_main_menu()

    def show_main_menu(self):
        clear_screen()
        display_message("==========================================")
        display_message("         ELDORIA: EXPANDED REALM          ")
        display_message("==========================================")
        display_message("1. New Game")
        display_message("2. Load Game")
        display_message("3. Quit")
        
        choice = get_input("Choose option (1-3):", ['1', '2', '3'])
        if choice == '1':
            self.start_new_game()
        elif choice == '2':
            self.load_game()
        else:
            display_message("Farewell!")

    def start_new_game(self):
        clear_screen()
        display_message("--- HERO CREATION ---")
        hero_name = get_input("Enter your hero's name:")

        display_message("\nChoose your Player Class:")
        for key, p_class in ALL_CLASSES.items():
            print(f"{key}. {p_class.name} - {p_class.description}")

        class_choice = get_input("Select Class (1-5):", ['1', '2', '3', '4', '5'])
        selected_class = ALL_CLASSES[class_choice]

        self.player = Player(name=hero_name, player_class=selected_class)
        display_message(f"\nWelcome, {self.player.name} the {selected_class.name}!")
        press_enter_to_continue()
        self.game_loop()

    def load_game(self):
        try:
            with open("savegame.pkl", "rb") as f:
                data = pickle.load(f)
                self.player = data['player']
                self.current_location_key = data['location']
                self.game_state = data['game_state']
            display_message("Save loaded successfully!")
            press_enter_to_continue()
            self.game_loop()
        except Exception as e:
            display_message(f"Failed loading save: {e}")
            press_enter_to_continue()
            self.show_main_menu()

    def save_game(self):
        try:
            with open("savegame.pkl", "wb") as f:
                pickle.dump({'player': self.player, 'location': self.current_location_key, 'game_state': self.game_state}, f)
            display_message("Game saved successfully!")
        except Exception as e:
            display_message(f"Error saving game: {e}")
        press_enter_to_continue()

    def game_loop(self):
        location_changed = True
        while self.player.is_alive():
            current_loc = WORLD_MAP[self.current_location_key]

            if location_changed:
                clear_screen()
                current_loc.display_info()
                location_changed = False

            if current_loc.check_for_encounter(self.player, self.game_state):
                display_message("GAME OVER - You have perished in Eldoria.")
                break

            valid_actions = ['look', 'move', 'inventory', 'stats', 'upgrade', 'save', 'quit']
            if current_loc.npcs:
                valid_actions.append('talk')
            if current_loc.items:
                valid_actions.append('take')
            if current_loc.shop:
                valid_actions.append('shop')

            action = get_input("\nAction (look/move/talk/take/shop/inventory/stats/upgrade/save/quit):", valid_actions)

            if action == 'move':
                dirs = list(current_loc.exits.keys())
                chosen_dir = get_input(f"Direction ({'/'.join(dirs)}):", dirs)
                if chosen_dir in current_loc.exits:
                    self.current_location_key = current_loc.exits[chosen_dir]
                    location_changed = True
            elif action == 'stats':
                self.player.display_stats()
                press_enter_to_continue()
            elif action == 'upgrade':
                self.player.spend_attribute_points()
                self.player.spend_perk_points()
            elif action == 'inventory':
                self.player.display_inventory()
            elif action == 'save':
                self.save_game()
            elif action == 'quit':
                break
            else:
                current_loc.handle_action(self.player, action, self.game_state)
