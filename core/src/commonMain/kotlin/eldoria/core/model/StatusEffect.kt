package eldoria.core.model

/**
 * A combat status a weapon (or, later, a spell) can inflict on a hit --
 * ported from the Python prototype's proven design (5 dmg/turn for the two
 * damage-over-time effects, a full skipped turn for freeze). Currently only
 * ever inflicted ON an enemy, never on the player, matching the source
 * material's actual behavior (see Game.kt's `attack`, world/StatGenerator's
 * legendary-weapon roll). Duration and resistance are tracked per-encounter,
 * not persisted -- see Game.kt's local status-tracking vars in `attack`.
 */
enum class StatusEffect(val displayName: String, val perTurnDamage: Int, val skipsTurn: Boolean, val defaultTurns: Int) {
    BURN("Burning", perTurnDamage = 5, skipsTurn = false, defaultTurns = 3),
    POISON("Poisoned", perTurnDamage = 5, skipsTurn = false, defaultTurns = 3),
    FREEZE("Frozen", perTurnDamage = 0, skipsTurn = true, defaultTurns = 1),
}
