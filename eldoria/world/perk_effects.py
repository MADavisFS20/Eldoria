"""Applies a chosen Perk's permanent effect.

Most perks bake a flat stat bump in immediately. SECOND_WIND, MASTER_TRADER,
and CRITICAL_FOCUS don't touch a stat here -- they're read live at the point
of use instead (a near-death save, a shop discount, a combat crit-threshold
check via PlayerCharacter.perk_rank).
"""
from __future__ import annotations

from dataclasses import replace

from eldoria.models import Perk, PlayerCharacter, SkillType
from eldoria.world.skill_progression import MAX_SKILL_LEVEL


def apply_perk(player: PlayerCharacter, perk: Perk) -> PlayerCharacter:
    if player.pending_perk_choices <= 0:
        raise ValueError("No perk choice banked")

    new_perks = dict(player.perks)
    new_perks[perk] = new_perks.get(perk, 0) + 1
    with_perk = replace(player, perks=new_perks, pending_perk_choices=player.pending_perk_choices - 1)

    if perk == Perk.POWER_ATTACK:
        return replace(with_perk, attack_bonus=with_perk.attack_bonus + 2)
    if perk == Perk.IRON_SKIN:
        return replace(with_perk, armor_class=with_perk.armor_class + 1)
    if perk == Perk.QUICK_REFLEXES:
        return replace(with_perk, speed=with_perk.speed + 3)
    if perk == Perk.ARCANE_RESERVE:
        return replace(with_perk, willpower=with_perk.willpower + 2)
    if perk == Perk.SILENT_STEP:
        sneak = with_perk.skills.get(SkillType.SNEAK)
        if sneak is None:
            return with_perk
        new_skills = dict(with_perk.skills)
        new_skills[SkillType.SNEAK] = replace(sneak, level=min(MAX_SKILL_LEVEL, sneak.level + 15))
        return replace(with_perk, skills=new_skills)
    if perk == Perk.TOUGHNESS:
        return replace(with_perk, max_health=with_perk.max_health + 15, current_health=with_perk.current_health + 15)
    # SECOND_WIND, MASTER_TRADER, CRITICAL_FOCUS: behavioral flags only, checked live elsewhere.
    return with_perk
