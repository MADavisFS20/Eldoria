import random
from rpg_game.utils import (
    display_message, press_enter_to_continue, get_input,
    draw_box, render_bar, Color, c_enemy, c_item
)
from rpg_game.items import Potion, HEALTH_POTION_S, MANA_POTION_S, GOBLIN_EAR

class Enemy:
    def __init__(self, name, health, attack, defense, exp_reward, gold_reward, drops=None, status_resistance=None):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.drops = drops if drops is not None else []
        self.status = None
        self.status_turns = 0
        self.status_resistance = status_resistance if status_resistance is not None else []

    def take_damage(self, damage):
        actual = max(1, damage - self.defense)
        self.current_health = max(0, self.current_health - actual)
        return actual

    def apply_status(self, status_effect, turns=3):
        if status_effect not in self.status_resistance:
            self.status = status_effect
            self.status_turns = turns
            return True
        return False

    def is_alive(self):
        return self.current_health > 0

# --- ENEMY CATALOG ---
GOBLIN = Enemy("Goblin Scavenger", health=35, attack=10, defense=2, exp_reward=25, gold_reward=10, drops=[HEALTH_POTION_S, GOBLIN_EAR])
DIRE_WOLF = Enemy("Dire Wolf", health=45, attack=14, defense=3, exp_reward=35, gold_reward=5)
BANDIT_LEADER = Enemy("Bandit Outlaw", health=80, attack=20, defense=8, exp_reward=80, gold_reward=45)
SHADOW_CULTIST = Enemy("Shadow Cultist", health=70, attack=24, defense=5, exp_reward=90, gold_reward=60, drops=[MANA_POTION_S])
STONE_GOLEM = Enemy("Stone Golem", health=150, attack=30, defense=20, exp_reward=200, gold_reward=100, status_resistance=['poison', 'burn'])
ANCIENT_DRAGON = Enemy("Ancient Flame Dragon", health=350, attack=50, defense=25, exp_reward=800, gold_reward=500, status_resistance=['burn'])
GIANT_TOAD = Enemy("Giant Toad", health=60, attack=16, defense=4, exp_reward=40, gold_reward=15, drops=[HEALTH_POTION_S], status_resistance=['burn'])
MOUNTAIN_GOAT = Enemy("Mountain Goat", health=75, attack=18, defense=6, exp_reward=50, gold_reward=20)
GIANT_CRAB = Enemy("Giant Crab", health=90, attack=22, defense=10, exp_reward=70, gold_reward=30, status_resistance=['poison'])
SKELETAL_WARRIOR = Enemy("Skeletal Warrior", health=100, attack=25, defense=12, exp_reward=100, gold_reward=50, status_resistance=['poison'])

def _try_apply_status(enemy, spell):
    if spell.status_effect and spell.status_effect != 'drain':
        if enemy.apply_status(spell.status_effect):
            display_message(f"{c_enemy(enemy.name)} is afflicted by {Color.PURPLE}{spell.status_effect}{Color.RESET}!")
        else:
            display_message(f"{c_enemy(enemy.name)} resists the {spell.status_effect} effect.")

def _process_enemy_status(enemy):
    """Ticks the enemy's active status effect. Returns True if the enemy loses its turn."""
    if not enemy.status or enemy.status_turns <= 0:
        return False
    skip_turn = False
    status = enemy.status
    if status in ('burn', 'poison'):
        dot = 5
        enemy.current_health = max(0, enemy.current_health - dot)
        display_message(f"{c_enemy(enemy.name)} suffers {Color.RED}{dot} {status} damage{Color.RESET}!")
    elif status == 'freeze':
        skip_turn = True
        display_message(f"{c_enemy(enemy.name)} is {Color.CYAN}frozen{Color.RESET} and cannot act!")
    enemy.status_turns -= 1
    if enemy.status_turns <= 0:
        display_message(f"The {status} effect on {c_enemy(enemy.name)} wears off.")
        enemy.status = None
    return skip_turn

def start_combat(player, enemy, ai_engine=None):
    display_message(f"\n{Color.RED}{Color.BOLD}⚔ BATTLE COMMENCED: {enemy.name}! ⚔{Color.RESET}")
    
    if ai_engine and ai_engine.enabled:
        enemy_flavor = ai_engine.generate_enemy_flavor(enemy.name, player.level)
        if enemy_flavor:
            display_message(f"{Color.PURPLE}{enemy_flavor}{Color.RESET}")

    press_enter_to_continue()

    temp_player_def_buff = 0

    while player.is_alive() and enemy.is_alive():
        p_hp = render_bar(player.current_health, player.max_health, 15, Color.GREEN)
        p_mp = render_bar(player.current_magicka, player.max_magicka, 12, Color.BLUE)
        e_hp = render_bar(enemy.current_health, enemy.max_health, 18, Color.RED)

        combat_lines = [
            f"Hero: {Color.BOLD}{player.name}{Color.RESET}  | HP: {p_hp} | MP: {p_mp}",
            f"Foe:  {c_enemy(enemy.name)} | HP: {e_hp}"
        ]
        draw_box("COMBAT ARENA", combat_lines, width=64, border_color=Color.RED)

        action = get_input("Combat Command: (attack/magic/item/run)", ['attack', 'magic', 'item', 'run'])

        if action == 'attack':
            dmg = random.randint(player.get_total_attack() - 3, player.get_total_attack() + 3)
            # Critical Strike perk: 5% chance per level to deal 1.5x damage
            is_crit = random.random() < player.perks["critical_strike"] * 0.05
            if is_crit:
                dmg = int(dmg * 1.5)
            actual_dmg = enemy.take_damage(dmg)

            flavor = ai_engine.generate_combat_flavor(player.name, enemy.name, "Melee Strike", actual_dmg) if ai_engine and ai_engine.enabled else None
            if flavor:
                display_message(f"{Color.PURPLE}{flavor}{Color.RESET}")
            else:
                crit_text = f"{Color.YELLOW}{Color.BOLD}CRITICAL! {Color.RESET}" if is_crit else ""
                display_message(f"{crit_text}You hit {c_enemy(enemy.name)} for {Color.RED}{actual_dmg} damage{Color.RESET}!")

        elif action == 'magic':
            if not player.spells:
                display_message("No learned spells available!")
                continue
            
            spell_lines = [f"{i+1}. {s.name} ({s.school}) - Cost: {s.magicka_cost} MP | Power: {s.power}" for i, s in enumerate(player.spells)]
            draw_box("SPELLBOOK", spell_lines, width=60, border_color=Color.BLUE)

            choice = get_input("Cast spell # or 'back':", [str(i+1) for i in range(len(player.spells))] + ['back'])
            if choice == 'back':
                continue
            
            spell = player.spells[int(choice) - 1]
            # Mana Efficiency perk: -2 MP cost per level (minimum 1)
            magicka_cost = max(1, spell.magicka_cost - player.perks["mana_efficiency"] * 2)
            if player.current_magicka < magicka_cost:
                display_message(f"{Color.RED}Insufficient Magicka!{Color.RESET}")
                continue

            player.current_magicka -= magicka_cost
            # Spell Power perk: +5 power per level
            spell_power = spell.power + (player.intelligence * 2) + player.perks["spell_power"] * 5

            if spell.effect_type == "damage":
                actual_dmg = enemy.take_damage(spell_power)
                display_message(f"You cast {Color.BLUE}{spell.name}{Color.RESET}! Deals {Color.RED}{actual_dmg} magic damage{Color.RESET}.")
                _try_apply_status(enemy, spell)
            elif spell.effect_type == "drain":
                actual_dmg = enemy.take_damage(spell_power)
                drained = actual_dmg // 2
                player.heal(drained)
                display_message(f"You cast {Color.BLUE}{spell.name}{Color.RESET}! Deals {Color.RED}{actual_dmg} damage{Color.RESET} and siphons {Color.GREEN}{drained} HP{Color.RESET} back to you.")
            elif spell.effect_type == "heal":
                player.heal(spell_power)
                display_message(f"You cast {Color.BLUE}{spell.name}{Color.RESET} and recovered {Color.GREEN}{spell_power} HP{Color.RESET}.")
            elif spell.effect_type == "buff_defense":
                temp_player_def_buff += spell_power # Apply buff
                display_message(f"You cast {Color.BLUE}{spell.name}{Color.RESET}! Your defense is bolstered by {Color.CYAN}{spell_power}{Color.RESET}.")


        elif action == 'item':
            potions = [i for i in player.inventory if isinstance(i, Potion)]
            if not potions:
                display_message("No consumable potions in inventory!")
                continue
            
            p_lines = [f"{i+1}. {c_item(p.name)} - {p.description}" for i, p in enumerate(potions)]
            draw_box("POTIONS", p_lines, width=58, border_color=Color.YELLOW)

            choice = get_input("Use potion # or 'back':", [str(i+1) for i in range(len(potions))] + ['back'])
            if choice == 'back':
                continue
            potions[int(choice) - 1].use(player)

        elif action == 'run':
            if random.random() < 0.50:
                display_message(f"{Color.GREEN}Successfully fled from combat!{Color.RESET}")
                return False, None # Player fled, not defeated
            display_message(f"{Color.RED}Escape attempt failed!{Color.RESET}")

        enemy_turn_skipped = _process_enemy_status(enemy)

        if not enemy.is_alive():
            display_message(f"\n{Color.YELLOW}{Color.BOLD}★ VICTORY! Defeated {enemy.name}! ★{Color.RESET}")
            player.add_experience(enemy.exp_reward)
            player.gold += enemy.gold_reward
            for drop in enemy.drops:
                player.inventory.append(drop)
                display_message(f"Looted: {c_item(drop.name)}")
            press_enter_to_continue()
            return False, None # Player won, not defeated

        # Foe Turn Counter-Attack
        if not enemy_turn_skipped:
            display_message(f"\n{c_enemy(enemy.name)} attacks!")
            enemy_atk = max(1, enemy.attack - temp_player_def_buff)
            player_taken = player.take_damage(enemy_atk)
            display_message(f"{enemy.name} dealt {Color.RED}{player_taken} damage{Color.RESET} to you!")

        if not player.is_alive():
            display_message(f"\n{Color.RED}{Color.BOLD}YOU HAVE BEEN DEFEATED IN BATTLE...{Color.RESET}")
            press_enter_to_continue()
            return True, enemy.name # Player defeated, return enemy name

        press_enter_to_continue()

    return False, None # Combat ended, player not defeated (e.g., ran away)
