from rpg_game.items import ANCIENT_RELIC, CITADEL_KEY, DRAGON_SCALE

class Quest:
    def __init__(self, name, description, reward_exp, reward_gold, reward_item=None):
        self.name = name
        self.description = description
        self.reward_exp = reward_exp
        self.reward_gold = reward_gold
        self.reward_item = reward_item
        self.is_active = False
        self.is_completed = False

    def activate(self):
        self.is_active = True
        print(f"\n[QUEST ACCEPTED]: {self.name}")
        print(f"Details: {self.description}")

    def complete(self, player):
        self.is_completed = True
        self.is_active = False
        print(f"\n[QUEST COMPLETED]: {self.name}!")
        print(f"Rewards: {self.reward_exp} EXP, {self.reward_gold} Gold.")
        player.add_experience(self.reward_exp)
        player.gold += self.reward_gold
        if self.reward_item:
            player.inventory.append(self.reward_item)
            print(f"Reward Item Obtained: {self.reward_item.name}")

# --- QUEST SYSTEM DATABASE ---
QUEST_RELIC = Quest("The Ancient Relic", "Recover the Ancient Relic from deep within the Whispering Woods.", 150, 100, reward_item=CITADEL_KEY)
QUEST_GOBLINS = Quest("Goblin Outbreak", "Defeat at least 3 goblins terrorizing the road to Stonebridge.", 120, 80)
QUEST_MUSHROOMS = Quest("Alchemical Fungi", "Gather 2 Glowing Mushrooms from the Shadow Caves.", 100, 60)
QUEST_DRAGON = Quest("Slay the Wyrm", "Defeat the Ancient Dragon resting atop Dragon's Peak.", 1000, 1000, reward_item=DRAGON_SCALE)

ALL_QUESTS = {
    "the_lost_relic": QUEST_RELIC,
    "goblin_menace": QUEST_GOBLINS,
    "alchemical_fungi": QUEST_MUSHROOMS,
    "slay_the_wyrm": QUEST_DRAGON
}
