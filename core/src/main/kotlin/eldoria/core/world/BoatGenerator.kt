package eldoria.core.world

import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import kotlin.random.Random

/**
 * Boats are bought at Sea-biome settlements (see Game.kt's buyBoat) and
 * modeled as a plain Item (kind=BOAT) so they get the same durability/wear
 * mechanic as weapons and armor -- sailing wears one down, a bad fight with
 * pirates or a sea monster can destroy it outright, and repairs cost gold
 * scaled to how battered it is, same shape as StatGenerator.repairCost.
 */
object BoatGenerator {
    private val NAMES = listOf(
        "Gullwing Skiff", "Saltbrine Sloop", "The Tidewalker", "Driftrunner", "The Brinehopper", "Foamcutter",
    )

    fun buy(rng: Random): Item {
        val durability = DiceFormula(3, DieType.D8, 10).roll(rng)
        val price = DiceFormula(4, DieType.D20, 40).roll(rng) * 3
        return Item(
            name = NAMES.random(rng),
            kind = ItemKind.BOAT,
            tier = 1,
            value = price,
            maxDurability = durability,
        )
    }

    fun repairCost(boat: Item): Int = (boat.maxDurability - boat.currentDurability) * 5
}
