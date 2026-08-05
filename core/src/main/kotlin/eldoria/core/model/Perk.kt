package eldoria.core.model

/**
 * A permanent bonus chosen by the player at certain level-ups (every 5
 * levels, see LevelProgression). Most bake a flat stat bump in immediately
 * via world/PerkEffects; SECOND_WIND and MASTER_TRADER are behavioral flags
 * checked at the point of use (a near-death heal, a shop discount) instead.
 */
enum class Perk(val displayName: String, val description: String) {
    POWER_ATTACK("Power Attack", "+2 attack bonus in melee -- you hit harder and more often."),
    IRON_SKIN("Iron Skin", "+1 armor class -- your hide (or habits) have toughened."),
    QUICK_REFLEXES("Quick Reflexes", "+3 speed -- you react and move faster than most."),
    ARCANE_RESERVE("Arcane Reserve", "+2 willpower -- your reserve of magical focus deepens."),
    SILENT_STEP("Silent Step", "+15 Sneak -- you've learned to move without a sound."),
    TOUGHNESS("Toughness", "+15 max health -- you can simply take more punishment."),
    SECOND_WIND("Second Wind", "Once per rest, surviving a killing blow leaves you at 1 health instead of 0."),
    MASTER_TRADER("Master Trader", "Merchants give you noticeably better prices, buying and selling."),
}
