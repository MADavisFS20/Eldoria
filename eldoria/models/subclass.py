"""An optional curse/gift a character can request from the one NPC in the world who offers it.

Mutually exclusive and permanent -- once chosen, PlayerCharacter.subclass is
set for good and the other option is no longer available to that character.
"""
from __future__ import annotations

from enum import Enum


class Subclass(Enum):
    VAMPIRE = (
        "Vampire",
        "The bite took hold, and something ancient and hungry now moves beneath your skin.",
        "Unnaturally swift and graceful, and every wound you deal feeds something back into you.",
        "Frailer than you look underneath the borrowed strength, and no less easy to kill for it.",
        0, 3, 1, -4, -1, 15, 0,
    )
    WEREWOLF = (
        "Werewolf",
        "The curse runs hot in your blood now -- on a bad night you can feel the shape underneath your own.",
        "Ferocious and hard to put down, especially once you're bleeding.",
        "The beast rides closer to the surface than you'd like -- your focus and your guard both suffer for it.",
        4, 0, -2, 15, -1, 0, 3,
    )

    def __init__(
        self,
        display_name: str,
        lore: str,
        strength_description: str,
        weakness_description: str,
        strength_bonus: int,
        agility_bonus: int,
        willpower_bonus: int,
        max_health_bonus: int,
        armor_class_bonus: int,
        lifesteal_percent: int,
        low_health_rage_bonus: int,
    ):
        self.display_name = display_name
        self.lore = lore
        self.strength_description = strength_description
        self.weakness_description = weakness_description
        self.strength_bonus = strength_bonus
        self.agility_bonus = agility_bonus
        self.willpower_bonus = willpower_bonus
        self.max_health_bonus = max_health_bonus
        self.armor_class_bonus = armor_class_bonus
        self.lifesteal_percent = lifesteal_percent
        self.low_health_rage_bonus = low_health_rage_bonus
