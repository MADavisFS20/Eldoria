class Spell:
    def __init__(self, name, school, magicka_cost, power, effect_type="damage", description="", status_effect=None):
        self.name = name
        self.school = school
        self.magicka_cost = magicka_cost
        self.power = power
        self.effect_type = effect_type  # 'damage', 'heal', 'buff_defense', 'drain'
        self.description = description
        self.status_effect = status_effect  # 'burn', 'freeze', 'poison', 'drain'

# --- SPELL DATABASE ---
FIREBALL = Spell("Fireball", "Destruction", magicka_cost=20, power=30, effect_type="damage", description="Hurls a ball of fire causing heavy damage and burning.", status_effect="burn")
FROSTBITE = Spell("Frostbite", "Destruction", magicka_cost=15, power=20, effect_type="damage", description="Freezes target, reducing turn effectiveness.", status_effect="freeze")
LIGHTNING_BOLT = Spell("Lightning Bolt", "Destruction", magicka_cost=25, power=40, effect_type="damage", description="Strikes with precision electrical damage.")

FAST_HEAL = Spell("Fast Heal", "Restoration", magicka_cost=20, power=35, effect_type="heal", description="Restores player health rapidly.")
GREATER_HEAL = Spell("Greater Heal", "Restoration", magicka_cost=45, power=90, effect_type="heal", description="Mends severe wounds, restoring substantial health.")

STONEFLESH = Spell("Stoneflesh", "Alteration", magicka_cost=15, power=10, effect_type="buff_defense", description="Hardens skin to bolster defense for combat.")
ARCANE_SHIELD = Spell("Arcane Shield", "Alteration", magicka_cost=30, power=25, effect_type="buff_defense", description="Creates an energy barrier granting high defense.")

DRAIN_LIFE = Spell("Drain Life", "Necromancy", magicka_cost=25, power=25, effect_type="drain", description="Siphons life essence from enemy to restore health.", status_effect="drain")
POISON_DART = Spell("Poison Dart", "Necromancy", magicka_cost=18, power=15, effect_type="damage", description="Infects target with deadly lingering venom.", status_effect="poison")

HOLY_SMITE = Spell("Holy Smite", "Restoration", magicka_cost=35, power=50, effect_type="damage", description="Calls down sacred radiance to incinerate foes.")

ALL_SPELLS = {
    "fireball": FIREBALL,
    "frostbite": FROSTBITE,
    "lightning_bolt": LIGHTNING_BOLT,
    "fast_heal": FAST_HEAL,
    "greater_heal": GREATER_HEAL,
    "stoneflesh": STONEFLESH,
    "arcane_shield": ARCANE_SHIELD,
    "drain_life": DRAIN_LIFE,
    "poison_dart": POISON_DART,
    "holy_smite": HOLY_SMITE
}
