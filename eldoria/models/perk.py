"""A permanent bonus chosen by the player at certain level-ups (every 5 levels).

Perks are pickable more than once (see PlayerCharacter.perks, a dict of perk
-> stack count rather than a set).
"""
from __future__ import annotations

from enum import Enum


class Perk(Enum):
    POWER_ATTACK = ("Power Attack", "+2 attack bonus in melee -- you hit harder and more often.")
    IRON_SKIN = ("Iron Skin", "+1 armor class per rank -- your hide (or habits) have toughened.")
    QUICK_REFLEXES = ("Quick Reflexes", "+3 speed -- you react and move faster than most.")
    ARCANE_RESERVE = ("Arcane Reserve", "+2 willpower -- your reserve of magical focus deepens.")
    SILENT_STEP = ("Silent Step", "+15 Sneak -- you've learned to move without a sound.")
    TOUGHNESS = ("Toughness", "+15 max health -- you can simply take more punishment.")
    SECOND_WIND = ("Second Wind", "Once per rest, surviving a killing blow leaves you at 1 health instead of 0.")
    MASTER_TRADER = ("Master Trader", "Merchants give you noticeably better prices, buying and selling.")
    CRITICAL_FOCUS = (
        "Critical Focus",
        "Lowers the roll needed to land a critical hit by 1 per rank (crit on natural 20, then 19+, then 18+...).",
    )

    def __init__(self, display_name: str, description: str):
        self.display_name = display_name
        self.description = description
