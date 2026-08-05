"""Every physical/magical number in the game comes from here -- always dice + tier, never a flat number.

Which die size gets used follows classic tabletop D&D convention: weapon
damage dice and creature hit dice both scale D4 -> D12 as tier rises.
CombatMath below is the core roll-d20-plus-bonus-vs-target-number mechanic,
natural 20 crits / natural 1 fumbles included.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from eldoria.models import DiceFormula, DieType, Item, ItemKind, MagicEffect, StatBlock, StatusEffect

_MAGIC_EFFECT_TEMPLATES = [
    ("Weakening Curse", "strength", False),
    ("Chilling Grasp", "speed", False),
    ("Mind Fog", "willpower", False),
    ("Sundering Strike", "armorClass", False),
    ("Enfeebling Touch", "agility", False),
    ("Empowering Aura", "strength", True),
    ("Windward Blessing", "speed", True),
    ("Arcane Focus", "willpower", True),
    ("Warding Sigil", "armorClass", True),
    ("Swift Grace", "agility", True),
    # Finance/economics-themed effects -- same tuple shape, same roll odds as
    # everything above; the names carry a real lesson, see data/finance_lore.py's
    # MAGIC_EFFECT_NOTES for what each one is teaching.
    ("Diversified Guard", "armorClass", True),
    ("Bull Market Vigor", "strength", True),
    ("Bear Market Dread", "strength", False),
    ("Liquid Assets", "speed", True),
    ("Frozen Assets", "speed", False),
    ("Compounding Focus", "willpower", True),
]


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _weapon_die(tier: int) -> DieType:
    """Weapon-weight-class die by tier, the D&D light/medium/heavy weapon progression."""
    return {1: DieType.D4, 2: DieType.D6, 3: DieType.D8, 4: DieType.D10}.get(tier, DieType.D12)


def _hit_die(tier: int) -> DieType:
    """Creature/monster hit-die size by tier."""
    if tier == 1:
        return DieType.D6
    if tier in (2, 3):
        return DieType.D8
    if tier == 4:
        return DieType.D10
    return DieType.D12


def _roll_ability(tier: int, rng: random.Random) -> int:
    return DiceFormula(3, DieType.D6, (tier - 1) * 2).roll(rng)


def _roll_magic_effect(rng: random.Random) -> MagicEffect:
    name, trait, beneficial = rng.choice(_MAGIC_EFFECT_TEMPLATES)
    magnitude = DiceFormula(1, DieType.D4).roll(rng)
    return MagicEffect(name, trait, magnitude, beneficial)


def creature_stats(tier: int, rng: random.Random) -> StatBlock:
    """Every creature/NPC/player stat block, scaled off tier (1..5) by dice roll."""
    t = _clamp(tier, 1, 5)
    strength = _roll_ability(t, rng)
    agility = _roll_ability(t, rng)
    willpower = _roll_ability(t, rng)
    str_mod = StatBlock.modifier_of(strength)
    agi_mod = StatBlock.modifier_of(agility)
    will_mod = StatBlock.modifier_of(willpower)

    hit_dice_count = t + 1
    max_health = max(1, DiceFormula(hit_dice_count, _hit_die(t), str_mod * hit_dice_count).roll(rng))

    armor_class = 10 + agi_mod + t
    speed = max(5, 20 + agi_mod * 2 + DiceFormula(1, DieType.D6).roll(rng))
    attack_bonus = t + str_mod

    damage_dice = 2 if t == 5 else 1
    damage = DiceFormula(damage_dice, _weapon_die(t), str_mod)

    # Percentile roll (D100) for magic presence: ~15% at tier 1 rising to ~85% at tier 5.
    magic_chance_roll = DiceFormula(1, DieType.D100).roll(rng)
    has_magic = magic_chance_roll <= (10 + t * 15)
    magic_damage = DiceFormula(max(1, t), DieType.D6, will_mod) if has_magic else None
    magic_effect = _roll_magic_effect(rng) if has_magic else None

    worth = DiceFormula(t, DieType.D20, 0).roll(rng) * 5

    return StatBlock(
        tier=t,
        strength=strength,
        agility=agility,
        willpower=willpower,
        max_health=max_health,
        armor_class=armor_class,
        speed=speed,
        attack_bonus=attack_bonus,
        damage=damage,
        magic_damage=magic_damage,
        magic_effect=magic_effect,
        worth=worth,
    )


def _roll_durability(tier: int, legendary: bool, rng: random.Random) -> int:
    multiplier = tier + (2 if legendary else 1)
    return DiceFormula(1, DieType.D8, 0).roll(rng) * multiplier


def _roll_value(tier: int, legendary: bool, rng: random.Random) -> int:
    base = DiceFormula(max(1, tier), DieType.D20, 0).roll(rng) * 10
    return base * 3 if legendary else base


def _roll_status_effect(rng: random.Random) -> StatusEffect:
    return rng.choice(list(StatusEffect))


def weapon_item(name: str, tier: int, rng: random.Random, legendary: bool = False) -> Item:
    t = _clamp(tier, 1, 5)
    dice_count = 2 if t == 5 else 1
    craft_bonus = t + (2 if legendary else 0)
    return Item(
        name=name,
        kind=ItemKind.WEAPON,
        tier=t,
        damage=DiceFormula(dice_count, _weapon_die(t), craft_bonus),
        magic_effect=_roll_magic_effect(rng) if legendary else None,
        value=_roll_value(t, legendary, rng),
        max_durability=_roll_durability(t, legendary, rng),
        is_legendary=legendary,
        inflicts_status=_roll_status_effect(rng) if legendary else None,
    )


def armor_item(name: str, tier: int, rng: random.Random, legendary: bool = False, slot: ItemKind = ItemKind.ARMOR) -> Item:
    """slot must be a physical-armor ItemKind: ARMOR (chest), OFFHAND, or HEAD."""
    if slot not in (ItemKind.ARMOR, ItemKind.OFFHAND, ItemKind.HEAD):
        raise ValueError(f"armor_item slot must be ARMOR, OFFHAND, or HEAD, got {slot}")
    t = _clamp(tier, 1, 5)
    # Offhand (shield) and head pieces are lighter than a full chest piece -- half the AC bonus, floor 1.
    chest_bonus = (t + 1) // 2 + (1 if legendary else 0)
    bonus = chest_bonus if slot == ItemKind.ARMOR else max(1, chest_bonus // 2)
    return Item(
        name=name,
        kind=slot,
        tier=t,
        armor_class_bonus=bonus,
        magic_effect=_roll_magic_effect(rng) if legendary else None,
        value=_roll_value(t, legendary, rng),
        max_durability=_roll_durability(t, legendary, rng),
        is_legendary=legendary,
    )


def accessory_item(name: str, tier: int, rng: random.Random, slot: ItemKind, legendary: bool = False) -> Item:
    """RING or AMULET -- bonus lives entirely in magic_effect, always beneficial (unlike the 50/50 curse roll)."""
    if slot not in (ItemKind.RING, ItemKind.AMULET):
        raise ValueError(f"accessory_item slot must be RING or AMULET, got {slot}")
    t = _clamp(tier, 1, 5)
    effect = _roll_magic_effect(rng)
    while not effect.beneficial:
        effect = _roll_magic_effect(rng)
    return Item(
        name=name,
        kind=slot,
        tier=t,
        magic_effect=effect,
        value=_roll_value(t, legendary, rng),
        max_durability=_roll_durability(t, legendary, rng),
        is_legendary=legendary,
    )


def quest_item(name: str, tier: int, rng: random.Random) -> Item:
    t = _clamp(tier, 1, 5)
    return Item(
        name=name,
        kind=ItemKind.QUEST_ITEM,
        tier=t,
        value=_roll_value(t, True, rng),
        max_durability=_roll_durability(t, True, rng),
    )


def repair_cost(item: Item, rng: random.Random) -> int:
    """Gold cost to fully repair a worn item -- itself dice-scaled, not a flat fraction."""
    return (item.value // 10) + DiceFormula(1, DieType.D6).roll(rng)


@dataclass(frozen=True)
class AttackRoll:
    natural_d20: int
    total: int
    crit_threshold: int = 20

    @property
    def is_critical(self) -> bool:
        return self.natural_d20 >= self.crit_threshold

    @property
    def is_fumble(self) -> bool:
        return self.natural_d20 == 1


def attack_roll(rng: random.Random, attack_bonus: int) -> int:
    """Simple total-only roll -- fine for anything that doesn't need crit/fumble detection."""
    return DiceFormula(1, DieType.D20, attack_bonus).roll(rng)


def attack_roll_detailed(rng: random.Random, attack_bonus: int, crit_threshold: int = 20) -> AttackRoll:
    natural = rng.randint(1, 20)
    return AttackRoll(natural, natural + attack_bonus, crit_threshold)


def is_hit(roll, target_armor_class: int) -> bool:
    """Accepts either a plain int total or an AttackRoll (natural 20 always hits, natural 1 always misses)."""
    if isinstance(roll, AttackRoll):
        if roll.is_critical:
            return True
        if roll.is_fumble:
            return False
        return roll.total >= target_armor_class
    return roll >= target_armor_class


def critical_damage(formula: DiceFormula, rng: random.Random) -> int:
    """Classic 5e crit rule: double the damage DICE (not the flat modifier), then roll once."""
    return DiceFormula(formula.count * 2, formula.die, formula.modifier).roll(rng)
