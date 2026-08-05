package eldoria.core.world

import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import kotlin.random.Random

/**
 * Trader NPCs (see data/DialogueContent.kt's TRADER archetype) sell a
 * small, deterministic stock of tier-appropriate generic gear -- generated
 * on the fly from the same StatGenerator dice formulas everything else in
 * the game uses, seeded off the trader's name and location so the same
 * merchant always has the same stock in the same playthrough.
 */
object ShopGenerator {
    private val WEAPON_NAMES = listOf(
        "Traveler's Sword", "Worn Hand Axe", "Hunting Bow", "Iron Mace", "Simple Dagger", "Oak Quarterstaff",
    )
    private val ARMOR_NAMES = listOf(
        "Traveler's Vest", "Reinforced Buckler", "Padded Jerkin", "Riveted Cuirass", "Simple Hood", "Worn Chainmail",
    )
    private val OFFHAND_NAMES = listOf("Worn Buckler", "Iron Targe", "Reinforced Kite Shield")
    private val HEAD_NAMES = listOf("Leather Cap", "Iron Skullcap", "Traveler's Hood")
    private val RING_NAMES = listOf("Simple Band", "Engraved Signet Ring", "Weathered Ring")
    private val AMULET_NAMES = listOf("Plain Pendant", "Carved Bone Amulet", "Silver Locket")

    fun inventoryFor(traderName: String, locationId: String, tier: Int, worldSeed: Long): List<Item> {
        val rng = DeterministicRandom.random(worldSeed, traderName.hashCode().toLong(), locationId.hashCode().toLong(), 555L)
        val count = rng.nextInt(3, 6)
        return List(count) {
            when (rng.nextInt(6)) {
                0, 1 -> StatGenerator.weaponItem(WEAPON_NAMES.random(rng), tier, rng)
                2, 3 -> StatGenerator.armorItem(ARMOR_NAMES.random(rng), tier, rng)
                4 -> if (rng.nextBoolean())
                    StatGenerator.armorItem(OFFHAND_NAMES.random(rng), tier, rng, slot = ItemKind.OFFHAND)
                else
                    StatGenerator.armorItem(HEAD_NAMES.random(rng), tier, rng, slot = ItemKind.HEAD)
                else -> if (rng.nextBoolean())
                    StatGenerator.accessoryItem(RING_NAMES.random(rng), tier, rng, slot = ItemKind.RING)
                else
                    StatGenerator.accessoryItem(AMULET_NAMES.random(rng), tier, rng, slot = ItemKind.AMULET)
            }
        }
    }

    /**
     * Price a merchant pays the player for an item they're selling -- base
     * 50% of value, plus `bonusPercent` stacked from the Master Trader perk
     * and/or the Coercion Device artifact (both push the merchant's price up).
     */
    fun sellBackPrice(item: Item, bonusPercent: Int): Int =
        (item.value * (50 + bonusPercent).coerceAtMost(95) / 100.0).toInt().coerceAtLeast(1)

    /** Price the player pays to buy an item -- `discountPercent` stacks the same way, in the buyer's favor. */
    fun buyPrice(item: Item, discountPercent: Int): Int =
        (item.value * (100 - discountPercent).coerceAtLeast(5) / 100.0).toInt().coerceAtLeast(1)
}
