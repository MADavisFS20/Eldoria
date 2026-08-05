package eldoria.core.model

/**
 * An optional curse/gift a character can request from the one NPC in the
 * world who offers it (see SpawnEntry.offersSubclass). Mutually exclusive
 * and permanent -- once chosen, PlayerCharacter.subclass is set for good
 * and the other option is no longer available to that character. Classic
 * minor strengths/weaknesses, not a full second class: a handful of stat
 * bonuses applied once at the moment of transformation, plus a combat
 * behavior (lifesteal or a low-health rage bonus) checked in Game.kt's
 * `attack()`.
 */
enum class Subclass(
    val displayName: String,
    val lore: String,
    val strengthDescription: String,
    val weaknessDescription: String,
    val strengthBonus: Int,
    val agilityBonus: Int,
    val willpowerBonus: Int,
    val maxHealthBonus: Int,
    val armorClassBonus: Int,
    /** % of damage dealt in melee returned as healing. */
    val lifestealPercent: Int,
    /** Flat bonus damage while below half health -- the beast coming out under pressure. */
    val lowHealthRageBonus: Int,
) {
    VAMPIRE(
        "Vampire",
        "The bite took hold, and something ancient and hungry now moves beneath your skin.",
        "Unnaturally swift and graceful, and every wound you deal feeds something back into you.",
        "Frailer than you look underneath the borrowed strength, and no less easy to kill for it.",
        strengthBonus = 0, agilityBonus = 3, willpowerBonus = 1, maxHealthBonus = -4, armorClassBonus = -1,
        lifestealPercent = 15, lowHealthRageBonus = 0,
    ),
    WEREWOLF(
        "Werewolf",
        "The curse runs hot in your blood now -- on a bad night you can feel the shape underneath your own.",
        "Ferocious and hard to put down, especially once you're bleeding.",
        "The beast rides closer to the surface than you'd like -- your focus and your guard both suffer for it.",
        strengthBonus = 4, agilityBonus = 0, willpowerBonus = -2, maxHealthBonus = 15, armorClassBonus = -1,
        lifestealPercent = 0, lowHealthRageBonus = 3,
    ),
}
