from rpg_game.items import ANCIENT_RELIC, CITADEL_KEY, DRAGON_SCALE, SWAMP_HERB, SHIP_MANIFEST, ANCIENT_COMPASS, LOST_MINER_NOTE, GLOWING_MUSHROOM
from rpg_game.utils import display_message, Color, c_quest

class Quest:
    def __init__(self, name, description, reward_exp, reward_gold, reward_item=None, required_items=None):
        self.name = name
        self.description = description
        self.reward_exp = reward_exp
        self.reward_gold = reward_gold
        self.reward_item = reward_item
        self.required_items = required_items if required_items is not None else {} # {item_object: quantity}
        self.is_active = False
        self.is_completed = False

    def activate(self, player_level: int, ai_engine=None):
        self.is_active = True
        display_message(f"\n[QUEST ACCEPTED]: {c_quest(self.name)}")
        if ai_engine and ai_engine.enabled:
            ai_flavor = ai_engine.generate_quest_flavor(self.name, self.description, player_level, is_completion=False)
            if ai_flavor:
                display_message(f"{Color.PURPLE}Details: {ai_flavor}{Color.RESET}")
            else:
                display_message(f"Details: {self.description}")
        else:
            display_message(f"Details: {self.description}")

    def complete(self, player, ai_engine=None):
        # Check if player has required items
        if self.required_items:
            for item, quantity in self.required_items.items():
                if player.inventory.count(item) < quantity:
                    display_message(f"{Color.RED}You don't have enough {item.name} to complete this quest.{Color.RESET}")
                    return False
            # Remove required items
            for item, quantity in self.required_items.items():
                for _ in range(quantity):
                    player.inventory.remove(item)

        self.is_completed = True
        self.is_active = False
        display_message(f"\n{Color.YELLOW}{Color.BOLD}[QUEST COMPLETED]: {c_quest(self.name)}!{Color.RESET}")
        
        if ai_engine and ai_engine.enabled:
            ai_flavor = ai_engine.generate_quest_flavor(self.name, self.description, player.level, is_completion=True)
            if ai_flavor:
                display_message(f"{Color.PURPLE}{ai_flavor}{Color.RESET}")
        
        display_message(f"Rewards: {self.reward_exp} EXP, {self.reward_gold} Gold.")
        player.add_experience(self.reward_exp)
        player.gold += self.reward_gold
        if self.reward_item:
            player.inventory.append(self.reward_item)
            display_message(f"Reward Item Obtained: {self.reward_item.name}")
        return True

# --- QUEST SYSTEM DATABASE ---
QUEST_RELIC = Quest("The Ancient Relic", "Recover the Ancient Relic from deep within the Whispering Woods.", 150, 100, reward_item=CITADEL_KEY)
QUEST_GOBLINS = Quest("Goblin Outbreak", "Defeat at least 3 goblins terrorizing the road to Stonebridge.", 120, 80)
QUEST_MUSHROOMS = Quest("Alchemical Fungi", "Gather 2 Glowing Mushrooms from the Shadow Caves.", 100, 60, required_items={GLOWING_MUSHROOM: 2})
QUEST_DRAGON = Quest("Slay the Wyrm", "Defeat the Ancient Dragon resting atop Dragon's Peak.", 1000, 1000, reward_item=DRAGON_SCALE)

# New Quests
QUEST_POISONED_WATERS = Quest(
    "The Poisoned Waters",
    "Collect 3 Swamp Herbs from the Eastern Swamps to help purify Oakhaven's water supply.",
    180, 120,
    required_items={SWAMP_HERB: 3}
)
QUEST_LOST_CARGO = Quest(
    "Lost Cargo",
    "Find the Ship's Manifest from the Sunken Shipwreck near the Coastal Town.",
    250, 150,
    reward_item=None, # No item reward, just exp/gold for now
    required_items={SHIP_MANIFEST: 1}
)
QUEST_MOUNTAIN_RESCUE = Quest(
    "Mountain Rescue",
    "Find the Lost Miner in the Northern Mountain Pass and bring back his note.",
    300, 200,
    required_items={LOST_MINER_NOTE: 1}
)
QUEST_ANCIENT_COMPASS = Quest(
    "The Ancient Compass",
    "Retrieve the Ancient Compass from the Forgotten Crypt within the Ancient Ruins.",
    400, 300,
    reward_item=ANCIENT_COMPASS,
    required_items={ANCIENT_COMPASS: 1} # Player needs to pick it up and then "turn it in"
)


ALL_QUESTS = {
    "the_lost_relic": QUEST_RELIC,
    "goblin_menace": QUEST_GOBLINS,
    "alchemical_fungi": QUEST_MUSHROOMS,
    "slay_the_wyrm": QUEST_DRAGON,
    "poisoned_waters": QUEST_POISONED_WATERS,
    "lost_cargo": QUEST_LOST_CARGO,
    "mountain_rescue": QUEST_MOUNTAIN_RESCUE,
    "ancient_compass": QUEST_ANCIENT_COMPASS
}

def reset_quests():
    """Resets all quest progress (used when starting a new game)."""
    for quest in ALL_QUESTS.values():
        quest.is_active = False
        quest.is_completed = False

def get_quest_state():
    """Snapshot of quest progress for saving."""
    return {key: {'is_active': q.is_active, 'is_completed': q.is_completed} for key, q in ALL_QUESTS.items()}

def set_quest_state(state):
    """Restores quest progress from a save snapshot."""
    for key, flags in state.items():
        quest = ALL_QUESTS.get(key)
        if quest:
            quest.is_active = flags.get('is_active', False)
            quest.is_completed = flags.get('is_completed', False)
