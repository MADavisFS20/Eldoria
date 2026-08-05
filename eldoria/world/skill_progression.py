""""The more a skill is used, the higher it levels" -- this is the whole mechanic.

Every skill runs 1..100. Deliberately independent of character level/combat
XP -- see level_progression for that track.
"""
from __future__ import annotations

import random
from dataclasses import replace

from eldoria.models import DiceFormula, DieType, PlayerCharacter, Race, Skill, SkillType

MAX_SKILL_LEVEL = 100


def xp_to_next_level(level: int) -> int:
    return 10 + level * 2


def trainer_starting_level(race: Race, type_: SkillType) -> int:
    """Starting level a freshly learned trainer-locked skill begins at."""
    return max(1, min(MAX_SKILL_LEVEL, 10 + race.skill_affinities.get(type_, 0)))


def _grow(skill: Skill, gained_xp: int) -> Skill:
    level = skill.level
    xp = skill.xp + gained_xp
    while level < MAX_SKILL_LEVEL and xp >= xp_to_next_level(level):
        xp -= xp_to_next_level(level)
        level += 1
    if level >= MAX_SKILL_LEVEL:
        level = MAX_SKILL_LEVEL
        xp = 0
    return replace(skill, level=level, xp=xp)


def gain_skill_use(player: PlayerCharacter, type_: SkillType, rng: random.Random) -> PlayerCharacter:
    """Use a skill the character already knows. No-op if unknown or already maxed."""
    current = player.skills.get(type_)
    if current is None or current.level >= MAX_SKILL_LEVEL:
        return player

    base_gain = DiceFormula(1, DieType.D6, 1).roll(rng)
    is_primary = type_ in player.character_class.primary_skills
    gain = base_gain + DiceFormula(1, DieType.D6, 0).roll(rng) if is_primary else base_gain

    new_skills = dict(player.skills)
    new_skills[type_] = _grow(current, gain)
    return replace(player, skills=new_skills)


def learn_skill_from_trainer(player: PlayerCharacter, type_: SkillType) -> PlayerCharacter:
    """Learn a trainer-locked skill for the first time from an NPC trainer who teaches it."""
    if not type_.trainer_locked or player.knows_skill(type_):
        return player
    start_level = trainer_starting_level(player.race, type_)
    new_skills = dict(player.skills)
    new_skills[type_] = Skill(type_, start_level)
    return replace(player, skills=new_skills)
