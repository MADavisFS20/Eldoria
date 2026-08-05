package eldoria.core.model

import kotlinx.serialization.Serializable

/**
 * WEAPON/ARMOR(chest)/OFFHAND/HEAD/RING/AMULET are the six equip slots on
 * PlayerCharacter (see equippedWeapon/equippedOffhand/equippedArmor/
 * equippedHead/equippedRing/equippedAmulet) -- ARMOR specifically means the
 * chest slot, kept its original name to avoid churning every existing call
 * site for a cosmetic rename. RING/AMULET carry their bonus via
 * `magicEffect` rather than `armorClassBonus`, reusing the same mechanism
 * legendary items already use instead of adding parallel bonus fields.
 */
enum class ItemKind { WEAPON, ARMOR, OFFHAND, HEAD, RING, AMULET, QUEST_ITEM, TRINKET, MATERIAL, BOAT }

/**
 * Any physical item: weapon, armor, quest item, or misc trinket. Combat and
 * shop stats are all dice-derived (see StatGenerator) -- value and durability
 * included, so "wear and tear" is a real mechanical value, not flavor text.
 */
@Serializable
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
    /** WEAPON-only: a chance to inflict this on a successful hit -- see Game.kt's `attack` and StatGenerator's legendary-weapon roll. */
    val inflictsStatus: StatusEffect? = null,
) {
    val isBroken: Boolean get() = currentDurability <= 0
    fun worn(amount: Int): Item = copy(currentDurability = (currentDurability - amount).coerceAtLeast(0))
    fun repaired(): Item = copy(currentDurability = maxDurability)
}
