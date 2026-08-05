package eldoria.core.model

import kotlin.random.Random
import kotlinx.serialization.Serializable

/**
 * Every physical or magical value in Eldoria is produced by rolling one of
 * these -- nothing is ever a bare hardcoded number pretending to be a stat.
 * This is the classic tabletop D&D die set, and each size is used for the
 * situation it's traditionally used for (see StatGenerator/CombatMath for
 * where each one is actually rolled):
 *  - D4: light/small weapon damage (dagger-tier), minor spell/status effects.
 *  - D6: the default -- most ability scores (3d6), medium weapon damage,
 *    small-creature hit dice, general-purpose "modest" rolls.
 *  - D8: bigger weapon damage, medium-creature hit dice, healing magic.
 *  - D10: heavy weapon damage, large-creature hit dice; paired with itself
 *    it also makes a D100 percentile roll (tens die + ones die).
 *  - D12: the heaviest weapons (greataxe-tier), huge/boss-tier hit dice.
 *  - D20: the core resolution die -- attack rolls, ability/skill checks,
 *    saving throws. A natural 20 is a critical hit; a natural 1 is a fumble.
 *  - D100: percentile rolls for rare-item/loot-table odds.
 */
enum class DieType(val sides: Int) { D4(4), D6(6), D8(8), D10(10), D12(12), D20(20), D100(100) }

/** An "NdX+M" formula, e.g. 2d8+3. */
@Serializable
data class DiceFormula(val count: Int, val die: DieType, val modifier: Int = 0) {
    fun roll(rng: Random): Int {
        var total = modifier
        repeat(count) { total += rng.nextInt(1, die.sides + 1) }
        return total
    }

    fun average(): Double = count * (die.sides + 1) / 2.0 + modifier

    override fun toString(): String {
        val sign = if (modifier > 0) "+$modifier" else if (modifier < 0) "$modifier" else ""
        return "${count}d${die.sides}$sign"
    }
}
