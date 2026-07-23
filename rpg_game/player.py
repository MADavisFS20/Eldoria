from rpg_game.items import Weapon, Armor, Accessory, Potion, Equipment

class Player:
    def __init__(self, name="Hero", player_class=None):
        self.name = name
        self.player_class = player_class
        
        # Attributes
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

        # Derived Pools
        self.recalculate_stats()
        self.current_health = self.max_health
        self.current_magicka = self.max_magicka
        self.current_stamina = self.max_stamina

        # Equipment Slots
        self.equipment = {
            "weapon": None,
            "offhand": None,
            "chest": None,
            "head": None,
            "ring": None,
            "amulet": None
        }

        self.inventory = []
        self.spells = []
        self.perks = {
            "critical_strike": 0,
            "spell_power": 0,
            "iron_skin": 0,
            "mana_efficiency": 0
        }

        # Apply class initial equipment and spells
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
        self.max_health = 80 + (self.constitution * 12)
        self.max_magicka = 40 + (self.intelligence * 10) + (self.wisdom * 5)
        self.max_stamina = 50 + (self.dexterity * 8) + (self.constitution * 4)

    def learn_spell(self, spell):
        if spell not in self.spells:
            self.spells.append(spell)

    def equip(self, equipment, silent=False):
        if not isinstance(equipment, Equipment):
            return
        slot = equipment.slot
        if self.equipment[slot]:
            old_item = self.equipment[slot]
            self.inventory.append(old_item)
            if not silent:
                print(f"Unequipped {old_item.name}.")
        
        self.equipment[slot] = equipment
        if equipment in self.inventory:
            self.inventory.remove(equipment)
        if not silent:
            print(f"Equipped {equipment.name} into {slot.upper()} slot.")

    def get_total_attack(self):
        base_atk = self.strength * 1.5 + (self.dexterity * 0.8)
        weapon = self.equipment["weapon"]
        weapon_atk = weapon.damage if isinstance(weapon, Weapon) else 0
        ring_bonus = self.equipment["ring"].atk_bonus if self.equipment["ring"] else 0
        perk_bonus = self.perks["critical_strike"] * 3
        return int(base_atk + weapon_atk + ring_bonus + perk_bonus)

    def get_total_defense(self):
        base_def = self.constitution * 0.5
        chest_def = self.equipment["chest"].defense if isinstance(self.equipment["chest"], Armor) else 0
        offhand_def = self.equipment["offhand"].defense if isinstance(self.equipment["offhand"], Armor) else 0
        head_def = self.equipment["head"].defense if isinstance(self.equipment["head"], Armor) else 0
        ring_def = self.equipment["ring"].def_bonus if self.equipment["ring"] else 0
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
        print(f"Gained {amount} Experience Points.")
        while self.experience >= self.experience_to_next:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next
        self.experience_to_next = int(self.experience_to_next * 1.4)
        self.attribute_points += 3
        self.perk_points += 1
        
        self.recalculate_stats()
        self.current_health = self.max_health
        self.current_magicka = self.max_magicka
        self.current_stamina = self.max_stamina

        print(f"\n*** LEVEL UP! You reached Level {self.level}! ***")
        print("Gained +3 Attribute Points and +1 Perk Point! Health & Magicka fully restored.")

    def spend_attribute_points(self):
        while self.attribute_points > 0:
            print(f"\n--- Attribute Allocation ({self.attribute_points} Points Available) ---")
            print(f"1. Strength: {self.strength}")
            print(f"2. Dexterity: {self.dexterity}")
            print(f"3. Intelligence: {self.intelligence}")
            print(f"4. Constitution: {self.constitution}")
            print(f"5. Wisdom: {self.wisdom}")
            print("6. Done")
            
            choice = input("Select attribute to upgrade (1-6): ").strip()
            if choice == "1":
                self.strength += 1; self.attribute_points -= 1
            elif choice == "2":
                self.dexterity += 1; self.attribute_points -= 1
            elif choice == "3":
                self.intelligence += 1; self.attribute_points -= 1
            elif choice == "4":
                self.constitution += 1; self.attribute_points -= 1
            elif choice == "5":
                self.wisdom += 1; self.attribute_points -= 1
            elif choice == "6":
                break
            self.recalculate_stats()

    def spend_perk_points(self):
        while self.perk_points > 0:
            print(f"\n--- Perk Upgrades ({self.perk_points} Perk Points Available) ---")
            print(f"1. Critical Strike (Lvl {self.perks['critical_strike']}) - Boosts melee attack power.")
            print(f"2. Spell Power (Lvl {self.perks['spell_power']}) - Increases magic damage & healing.")
            print(f"3. Iron Skin (Lvl {self.perks['iron_skin']}) - Boosts physical defense.")
            print(f"4. Mana Efficiency (Lvl {self.perks['mana_efficiency']}) - Reduces spell cost.")
            print("5. Done")

            choice = input("Select perk to upgrade (1-5): ").strip()
            if choice == "1":
                self.perks['critical_strike'] += 1; self.perk_points -= 1
            elif choice == "2":
                self.perks['spell_power'] += 1; self.perk_points -= 1
            elif choice == "3":
                self.perks['iron_skin'] += 1; self.perk_points -= 1
            elif choice == "4":
                self.perks['mana_efficiency'] += 1; self.perk_points -= 1
            elif choice == "5":
                break

    def display_stats(self):
        print(f"\n==================== {self.name.upper()} ====================")
        print(f"Class: {self.player_class.name if self.player_class else 'None'} | Level: {self.level} | EXP: {self.experience}/{self.experience_to_next}")
        print(f"Health: {self.current_health}/{self.max_health} | Magicka: {self.current_magicka}/{self.max_magicka} | Stamina: {self.current_stamina}/{self.max_stamina}")
        print(f"Attack Power: {self.get_total_attack()} | Defense: {self.get_total_defense()} | Gold: {self.gold}")
        print(f"Attributes: STR: {self.strength} | DEX: {self.dexterity} | INT: {self.intelligence} | CON: {self.constitution} | WIS: {self.wisdom}")
        print(f"Unspent Points: Attribute Points ({self.attribute_points}) | Perk Points ({self.perk_points})")
        print("Equipped Equipment:")
        for slot, item in self.equipment.items():
            print(f"  - {slot.capitalize()}: {item.name if item else 'Empty'}")
        print("==========================================================")

    def display_inventory(self):
        if not self.inventory:
            print("\nYour inventory is empty.")
            return

        print("\n--- Inventory Items ---")
        for i, item in enumerate(self.inventory):
            print(f"{i+1}. {item.name} ({type(item).__name__}) - {item.description}")
        print("-----------------------")

        while True:
            choice = input("Enter item number to use/equip, or 'back': ").strip().lower()
            if choice == 'back':
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.inventory):
                    item = self.inventory[idx]
                    if isinstance(item, Equipment):
                        self.equip(item)
                    elif isinstance(item, Potion):
                        item.use(self)
                    else:
                        print(f"You examine {item.name}: {item.description}")
                    break
            except ValueError:
                print("Invalid input.")
