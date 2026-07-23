from rpg_game.items import IRON_SWORD, RUSTY_DAGGER, APPRENTICE_STAFF, WOODEN_SHIELD, CLOTH_ROBE, LEATHER_ARMOR, STEEL_PLATE
from rpg_game.spells import FIREBALL, FAST_HEAL, DRAIN_LIFE, STONEFLESH

class PlayerClass:
    def __init__(self, name, description, str_base, dex_base, int_base, con_base, wis_base, starting_weapon, starting_armor, starting_offhand=None, starting_spells=None):
        self.name = name
        self.description = description
        self.str_base = str_base
        self.dex_base = dex_base
        self.int_base = int_base
        self.con_base = con_base
        self.wis_base = wis_base
        self.starting_weapon = starting_weapon
        self.starting_armor = starting_armor
        self.starting_offhand = starting_offhand
        self.starting_spells = starting_spells if starting_spells else []

# --- CLASS DEFINITIONS ---
WARRIOR = PlayerClass(
    name="Warrior",
    description="A master of close combat with high health, defense, and physical prowess.",
    str_base=14, dex_base=10, int_base=6, con_base=14, wis_base=8,
    starting_weapon=IRON_SWORD, starting_armor=LEATHER_ARMOR, starting_offhand=WOODEN_SHIELD,
    starting_spells=[]
)

MAGE = PlayerClass(
    name="Mage",
    description="A scholar of mystical arts wielding destructive and protective incantations.",
    str_base=6, dex_base=8, int_base=16, con_base=8, wis_base=14,
    starting_weapon=APPRENTICE_STAFF, starting_armor=CLOTH_ROBE,
    starting_spells=[FIREBALL, STONEFLESH]
)

ROGUE = PlayerClass(
    name="Rogue",
    description="A swift, deadly skirmisher relying on speed, critical strikes, and agility.",
    str_base=10, dex_base=16, int_base=8, con_base=10, wis_base=8,
    starting_weapon=RUSTY_DAGGER, starting_armor=LEATHER_ARMOR,
    starting_spells=[]
)

PALADIN = PlayerClass(
    name="Paladin",
    description="A holy champion blending martial expertise with divine restoration magic.",
    str_base=12, dex_base=8, int_base=8, con_base=14, wis_base=12,
    starting_weapon=IRON_SWORD, starting_armor=STEEL_PLATE, starting_offhand=WOODEN_SHIELD,
    starting_spells=[FAST_HEAL]
)

NECROMANCER = PlayerClass(
    name="Necromancer",
    description="A dark practitioner utilizing life drainage, venomous spells, and dark rites.",
    str_base=6, dex_base=8, int_base=15, con_base=11, wis_base=12,
    starting_weapon=APPRENTICE_STAFF, starting_armor=CLOTH_ROBE,
    starting_spells=[DRAIN_LIFE]
)

ALL_CLASSES = {
    "1": WARRIOR,
    "2": MAGE,
    "3": ROGUE,
    "4": PALADIN,
    "5": NECROMANCER
}
