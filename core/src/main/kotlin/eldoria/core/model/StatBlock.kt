package eldoria.core.model

/** A magic effect that shifts one trait/skill up (buff) or down (curse), e.g. on a legendary item or a hostile spellcaster's touch. */
data class MagicEffect(
    val name: String,
    val affectedTrait: String,
    val magnitude: Int,
    val beneficial: Boolean,
) : java.io.Serializable

/**
 * The full physical/magical profile of any creature, NPC, or player: every
 * field here is produced by StatGenerator from d6/d8/d20 rolls, scaled by
 * difficulty tier (1..5). This is what combat, encounters, and shops read
 * from -- nothing is flavor-text-only.
 */
data class StatBlock(
    val tier: Int,
    val strength: Int,
    val agility: Int,
    val willpower: Int,
    val maxHealth: Int,
    val armorClass: Int,
    val speed: Int,
    val attackBonus: Int,
    val damage: DiceFormula,
    val magicDamage: DiceFormula?,
    val magicEffect: MagicEffect?,
    val worth: Int,
) {
    companion object {
        fun modifierOf(score: Int): Int = Math.floorDiv(score - 10, 2)
    }
}
