package eldoria.core.model

/**
 * A permanent bonus chosen by the player at certain level-ups (every 5
 * levels, see LevelProgression). Most bake a flat stat bump in immediately
 * via world/PerkEffects; SECOND_WIND and MASTER_TRADER are behavioral flags
 * checked at the point of use (a near-death heal, a shop discount) instead.
 *
 * Perks are pickable more than once (see PlayerCharacter.perks, a
 * Map<Perk, Int> stack count rather than a Set) -- merged in from the
 * Python prototype, where every perk was stackable with no cap. IRON_SKIN
 * and the new CRITICAL_FOCUS scale their effect per stack; the flat
 * one-time bumps (POWER_ATTACK, QUICK_REFLEXES, etc.) also just apply
 * again per repeat pick, which was already correct behavior needing no
 * code change. SECOND_WIND/MASTER_TRADER are presence-only flags, so
 * re-picking them is harmless but has no additional effect.
 */
enum class Perk(val displayName: String, val description: String) {
    POWER_ATTACK("Power Attack", "+2 attack bonus in melee -- you hit harder and more often."),
    IRON_SKIN("Iron Skin", "+1 armor class per rank -- your hide (or habits) have toughened."),
    QUICK_REFLEXES("Quick Reflexes", "+3 speed -- you react and move faster than most."),
    ARCANE_RESERVE("Arcane Reserve", "+2 willpower -- your reserve of magical focus deepens."),
    SILENT_STEP("Silent Step", "+15 Sneak -- you've learned to move without a sound."),
    TOUGHNESS("Toughness", "+15 max health -- you can simply take more punishment."),
    SECOND_WIND("Second Wind", "Once per rest, surviving a killing blow leaves you at 1 health instead of 0."),
    MASTER_TRADER("Master Trader", "Merchants give you noticeably better prices, buying and selling."),
    /** Merged from Python's stackable `critical_strike` perk, reshaped around Kotlin's natural-20 crit rule (a flat crit-damage bonus wouldn't fit the same way). */
    CRITICAL_FOCUS("Critical Focus", "Lowers the roll needed to land a critical hit by 1 per rank (crit on natural 20, then 19+, then 18+...)."),
}
