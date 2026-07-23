import random
from rpg_game.utils import display_message, press_enter_to_continue, get_input
from rpg_game.items import Potion, HEALTH_POTION_S, MANA_POTION_S
from rpg_game.spells import ALL_SPELLS

class Enemy:
    def __init__(self, name, health, attack, defense, exp_reward, gold_reward, drops=None):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.drops = drops if drops is not None else []
        self.status = None

    def take_damage(self, damage):
        actual = max(1, damage - self.defense)
        self.current_health = max(0, self.current_health - actual)
        return actual

    def is_alive(self):
        return self.current_health > 0

# --- ENEMY ROSTER ---
GOBLIN = Enemy("Goblin Scavenger", health=35, attack=10, defense=2, exp_reward=25, gold_reward=10, drops=[HEALTH_POTION_S])
DIRE_WOLF = Enemy("Dire Wolf", health=45, attack=14, defense=3, exp_reward=35, gold_reward=5)
BANDIT_LEADER = Enemy("Bandit Outlaw", health=80, attack=20, defense=8, exp_reward=80, gold_reward=45)
SHADOW_CULTIST = Enemy("Shadow Cultist", health=70, attack=24, defense=5, exp_reward=90, gold_reward=60, drops=[MANA_POTION_S])
STONE_GOLEM = Enemy("Stone Golem", health=150, attack=30, defense=20, exp_reward=200, gold_reward=100)
ANCIENT_DRAGON = Enemy("Ancient Flame Dragon", health=350, attack=50, defense=25, exp_reward=800, gold_reward=500)

def start_combat(player, enemy, ai_engine=None):
    display_message(f"\n COMBAT ENGAGED: {enemy.name} emerges!")
    press_enter_to_continue()

    temp_player_def_buff = 0

    while player.is_alive() and enemy.is_alive():
        display_message(f"\n--- {player.name} vs {enemy.name} ---")
        display_message(f"Hero HP: {player.current_health}/{player.max_health} | MP: {player.current_magicka}/{player.max_magicka}")
        display_message(f"Enemy HP: {enemy.current_health}/{enemy.max_health}")

        action = get_input("Select Combat Action: (attack/magic/item/run)", ['attack', 'magic', 'item', 'run'])

        if action == 'attack':
            dmg = random.randint(player.get_total_attack() - 3, player.get_total_attack() + 3)
            actual_dmg = enemy.take_damage(dmg)
            
            flavor = ai_engine.generate_combat_flavor(player.name, enemy.name, "Melee Attack", actual_dmg) if ai_engine else None
            display_message(flavor if flavor else f"You strike {enemy.name} for {actual_dmg} damage!")

        elif action == 'magic':
            if not player.spells:
                display_message("You know no spells!")
                continue
            
            print("\n--- Spellbook ---")
            for i, spell in enumerate(player.spells):
                cost = max(5, spell.magicka_cost - player.perks["mana_efficiency"] * 2)
                print(f"{i+1}. {spell.name} ({spell.school}) - Cost: {cost} MP | Power: {spell.power}")

            choice = get_input("Cast spell number, or 'back':", [str(i+1) for i in range(len(player.spells))] + ['back'])
            if choice == 'back':
                continue
            
            spell = player.spells[int(choice) - 1]
            actual_cost = max(5, spell.magicka_cost - player.perks["mana_efficiency"] * 2)

            if player.current_magicka < actual_cost:
                display_message("Insufficient Magicka!")
                continue

            player.current_magicka -= actual_cost
            spell_power = spell.power + (player.intelligence * 2) + (player.perks["spell_power"] * 5)

            if spell.effect_type == "damage":
                actual_dmg = enemy.take_damage(spell_power)
                display_message(f"You cast {spell.name}! It deals {actual_dmg} magic damage to {enemy.name}.")
                if spell.status_effect:
                    enemy.status = spell.status_effect
                    display_message(f"{enemy.name} is now affected by {spell.status_effect.upper()}!")

            elif spell.effect_type == "heal":
                player.heal(spell_power)
                display_message(f"You cast {spell.name} and restored {spell_power} Health!")

            elif spell.effect_type == "buff_defense":
                temp_player_def_buff += spell.power
                display_message(f"You cast {spell.name}, bolstering defense by +{spell.power} for this fight!")

            elif spell.effect_type == "drain":
                actual_dmg = enemy.take_damage(spell_power)
                player.heal(actual_dmg // 2)
                display_message(f"You drained {actual_dmg} life from {enemy.name}, restoring {actual_dmg // 2} HP!")

        elif action == 'item':
            potions = [i for i in player.inventory if isinstance(i, Potion)]
            if not potions:
                display_message("No potions in inventory!")
                continue
            for i, p in enumerate(potions):
                print(f"{i+1}. {p.name} - {p.description}")
            choice = get_input("Use potion number, or 'back':", [str(i+1) for i in range(len(potions))] + ['back'])
            if choice == 'back':
                continue
            potions[int(choice) - 1].use(player)

        elif action == 'run':
            if random.random() < 0.45:
                display_message("You fled combat successfully!")
                return False
            display_message("Escape attempt failed!")

        if not enemy.is_alive():
            display_message(f"\nVictory! You defeated {enemy.name}!")
            player.add_experience(enemy.exp_reward)
            player.gold += enemy.gold_reward
            for drop in enemy.drops:
                player.inventory.append(drop)
                display_message(f"Looted item: {drop.name}")
            press_enter_to_continue()
            return True

        # Enemy Turn & Status Application
        if enemy.status == "burn":
            burn_dmg = enemy.take_damage(8)
            display_message(f"{enemy.name} suffers {burn_dmg} burn damage!")
        elif enemy.status == "poison":
            p_dmg = enemy.take_damage(12)
            display_message(f"{enemy.name} takes {p_dmg} poison damage!")

        display_message(f"\n{enemy.name} strikes back!")
        enemy_atk = max(1, enemy.attack - temp_player_def_buff)
        player_taken = player.take_damage(enemy_atk)
        display_message(f"{enemy.name} dealt {player_taken} damage to you!")

        if not player.is_alive():
            display_message("\nYou were slain in battle...")
            press_enter_to_continue()
            return False

        press_enter_to_continue()

    return False
