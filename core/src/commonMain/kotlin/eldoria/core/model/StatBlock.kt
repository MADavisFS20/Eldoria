package eldoria.core.model

import kotlinx.serialization.Serializable

/** A magic effect that shifts one trait/skill up (buff) or down (curse), e.g. on a legendary item or a hostile spellcaster's touch. */
@Serializable
data class MagicEffect(
    val name: String,
    val affectedTrait: String,
    val magnitude: Int,
    val beneficial: Boolean,
)

/**
 * The full physical/magical profile of any creature, NPC, or player: every
 * field here is produced by StatGenerator from d6/d8/d20 rolls, scaled by
 * difficulty tier (1..5). This is what combat, encounters, and shops read
 * from -- nothing is flavor-text-only.
 */
@Serializable
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
    /** Statuses this being shrugs off entirely -- see model/StatusEffect.kt. Empty by default; Phase 2's ported named enemies (goblins, stone golems, etc.) get real per-type resistance lists. */
    val statusResistances: Set<StatusEffect> = emptySet(),
) {
    companion object {
        // (score - 10).floorDiv(2): java.lang.Math.floorDiv is JVM-only, this
        // is the multiplatform-safe Kotlin stdlib equivalent (since 1.5).
        fun modifierOf(score: Int): Int = (score - 10).floorDiv(2)
    }
}
