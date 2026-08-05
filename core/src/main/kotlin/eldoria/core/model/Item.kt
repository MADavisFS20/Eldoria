package eldoria.core.model

enum class ItemKind { WEAPON, ARMOR, QUEST_ITEM, TRINKET, MATERIAL, BOAT }

/**
 * Any physical item: weapon, armor, quest item, or misc trinket. Combat and
 * shop stats are all dice-derived (see StatGenerator) -- value and durability
 * included, so "wear and tear" is a real mechanical value, not flavor text.
 */
data class Item(
    val name: String,
    val kind: ItemKind,
    val tier: Int,
    val damage: DiceFormula? = null,
    val armorClassBonus: Int? = null,
    val magicEffect: MagicEffect? = null,
    val value: Int,
    val maxDurability: Int,
    val currentDurability: Int = maxDurability,
    val isLegendary: Boolean = false,
    /** BOAT-only: fitted cannons add a bonus damage volley each round of ship combat, see Game.kt's shipEncounter. */
    val hasCannons: Boolean = false,
) : java.io.Serializable {
    val isBroken: Boolean get() = currentDurability <= 0
    fun worn(amount: Int): Item = copy(currentDurability = (currentDurability - amount).coerceAtLeast(0))
    fun repaired(): Item = copy(currentDurability = maxDurability)
}
