from rpg_game.utils import display_message, get_input, press_enter_to_continue
from rpg_game.items import Equipment

class Shop:
    def __init__(self, name, inventory=None):
        self.name = name
        self.inventory = inventory if inventory is not None else []

    def enter_shop(self, player):
        display_message(f"\nWelcome to {self.name}!")
        while True:
            display_message(f"Your Gold: {player.gold}")
            action = get_input("Choose action: (buy/sell/exit)", ['buy', 'sell', 'exit'])

            if action == 'buy':
                if not self.inventory:
                    display_message("Shop is out of stock.")
                    continue
                print("\n--- Items for Sale ---")
                for i, item in enumerate(self.inventory):
                    print(f"{i+1}. {item.name} - Price: {item.value} Gold ({item.description})")
                
                choice = get_input("Enter item number to buy, or 'back':", [str(i+1) for i in range(len(self.inventory))] + ['back'])
                if choice == 'back':
                    continue
                idx = int(choice) - 1
                item = self.inventory[idx]
                if player.gold >= item.value:
                    player.gold -= item.value
                    player.inventory.append(item)
                    self.inventory.remove(item)
                    display_message(f"Purchased {item.name}!")
                else:
                    display_message("Not enough gold!")

            elif action == 'sell':
                if not player.inventory:
                    display_message("You have no items to sell.")
                    continue
                print("\n--- Sellable Items ---")
                for i, item in enumerate(player.inventory):
                    print(f"{i+1}. {item.name} - Sell Value: {item.value // 2} Gold")
                
                choice = get_input("Enter item number to sell, or 'back':", [str(i+1) for i in range(len(player.inventory))] + ['back'])
                if choice == 'back':
                    continue
                idx = int(choice) - 1
                item = player.inventory[idx]
                player.gold += (item.value // 2)
                player.inventory.remove(item)
                display_message(f"Sold {item.name} for {item.value // 2} gold!")

            elif action == 'exit':
                display_message("Farewell!")
                break
