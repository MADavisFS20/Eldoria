package eldoria.core.world

import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.MagicEffect
import eldoria.core.model.StatBlock
import kotlin.random.Random

/**
 * Every physical/magical number in the game -- weapon damage, armor class,
 * speed, agility, value, health, strength, wear and tear, magic damage,
 * magic effects -- comes from here, and every one of them is a dice roll
 * scaled by difficulty tier (1 easiest .. 5 hardest). Nothing is a
 * flat/hardcoded number pretending to be a stat; it's always dice + tier.
 *
 * Which die size gets used follows classic tabletop D&D convention (see
 * model/Dice.kt's DieType doc): weapon damage dice and creature hit dice
 * both scale D4 -> D12 as tier rises, the same "bigger die for a bigger
 * threat" shape D&D uses for weapon weight class and monster size.
 *
 * Core resolution mechanic downstream (combat, checks) is the classic
 * roll-d20-plus-bonus-vs-target-number pattern, natural 20 crits / natural 1
 * fumbles included: see CombatMath.
 */
object StatGenerator {

    private val MAGIC_EFFECT_TEMPLATES = listOf(
        Triple("Weakening Curse", "strength", false),
        Triple("Chilling Grasp", "speed", false),
        Triple("Mind Fog", "willpower", false),
        Triple("Sundering Strike", "armorClass", false),
        Triple("Enfeebling Touch", "agility", false),
        Triple("Empowering Aura", "strength", true),
        Triple("Windward Blessing", "speed", true),
        Triple("Arcane Focus", "willpower", true),
        Triple("Warding Sigil", "armorClass", true),
        Triple("Swift Grace", "agility", true),
    )

    /** Weapon-weight-class die by tier, exactly the D&D light/medium/heavy weapon progression. */
    private fun weaponDie(tier: Int): DieType = when (tier) {
        1 -> DieType.D4
        2 -> DieType.D6
        3 -> DieType.D8
        4 -> DieType.D10
        else -> DieType.D12
    }

    /** Creature/monster hit-die size by tier, the same "bigger die for a bigger threat" convention D&D uses per monster size category. */
    private fun hitDie(tier: Int): DieType = when (tier) {
        1 -> DieType.D6
        2, 3 -> DieType.D8
        4 -> DieType.D10
        else -> DieType.D12
    }

    private fun rollAbility(tier: Int, rng: Random): Int =
        DiceFormula(3, DieType.D6, (tier - 1) * 2).roll(rng)

    private fun rollMagicEffect(rng: Random): MagicEffect {
        val (name, trait, beneficial) = MAGIC_EFFECT_TEMPLATES.random(rng)
        val magnitude = DiceFormula(1, DieType.D4).roll(rng)
        return MagicEffect(name, trait, magnitude, beneficial)
    }

    /** Every creature/NPC/player stat block, scaled off tier (1..5) by dice roll. */
    fun creatureStats(tier: Int, rng: Random): StatBlock {
        val t = tier.coerceIn(1, 5)
        val strength = rollAbility(t, rng)
        val agility = rollAbility(t, rng)
        val willpower = rollAbility(t, rng)
        val strMod = StatBlock.modifierOf(strength)
        val agiMod = StatBlock.modifierOf(agility)
        val willMod = StatBlock.modifierOf(willpower)

        val hitDiceCount = t + 1
        val maxHealth = DiceFormula(hitDiceCount, hitDie(t), strMod * hitDiceCount).roll(rng).coerceAtLeast(1)

        val armorClass = 10 + agiMod + t
        val speed = (20 + agiMod * 2 + DiceFormula(1, DieType.D6).roll(rng)).coerceAtLeast(5)
        val attackBonus = t + strMod

        val damageDice = if (t == 5) 2 else 1
        val damage = DiceFormula(damageDice, weaponDie(t), strMod)

        // Percentile roll (D100) for magic presence, classic table-lookup style: ~15% at tier 1 rising to ~85% at tier 5.
        val magicChanceRoll = DiceFormula(1, DieType.D100).roll(rng)
        val hasMagic = magicChanceRoll <= (10 + t * 15)
        val magicDamage = if (hasMagic) DiceFormula(t.coerceAtLeast(1), DieType.D6, willMod) else null
        val magicEffect = if (hasMagic) rollMagicEffect(rng) else null

        val worth = DiceFormula(t, DieType.D20, 0).roll(rng) * 5

        return StatBlock(
            tier = t,
            strength = strength,
            agility = agility,
            willpower = willpower,
            maxHealth = maxHealth,
            armorClass = armorClass,
            speed = speed,
            attackBonus = attackBonus,
            damage = damage,
            magicDamage = magicDamage,
            magicEffect = magicEffect,
            worth = worth,
        )
    }

    private fun rollDurability(tier: Int, legendary: Boolean, rng: Random): Int {
        val multiplier = tier + (if (legendary) 2 else 1)
        return DiceFormula(1, DieType.D8, 0).roll(rng) * multiplier
    }

    private fun rollValue(tier: Int, legendary: Boolean, rng: Random): Int {
        val base = DiceFormula(tier.coerceAtLeast(1), DieType.D20, 0).roll(rng) * 10
        return if (legendary) base * 3 else base
    }

    fun weaponItem(name: String, tier: Int, rng: Random, legendary: Boolean = false): Item {
        val t = tier.coerceIn(1, 5)
        val diceCount = if (t == 5) 2 else 1
        val craftBonus = t + (if (legendary) 2 else 0)
        return Item(
            name = name,
            kind = ItemKind.WEAPON,
            tier = t,
            damage = DiceFormula(diceCount, weaponDie(t), craftBonus),
            magicEffect = if (legendary) rollMagicEffect(rng) else null,
            value = rollValue(t, legendary, rng),
            maxDurability = rollDurability(t, legendary, rng),
            isLegendary = legendary,
        )
    }

    fun armorItem(name: String, tier: Int, rng: Random, legendary: Boolean = false): Item {
        val t = tier.coerceIn(1, 5)
        val bonus = (t + 1) / 2 + (if (legendary) 1 else 0)
        return Item(
            name = name,
            kind = ItemKind.ARMOR,
            tier = t,
            armorClassBonus = bonus,
            magicEffect = if (legendary) rollMagicEffect(rng) else null,
            value = rollValue(t, legendary, rng),
            maxDurability = rollDurability(t, legendary, rng),
            isLegendary = legendary,
        )
    }

    fun questItem(name: String, tier: Int, rng: Random): Item {
        val t = tier.coerceIn(1, 5)
        return Item(
            name = name,
            kind = ItemKind.QUEST_ITEM,
            tier = t,
            value = rollValue(t, legendary = true, rng = rng),
            maxDurability = rollDurability(t, legendary = true, rng = rng),
        )
    }

    /** Gold cost to fully repair a worn item -- itself dice-scaled, not a flat fraction. */
    fun repairCost(item: Item, rng: Random): Int =
        (item.value / 10) + DiceFormula(1, DieType.D6).roll(rng)
}

/**
 * The core resolution mechanic every encounter downstream should use: d20 +
 * bonus vs target number, with the classic tabletop crit/fumble rule --
 * natural 20 always hits (and is a critical, see [AttackRoll.isCritical]),
 * natural 1 always misses.
 */
object CombatMath {
    data class AttackRoll(val naturalD20: Int, val total: Int) {
        val isCritical: Boolean get() = naturalD20 == 20
        val isFumble: Boolean get() = naturalD20 == 1
    }

    /** Simple total-only roll -- fine for anything that doesn't need crit/fumble detection. */
    fun attackRoll(rng: Random, attackBonus: Int): Int = DiceFormula(1, DieType.D20, attackBonus).roll(rng)

    /** Full detail (natural face + total) for combat loops that apply the crit/fumble rule. */
    fun attackRollDetailed(rng: Random, attackBonus: Int): AttackRoll {
        val natural = rng.nextInt(1, 21)
        return AttackRoll(natural, natural + attackBonus)
    }

    fun isHit(attackRoll: Int, targetArmorClass: Int): Boolean = attackRoll >= targetArmorClass

    /** Natural 20 always hits, natural 1 always misses, regardless of the total vs AC. */
    fun isHit(roll: AttackRoll, targetArmorClass: Int): Boolean =
        if (roll.isCritical) true else if (roll.isFumble) false else roll.total >= targetArmorClass

    /** Classic 5e crit rule: double the damage DICE (not the flat modifier), then roll once. */
    fun criticalDamage(formula: DiceFormula, rng: Random): Int =
        DiceFormula(formula.count * 2, formula.die, formula.modifier).roll(rng)
}
