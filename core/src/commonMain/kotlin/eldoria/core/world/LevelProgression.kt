package eldoria.core.world

import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.PlayerCharacter
import eldoria.core.model.StatBlock
import kotlin.random.Random

/**
 * Character level (1..50) is its own track, separate from skill mastery
 * (see SkillProgression): defeating enemies and completing quests grants
 * experience points; enough banked xp levels the character up. Higher
 * world-map difficulty tiers (1..5) are tougher fights that pay out more
 * xp, so hunting in a harder biome zone is the "grind faster" lever.
 *
 * A level-up bumps every basic stat slightly -- health and strength gain
 * the most, agility/willpower a little -- and each level demands more xp
 * than the last, same escalating-difficulty shape used everywhere else in
 * the engine.
 */
object LevelProgression {
    const val MAX_CHARACTER_LEVEL = 50

    /** Banked xp required to advance from `level` to `level + 1`. */
    fun xpToNextLevel(level: Int): Int = level * level * 20 + 100

    /** Xp a kill of the given world difficulty tier (1..5) pays out. Harder tier, bigger reward. */
    fun xpForDefeating(tier: Int, rng: Random): Int {
        val t = tier.coerceIn(1, 5)
        return DiceFormula(t, DieType.D20, t * 10).roll(rng) * t
    }

    /** Apply a batch of xp (from a kill, a quest reward, whatever), leveling up as many times as it covers. */
    fun applyExperience(player: PlayerCharacter, xpGained: Int, rng: Random): PlayerCharacter {
        var level = player.level
        var xp = player.experience + xpGained
        var strength = player.strength
        var agility = player.agility
        var willpower = player.willpower
        var maxHealth = player.maxHealth
        var currentHealth = player.currentHealth
        var maxStamina = player.maxStamina
        var currentStamina = player.currentStamina
        var pendingPerkChoices = player.pendingPerkChoices

        while (level < MAX_CHARACTER_LEVEL && xp >= xpToNextLevel(level)) {
            xp -= xpToNextLevel(level)
            level++

            val healthGain = DiceFormula(2, DieType.D8, 3).roll(rng)
            maxHealth += healthGain
            currentHealth += healthGain
            val staminaGain = DiceFormula(1, DieType.D8, 2).roll(rng)
            maxStamina += staminaGain
            currentStamina += staminaGain
            if (DiceFormula(1, DieType.D20).roll(rng) <= 12) strength++ // ~60% chance
            if (DiceFormula(1, DieType.D20).roll(rng) <= 8) agility++ // ~40% chance
            if (DiceFormula(1, DieType.D20).roll(rng) <= 8) willpower++ // ~40% chance
            if (level % 5 == 0) pendingPerkChoices++
        }
        if (level >= MAX_CHARACTER_LEVEL) {
            level = MAX_CHARACTER_LEVEL
            xp = 0
        }

        val strMod = StatBlock.modifierOf(strength)
        val agiMod = StatBlock.modifierOf(agility)
        val armorClass = 10 + agiMod + level / 5
        val attackBonus = level / 4 + strMod
        val speed = (20 + agiMod * 2 + level / 10).coerceAtLeast(5)
        val unarmedDamage = DiceFormula(1 + level / 15, if (level < 25) DieType.D6 else DieType.D8, strMod)

        return player.copy(
            level = level,
            experience = xp,
            strength = strength,
            agility = agility,
            willpower = willpower,
            maxHealth = maxHealth,
            currentHealth = currentHealth,
            maxStamina = maxStamina,
            currentStamina = currentStamina,
            armorClass = armorClass,
            speed = speed,
            attackBonus = attackBonus,
            unarmedDamage = unarmedDamage,
            pendingPerkChoices = pendingPerkChoices,
        )
    }
}
