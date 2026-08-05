package eldoria.core.model

import kotlinx.serialization.Serializable

/**
 * A hired companion: deliberately lightweight (not a full SpawnEntry/StatBlock)
 * since this rides along on PlayerCharacter and gets saved to disk. Combat
 * stats are copied off the source NPC's StatBlock once, at hire time.
 *
 * `hiredAtMillis` is wall-clock real time (kotlin.time.Clock, epoch millis),
 * not game ticks -- per explicit spec, a companion leaves after 3 real
 * hours, not 3 hours of in-game time.
 */
@Serializable
data class HiredCompanion(
    val name: String,
    val attackBonus: Int,
    val armorClass: Int,
    val damage: DiceFormula,
    val originLocationId: String,
    val hiredAtMillis: Long,
    val reviveUsed: Boolean = false,
) {
    companion object {
        const val EMPLOYMENT_DURATION_MILLIS: Long = 3L * 60 * 60 * 1000
    }
}
