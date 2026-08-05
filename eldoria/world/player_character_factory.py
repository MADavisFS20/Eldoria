"""Builds a fresh level-1 PlayerCharacter.

Rolls base ability scores (3d6, race-modified), derives starting combat
stats with the same formulas level_progression uses at level 1, and starts
every base (non trainer-locked) skill at a level shaped by class
specialization and race affinity. Trainer-locked skills start unknown except
for a class's one free signature skill, if it has one.
"""
from __future__ import annotations

import random

from eldoria.models import CharacterClass, DiceFormula, DieType, PlayerCharacter, Race, Skill, SkillType, StatBlock
from eldoria.world import stat_generator as sg
from eldoria.world.skill_progression import MAX_SKILL_LEVEL

_BASE_SKILL_FLOOR = 15
_CLASS_PRIMARY_BONUS = 20
_SIGNATURE_SKILL_START = 20


def create(name: str, race: Race, character_class: CharacterClass, rng: random.Random) -> PlayerCharacter:
    strength = max(1, DiceFormula(3, DieType.D6, 0).roll(rng) + race.ability_modifiers.strength)
    agility = max(1, DiceFormula(3, DieType.D6, 0).roll(rng) + race.ability_modifiers.agility)
    willpower = max(1, DiceFormula(3, DieType.D6, 0).roll(rng) + race.ability_modifiers.willpower)
    str_mod = StatBlock.modifier_of(strength)
    agi_mod = StatBlock.modifier_of(agility)

    max_health = max(10, DiceFormula(2, DieType.D8, str_mod * 2).roll(rng))
    max_stamina = max(10, DiceFormula(2, DieType.D8, agi_mod * 2).roll(rng))
    base_armor_class = 10 + agi_mod
    speed = max(5, 20 + agi_mod * 2 + DiceFormula(1, DieType.D6).roll(rng))
    attack_bonus = str_mod
    unarmed_damage = DiceFormula(1, DieType.D6, str_mod)
    gold = DiceFormula(2, DieType.D8, 20).roll(rng)

    skills: dict[SkillType, Skill] = {}
    for type_ in SkillType.base_skills():
        primary_bonus = _CLASS_PRIMARY_BONUS if type_ in character_class.primary_skills else 0
        race_bonus = race.skill_affinities.get(type_, 0)
        level = max(1, min(MAX_SKILL_LEVEL, _BASE_SKILL_FLOOR + primary_bonus + race_bonus))
        skills[type_] = Skill(type_, level)
    if character_class.free_signature_skill is not None:
        type_ = character_class.free_signature_skill
        race_bonus = race.skill_affinities.get(type_, 0)
        level = max(1, min(MAX_SKILL_LEVEL, _SIGNATURE_SKILL_START + race_bonus))
        skills[type_] = Skill(type_, level)

    weapon = sg.weapon_item(character_class.starting_gear.weapon_name, 1, rng)
    armor = sg.armor_item(character_class.starting_gear.armor_name, 1, rng)
    # Starting gear is equipped directly (bypassing commands.py's equip(), which
    # normally bakes an item's bonus into the player's stats on equip) -- so its
    # armor_class_bonus has to be folded in here too.
    armor_class = base_armor_class + (armor.armor_class_bonus or 0)

    return PlayerCharacter(
        name=name,
        race=race,
        character_class=character_class,
        level=1,
        experience=0,
        strength=strength,
        agility=agility,
        willpower=willpower,
        max_health=max_health,
        current_health=max_health,
        max_stamina=max_stamina,
        current_stamina=max_stamina,
        armor_class=armor_class,
        speed=speed,
        attack_bonus=attack_bonus,
        unarmed_damage=unarmed_damage,
        skills=skills,
        gold=gold,
        inventory=(weapon, armor),
        equipped_weapon=weapon,
        equipped_armor=armor,
    )
