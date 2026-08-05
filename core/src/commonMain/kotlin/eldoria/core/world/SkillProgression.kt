package eldoria.core.world

import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.PlayerCharacter
import eldoria.core.model.Race
import eldoria.core.model.Skill
import eldoria.core.model.SkillType
import kotlin.random.Random

/**
 * "The more a skill is used, the higher it levels" -- this is the whole
 * mechanic. Every skill runs 1..100. Using it grants a small dice-rolled xp
 * gain (bigger for a class's primary/specialized skills); banked xp needed
 * to reach the next level grows as the skill gets better, so early levels
 * come fast and mastery is a grind, same shape as StatGenerator's
 * dice-driven scaling elsewhere in the engine.
 *
 * This is deliberately independent of character level/combat XP -- see
 * LevelProgression for that track.
 */
object SkillProgression {
    const val MAX_SKILL_LEVEL = 100

    /** Banked xp required to advance from `level` to `level + 1`. */
    fun xpToNextLevel(level: Int): Int = 10 + level * 2

    /** Starting level a freshly learned trainer-locked skill begins at. */
    fun trainerStartingLevel(race: Race, type: SkillType): Int =
        (10 + (race.skillAffinities[type] ?: 0)).coerceIn(1, MAX_SKILL_LEVEL)

    private fun grow(skill: Skill, gainedXp: Int): Skill {
        var level = skill.level
        var xp = skill.xp + gainedXp
        while (level < MAX_SKILL_LEVEL && xp >= xpToNextLevel(level)) {
            xp -= xpToNextLevel(level)
            level++
        }
        if (level >= MAX_SKILL_LEVEL) {
            level = MAX_SKILL_LEVEL
            xp = 0
        }
        return skill.copy(level = level, xp = xp)
    }

    /**
     * Use a skill the character already knows. No-op if they don't know it
     * yet (trainer-locked skills must be learned first -- see
     * [learnSkillFromTrainer]) or if it's already maxed.
     */
    fun gainSkillUse(player: PlayerCharacter, type: SkillType, rng: Random): PlayerCharacter {
        val current = player.skills[type] ?: return player
        if (current.level >= MAX_SKILL_LEVEL) return player

        val baseGain = DiceFormula(1, DieType.D6, 1).roll(rng)
        val isPrimary = type in player.characterClass.primarySkills
        val gain = if (isPrimary) baseGain + DiceFormula(1, DieType.D6, 0).roll(rng) else baseGain

        return player.copy(skills = player.skills + (type to grow(current, gain)))
    }

    /**
     * Learn a trainer-locked skill for the first time from an NPC trainer
     * who teaches it. No-op if the character already knows it, or if the
     * skill isn't actually trainer-locked (those are known from creation).
     */
    fun learnSkillFromTrainer(player: PlayerCharacter, type: SkillType): PlayerCharacter {
        if (!type.trainerLocked || player.knowsSkill(type)) return player
        val startLevel = trainerStartingLevel(player.race, type)
        return player.copy(skills = player.skills + (type to Skill(type, startLevel)))
    }
}
