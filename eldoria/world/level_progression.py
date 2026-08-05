"""Character level (1..50): its own track, separate from skill mastery.

Defeating enemies and completing quests grants experience; enough banked xp
levels the character up. A level-up bumps every basic stat slightly, and
each level demands more xp than the last.
"""
from __future__ import annotations

import random
from dataclasses import replace

from eldoria.models import DiceFormula, DieType, PlayerCharacter, StatBlock

MAX_CHARACTER_LEVEL = 50


def xp_to_next_level(level: int) -> int:
    """Banked xp required to advance from `level` to `level + 1`."""
    return level * level * 20 + 100


def xp_for_defeating(tier: int, rng: random.Random) -> int:
    """Xp a kill of the given world difficulty tier (1..5) pays out. Harder tier, bigger reward."""
    t = max(1, min(5, tier))
    return DiceFormula(t, DieType.D20, t * 10).roll(rng) * t


def apply_experience(player: PlayerCharacter, xp_gained: int, rng: random.Random) -> PlayerCharacter:
    """Apply a batch of xp (from a kill, a quest reward, whatever), leveling up as many times as it covers."""
    level = player.level
    xp = player.experience + xp_gained
    strength = player.strength
    agility = player.agility
    willpower = player.willpower
    max_health = player.max_health
    current_health = player.current_health
    max_stamina = player.max_stamina
    current_stamina = player.current_stamina
    pending_perk_choices = player.pending_perk_choices

    while level < MAX_CHARACTER_LEVEL and xp >= xp_to_next_level(level):
        xp -= xp_to_next_level(level)
        level += 1

        health_gain = DiceFormula(2, DieType.D8, 3).roll(rng)
        max_health += health_gain
        current_health += health_gain
        stamina_gain = DiceFormula(1, DieType.D8, 2).roll(rng)
        max_stamina += stamina_gain
        current_stamina += stamina_gain
        if DiceFormula(1, DieType.D20).roll(rng) <= 12:  # ~60% chance
            strength += 1
        if DiceFormula(1, DieType.D20).roll(rng) <= 8:  # ~40% chance
            agility += 1
        if DiceFormula(1, DieType.D20).roll(rng) <= 8:  # ~40% chance
            willpower += 1
        if level % 5 == 0:
            pending_perk_choices += 1

    if level >= MAX_CHARACTER_LEVEL:
        level = MAX_CHARACTER_LEVEL
        xp = 0

    str_mod = StatBlock.modifier_of(strength)
    agi_mod = StatBlock.modifier_of(agility)
    armor_class = 10 + agi_mod + level // 5
    attack_bonus = level // 4 + str_mod
    speed = max(5, 20 + agi_mod * 2 + level // 10)
    unarmed_damage = DiceFormula(1 + level // 15, DieType.D6 if level < 25 else DieType.D8, str_mod)

    return replace(
        player,
        level=level,
        experience=xp,
        strength=strength,
        agility=agility,
        willpower=willpower,
        max_health=max_health,
        current_health=current_health,
        max_stamina=max_stamina,
        current_stamina=current_stamina,
        armor_class=armor_class,
        speed=speed,
        attack_bonus=attack_bonus,
        unarmed_damage=unarmed_damage,
        pending_perk_choices=pending_perk_choices,
    )
