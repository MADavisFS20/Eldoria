from rpg_game.items import Weapon, Armor, Accessory, Potion, Equipment
from rpg_game.utils import (
    draw_box, render_bar, Color, c_item, display_message, get_input, c_perk,
    clear_screen
)

class Player:
    def __init__(self, name="Hero", player_class=None):
        self.name = name
        self.player_class = player_class
        
        self.strength = player_class.str_base if player_class else 10
        self.dexterity = player_class.dex_base if player_class else 10
        self.intelligence = player_class.int_base if player_class else 10
        self.constitution = player_class.con_base if player_class else 10
        self.wisdom = player_class.wis_base if player_class else 10

        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.attribute_points = 0
        self.perk_points = 0
        self.gold = 100

        self.equipment = {
            "weapon": None, "offhand": None, "chest": None,
            "head": None, "ring": None, "amulet": None
        }

        self.recalculate_stats()
        self.current_health = self.max_health
        self.current_magicka = self.max_magicka
        self.current_stamina = self.max_stamina

        self.inventory = []
        self.spells = []
        self.perks = {"critical_strike": 0, "spell_power": 0, "iron_skin": 0, "mana_efficiency": 0}

        if player_class:
            if player_class.starting_weapon:
                self.equip(player_class.starting_weapon, silent=True)
            if player_class.starting_armor:
                self.equip(player_class.starting_armor, silent=True)
            if player_class.starting_offhand:
                self.equip(player_class.starting_offhand, silent=True)
            for sp in player_class.starting_spells:
                self.learn_spell(sp)

    def recalculate_stats(self):
        hp_bonus = mp_bonus = sta_bonus = 0
        for eq in self.equipment.values():
            if isinstance(eq, Accessory):
                hp_bonus += eq.hp_bonus
                mp_bonus += eq.mp_bonus
                sta_bonus += eq.sta_bonus
        self.max_health = 80 + (self.constitution * 12) + hp_bonus
        self.max_magicka = 40 + (self.intelligence * 10) + (self.wisdom * 5) + mp_bonus
        self.max_stamina = 50 + (self.dexterity * 8) + (self.constitution * 4) + sta_bonus
        self.current_health = min(getattr(self, 'current_health', self.max_health), self.max_health)
        self.current_magicka = min(getattr(self, 'current_magicka', self.max_magicka), self.max_magicka)
        self.current_stamina = min(getattr(self, 'current_stamina', self.max_stamina), self.max_stamina)

    def learn_spell(self, spell):
        if spell not in self.spells:
            self.spells.append(spell)

    def equip(self, equipment, silent=False):
        if not isinstance(equipment, Equipment):
            return
        slot = equipment.slot

        # Two-handed weapons occupy the offhand slot as well
        if slot == "offhand":
            weapon = self.equipment["weapon"]
            if isinstance(weapon, Weapon) and not weapon.is_one_handed:
                if not silent:
                    display_message(f"{Color.RED}You cannot use an offhand while wielding the two-handed {c_item(weapon.name)}.{Color.RESET}")
                return
        if isinstance(equipment, Weapon) and not equipment.is_one_handed and self.equipment["offhand"]:
            old_offhand = self.equipment["offhand"]
            self.equipment["offhand"] = None
            self.inventory.append(old_offhand)
            if not silent:
                display_message(f"Unequipped {c_item(old_offhand.name)} (two-handed weapon needs both hands).")

        if self.equipment[slot]:
            old_item = self.equipment[slot]
            self.inventory.append(old_item)
            if not silent:
                display_message(f"Unequipped {c_item(old_item.name)}.")

        self.equipment[slot] = equipment
        if equipment in self.inventory:
            self.inventory.remove(equipment)
        self.recalculate_stats()
        if not silent:
            display_message(f"Equipped {c_item(equipment.name)} to {slot.upper()}.")

    def get_total_attack(self):
        base_atk = self.strength * 1.5 + (self.dexterity * 0.8)
        weapon_atk = self.equipment["weapon"].damage if isinstance(self.equipment["weapon"], Weapon) else 0
        ring_bonus = self.equipment["ring"].atk_bonus if isinstance(self.equipment["ring"], Accessory) else 0
        perk_bonus = self.perks["critical_strike"] * 3
        return int(base_atk + weapon_atk + ring_bonus + perk_bonus)

    def get_total_defense(self):
        base_def = self.constitution * 0.5
        chest_def = self.equipment["chest"].defense if isinstance(self.equipment["chest"], Armor) else 0
        offhand_def = self.equipment["offhand"].defense if isinstance(self.equipment["offhand"], Armor) else 0
        head_def = self.equipment["head"].defense if isinstance(self.equipment["head"], Armor) else 0
        ring_def = self.equipment["ring"].def_bonus if isinstance(self.equipment["ring"], Accessory) else 0
        perk_def = self.perks["iron_skin"] * 4
        return int(base_def + chest_def + offhand_def + head_def + ring_def + perk_def)

    def take_damage(self, damage):
        actual = max(1, damage - self.get_total_defense())
        self.current_health = max(0, self.current_health - actual)
        return actual

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)

    def restore_magicka(self, amount):
        self.current_magicka = min(self.max_magicka, self.current_magicka + amount)

    def restore_stamina(self, amount):
        self.current_stamina = min(self.max_stamina, self.current_stamina + amount)

    def is_alive(self):
        return self.current_health > 0

    def add_experience(self, amount):
        self.experience += amount
        display_message(f"{Color.GREEN}+ {amount} Experience Points{Color.RESET}")
        while self.experience >= self.experience_to_next:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.4)
        self.attribute_points += 3
        self.perk_points += 1
        self.recalculate_stats()
        self.current_health, self.current_magicka, self.current_stamina = self.max_health, self.max_magicka, self.max_stamina
        display_message(f"\n{Color.YELLOW}{Color.BOLD}★ LEVEL UP! You are now Level {self.level}! ★{Color.RESET}")

    def display_stats(self):
        cls_name = self.player_class.name if self.player_class else "None"
        hp_bar = render_bar(self.current_health, self.max_health, 18, Color.RED)
        mp_bar = render_bar(self.current_magicka, self.max_magicka, 18, Color.BLUE)
        sp_bar = render_bar(self.current_stamina, self.max_stamina, 18, Color.STAMINA)

        lines = [
            f"Class: {Color.BOLD}{cls_name}{Color.RESET} | Level: {self.level} | EXP: {self.experience}/{self.experience_to_next}",
            f"HP: {hp_bar}",
            f"MP: {mp_bar}",
            f"SP: {sp_bar}",
            "────────────────────────────────────────────────────────",
            f"ATK: {Color.RED}{self.get_total_attack()}{Color.RESET} | DEF: {Color.CYAN}{self.get_total_defense()}{Color.RESET} | Gold: {Color.YELLOW}{self.gold}g{Color.RESET}",
            f"STR: {self.strength} | DEX: {self.dexterity} | INT: {self.intelligence} | CON: {self.constitution} | WIS: {self.wisdom}",
            f"Unspent Points: Attributes ({self.attribute_points}) | Perks ({self.perk_points})",
            "────────────────────────────────────────────────────────",
            "EQUIPMENT:",
            f"  Weapon: {c_item(self.equipment['weapon'].name if self.equipment['weapon'] else 'Empty')}",
            f"  Chest:  {c_item(self.equipment['chest'].name if self.equipment['chest'] else 'Empty')}",
            f"  Head:   {c_item(self.equipment['head'].name if self.equipment['head'] else 'Empty')}",
            f"  Offhand:{c_item(self.equipment['offhand'].name if self.equipment['offhand'] else 'Empty')}",
            f"  Ring:   {c_item(self.equipment['ring'].name if self.equipment['ring'] else 'Empty')}",
            f"  Amulet: {c_item(self.equipment['amulet'].name if self.equipment['amulet'] else 'Empty')}"
        ]
        draw_box(f"CHARACTER SHEET: {self.name.upper()}", lines, width=64)

    def display_inventory(self, ai_engine=None):
        if not self.inventory:
            display_message(f"\n{Color.GRAY}Your inventory is empty.{Color.RESET}")
            return

        lines = []
        for i, item in enumerate(self.inventory):
            item_type = type(item).__name__
            if ai_engine and ai_engine.enabled:
                ai_description = ai_engine.generate_item_flavor(item.name, item.description, item_type)
                description_to_use = ai_description if ai_description else item.description
            else:
                description_to_use = item.description
            lines.append(f"{i+1}. {c_item(item.name)} ({item_type}) - {Color.GRAY}{description_to_use}{Color.RESET}")

        draw_box("INVENTORY", lines, width=68)

    def choose_equipment_to_wear(self):
        equippable = [i for i in self.inventory if isinstance(i, Equipment)]
        if not equippable:
            display_message(f"{Color.GRAY}You have no equippable items in your inventory.{Color.RESET}")
            return

        lines = [f"{i+1}. {c_item(item.name)} [{item.slot}] - {Color.GRAY}{item.description}{Color.RESET}" for i, item in enumerate(equippable)]
        draw_box("EQUIP ITEM", lines, width=68)
        choice = get_input("Select item # to equip (or 'back'):", [str(i+1) for i in range(len(equippable))] + ['back'])
        if choice == 'back':
            return
        self.equip(equippable[int(choice) - 1])

    def use_item_from_inventory(self):
        usable = [i for i in self.inventory if isinstance(i, Potion)]
        if not usable:
            display_message(f"{Color.GRAY}You have no usable items (potions) in your inventory.{Color.RESET}")
            return

        lines = [f"{i+1}. {c_item(p.name)} - {Color.GRAY}{p.description}{Color.RESET}" for i, p in enumerate(usable)]
        draw_box("USE ITEM", lines, width=68)
        choice = get_input("Select item # to use (or 'back'):", [str(i+1) for i in range(len(usable))] + ['back'])
        if choice == 'back':
            return
        potion = usable[int(choice) - 1]
        potion.use(self)
        display_message(f"{Color.GREEN}Used {c_item(potion.name)}.{Color.RESET}")

    def spend_attribute_points(self):
        if self.attribute_points == 0:
            display_message(f"{Color.GRAY}You have no attribute points to spend.{Color.RESET}")
            return
        attributes = ["strength", "dexterity", "intelligence", "constitution", "wisdom"]
        while self.attribute_points > 0:
            clear_screen()
            attr_lines = [
                f"Available Attribute Points: {Color.YELLOW}{self.attribute_points}{Color.RESET}",
                "────────────────────────────────────────────────────────"
            ]
            for i, attr in enumerate(attributes):
                attr_lines.append(f"{i+1}. {attr.title()}: {getattr(self, attr)}")
            draw_box("SPEND ATTRIBUTE POINTS", attr_lines, width=64)

            choice = get_input("Select an attribute to raise (or 'back' to exit):", [str(i+1) for i in range(len(attributes))] + ['back'])
            if choice == 'back':
                return
            attr = attributes[int(choice) - 1]
            setattr(self, attr, getattr(self, attr) + 1)
            self.attribute_points -= 1
            self.recalculate_stats()
            display_message(f"{Color.GREEN}{attr.title()} raised to {getattr(self, attr)}!{Color.RESET}")
        display_message(f"{Color.GRAY}All attribute points spent.{Color.RESET}")

    def spend_perk_points(self, ai_engine=None):
        if self.perk_points == 0:
            display_message(f"{Color.GRAY}You have no perk points to spend.{Color.RESET}")
            return

        perk_base_descriptions = {
            "critical_strike": "Increases critical strike chance and damage.",
            "spell_power": "Increases the power of your spells.",
            "iron_skin": "Increases your physical defense.",
            "mana_efficiency": "Reduces the magicka cost of your spells."
        }

        while True:
            clear_screen()
            perk_lines = [
                f"Available Perk Points: {Color.PERK}{self.perk_points}{Color.RESET}",
                "────────────────────────────────────────────────────────"
            ]
            perk_options = []
            for i, (perk_name, level) in enumerate(self.perks.items()):
                display_name = perk_name.replace('_', ' ').title()
                
                description_to_use = perk_base_descriptions[perk_name]
                if ai_engine and ai_engine.enabled:
                    ai_flavor = ai_engine.generate_perk_flavor(display_name, perk_base_descriptions[perk_name], level)
                    if ai_flavor:
                        description_to_use = ai_flavor

                perk_lines.append(f"{i+1}. {c_perk(display_name)} (Level: {level}) - {description_to_use}")
                perk_options.append(str(i+1))
            
            draw_box("SPEND PERK POINTS", perk_lines, width=70)

            choice = get_input("Select a perk to upgrade (or 'back' to exit):", perk_options + ['back'])

            if choice == 'back':
                break
            
            try:
                perk_index = int(choice) - 1
                selected_perk_name = list(self.perks.keys())[perk_index]

                if self.perk_points >= 1:
                    self.perks[selected_perk_name] += 1
                    self.perk_points -= 1
                    display_message(f"{Color.GREEN}Upgraded {c_perk(selected_perk_name.replace('_', ' ').title())} to Level {self.perks[selected_perk_name]}!{Color.RESET}")
                else:
                    display_message(f"{Color.RED}You do not have enough perk points to upgrade {c_perk(selected_perk_name.replace('_', ' ').title())}.{Color.RESET}")
            except (ValueError, IndexError):
                display_message(f"{Color.RED}Invalid selection.{Color.RESET}")
            
            input(f"\n{Color.GRAY}[Press Enter to continue...]{Color.RESET}")
