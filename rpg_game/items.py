class Item:
    def __init__(self, name, description, value=0, weight=1.0):
        self.name = name
        self.description = description
        self.value = value
        self.weight = weight

    def __str__(self):
        return self.name

class Equipment(Item):
    def __init__(self, name, description, slot, value=0, weight=1.0):
        super().__init__(name, description, value, weight)
        self.slot = slot  # 'head', 'chest', 'weapon', 'offhand', 'ring', 'amulet'

class Weapon(Equipment):
    def __init__(self, name, description, damage, weapon_type="sword", is_one_handed=True, value=0, weight=5.0):
        super().__init__(name, description, slot="weapon", value=value, weight=weight)
        self.damage = damage
        self.weapon_type = weapon_type  # 'sword', 'dagger', 'staff', 'greatsword', 'mace', 'axe', 'bow'
        self.is_one_handed = is_one_handed

class Armor(Equipment):
    def __init__(self, name, description, defense, slot="chest", value=0, weight=8.0):
        super().__init__(name, description, slot=slot, value=value, weight=weight)
        self.defense = defense

class Accessory(Equipment):
    def __init__(self, name, description, slot="ring", hp_bonus=0, mp_bonus=0, atk_bonus=0, def_bonus=0, sta_bonus=0, value=0):
        super().__init__(name, description, slot=slot, value=value, weight=0.5)
        self.hp_bonus = hp_bonus
        self.mp_bonus = mp_bonus
        self.atk_bonus = atk_bonus
        self.def_bonus = def_bonus
        self.sta_bonus = sta_bonus

class Potion(Item):
    def __init__(self, name, description, amount, potion_type="health", value=0):
        super().__init__(name, description, value=value, weight=0.5)
        self.amount = amount
        self.potion_type = potion_type  # 'health', 'magicka', 'stamina', 'elixir'

    def use(self, player):
        if self.potion_type == "health":
            player.heal(self.amount)
        elif self.potion_type == "magicka":
            player.restore_magicka(self.amount)
        elif self.potion_type == "stamina":
            player.restore_stamina(self.amount)
        elif self.potion_type == "elixir":
            player.heal(self.amount)
            player.restore_magicka(self.amount)
            player.restore_stamina(self.amount) # Elixir also restores stamina
        if self in player.inventory:
            player.inventory.remove(self)

# --- GLOBAL ITEM CATALOG ---
# Weapons
RUSTY_DAGGER = Weapon("Rusty Dagger", "A corroded small blade.", damage=6, weapon_type="dagger", is_one_handed=True, value=10)
IRON_SWORD = Weapon("Iron Sword", "Standard forged iron sword.", damage=12, weapon_type="sword", is_one_handed=True, value=45)
STEEL_GREATSWORD = Weapon("Steel Greatsword", "Heavy two-handed steel blade.", damage=26, weapon_type="greatsword", is_one_handed=False, value=150)
APPRENTICE_STAFF = Weapon("Apprentice Staff", "Focus staff boosting spell resonance.", damage=8, weapon_type="staff", is_one_handed=True, value=60)
RUNIC_WARHAMMER = Weapon("Runic Warhammer", "Engraved hammer imbued with blunt force.", damage=34, weapon_type="mace", is_one_handed=False, value=300)
DRAGON_FANG_BLADE = Weapon("Dragon Fang Blade", "Forged from dragon tooth.", damage=45, weapon_type="sword", is_one_handed=True, value=750)
WAR_AXE = Weapon("Warrior's Axe", "A sturdy axe, good for cleaving.", damage=18, weapon_type="axe", is_one_handed=True, value=80)
SHORT_BOW = Weapon("Short Bow", "A simple bow for ranged attacks.", damage=10, weapon_type="bow", is_one_handed=False, value=50) # Bows are generally two-handed in RPGs

# Shields & Offhands
WOODEN_SHIELD = Armor("Wooden Shield", "Basic wooden defender.", defense=4, slot="offhand", value=20)
TOWER_SHIELD = Armor("Steel Tower Shield", "Massive iron barricade shield.", defense=12, slot="offhand", value=180)

# Armor & Helmets
CLOTH_ROBE = Armor("Cloth Robe", "Simple woven spellcaster robe.", defense=2, slot="chest", value=15)
LEATHER_ARMOR = Armor("Leather Armor", "Tanned leather hide.", defense=8, slot="chest", value=50)
STEEL_PLATE = Armor("Steel Plate Armor", "Heavy protective steel plate.", defense=22, slot="chest", value=250)
DRAGONSCALE_ARMOR = Armor("Dragonscale Armor", "Lightweight dragon scales.", defense=35, slot="chest", value=850)
IRON_HELMET = Armor("Iron Helmet", "Provides head protection.", defense=5, slot="head", value=40)
LEATHER_HELMET = Armor("Leather Hood", "A simple leather hood for head protection.", defense=3, slot="head", value=25)
CHAINMAIL_ARMOR = Armor("Chainmail Armor", "Interlocking metal rings provide decent protection.", defense=15, slot="chest", value=150)

# Accessories
RING_OF_HEALTH = Accessory("Ring of Vitality", "Increases max health.", slot="ring", hp_bonus=30, value=100)
RING_OF_POWER = Accessory("Ring of Power", "Increases attack output.", slot="ring", atk_bonus=6, value=150)
AMULET_OF_MANA = Accessory("Amulet of Arcana", "Increases max magicka.", slot="amulet", mp_bonus=40, value=120)
AMULET_OF_STAMINA = Accessory("Amulet of Vigor", "Increases max stamina.", slot="amulet", sta_bonus=30, value=110)
RING_OF_DEFENSE = Accessory("Ring of Protection", "Increases defense.", slot="ring", def_bonus=4, value=90)

# Potions
HEALTH_POTION_S = Potion("Small Health Potion", "Restores 30 Health.", amount=30, potion_type="health", value=20)
HEALTH_POTION_M = Potion("Medium Health Potion", "Restores 75 Health.", amount=75, potion_type="health", value=50)
HEALTH_POTION_L = Potion("Large Health Potion", "Restores 150 Health.", amount=150, potion_type="health", value=120)
MANA_POTION_S = Potion("Small Mana Potion", "Restores 30 Magicka.", amount=30, potion_type="magicka", value=20)
MANA_POTION_M = Potion("Medium Mana Potion", "Restores 75 Magicka.", amount=75, potion_type="magicka", value=50)
STAMINA_POTION_S = Potion("Small Stamina Potion", "Restores 30 Stamina.", amount=30, potion_type="stamina", value=20)
ELIXIR_OF_LIFE = Potion("Elixir of Life", "Restores 200 HP, MP, and SP.", amount=200, potion_type="elixir", value=250)

# Crafting & Quest Items
GOBLIN_EAR = Item("Goblin Ear", "Trophy from a slain goblin.", value=10)
ANCIENT_RELIC = Item("Ancient Relic", "Radiates old magical aura.", value=200)
GLOWING_MUSHROOM = Item("Glowing Mushroom", "Luminous fungi from damp caves.", value=15)
CITADEL_KEY = Item("Citadel Gate Key", "Heavy iron key to the Citadel inner courtyard.", value=0)
DRAGON_SCALE = Item("Dragon Scale", "Extremely tough dragon scale.", value=150)
SWAMP_HERB = Item("Swamp Herb", "A pungent herb found in marshy areas.", value=5)
SHIP_MANIFEST = Item("Ship's Manifest", "A waterlogged document detailing cargo.", value=0)
ANCIENT_COMPASS = Item("Ancient Compass", "An old compass that hums with faint magic.", value=0)
MINER_PICKAXE = Item("Miner's Pickaxe", "A sturdy pickaxe, well-used.", value=30)
LOST_MINER_NOTE = Item("Lost Miner's Note", "A crumpled note from a lost miner.", value=0)
