package eldoria.core

import eldoria.core.model.CharacterClass
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.MagicEffect
import eldoria.core.model.Race
import eldoria.core.world.PlayerCharacterFactory
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals

/**
 * Direct test of Game.kt's applyItemBonus -- the arithmetic Phase 1's
 * equip() rewrite leans on to apply/reverse an equipped item's passive
 * bonus. This is the single highest-risk spot in the equip-slot rewrite
 * (a sign error here means gear silently does nothing, or double-applies
 * on a swap), so it gets a direct test rather than relying solely on a
 * manual :core:play smoke run.
 */
class EquipBonusTest {

    private fun basePlayer() = PlayerCharacterFactory.create("Test", Race.HUMAN, CharacterClass.WARRIOR, Random(1))

    @Test
    fun `armorClassBonus applies then fully reverses`() {
        val player = basePlayer()
        val startingAc = player.armorClass
        val shield = Item(name = "Test Shield", kind = ItemKind.OFFHAND, tier = 1, armorClassBonus = 4, value = 10, maxDurability = 10)

        val equipped = applyItemBonus(player, shield, sign = 1)
        assertEquals(startingAc + 4, equipped.armorClass)

        val reversed = applyItemBonus(equipped, shield, sign = -1)
        assertEquals(startingAc, reversed.armorClass, "reversing must land exactly back at the starting AC, not drift")
    }

    @Test
    fun `beneficial magicEffect applies then fully reverses`() {
        val player = basePlayer()
        val startingStr = player.strength
        val ring = Item(
            name = "Ring of Might", kind = ItemKind.RING, tier = 1,
            magicEffect = MagicEffect("Empowering Aura", "strength", magnitude = 3, beneficial = true),
            value = 10, maxDurability = 10,
        )

        val equipped = applyItemBonus(player, ring, sign = 1)
        assertEquals(startingStr + 3, equipped.strength)

        val reversed = applyItemBonus(equipped, ring, sign = -1)
        assertEquals(startingStr, reversed.strength)
    }

    @Test
    fun `curse magicEffect subtracts on apply and adds back on reverse`() {
        val player = basePlayer()
        val startingSpeed = player.speed
        val cursedItem = Item(
            name = "Cursed Trinket", kind = ItemKind.AMULET, tier = 1,
            magicEffect = MagicEffect("Chilling Grasp", "speed", magnitude = 5, beneficial = false),
            value = 10, maxDurability = 10,
        )

        val equipped = applyItemBonus(player, cursedItem, sign = 1)
        assertEquals(startingSpeed - 5, equipped.speed, "a curse (beneficial=false) must subtract, not add")

        val reversed = applyItemBonus(equipped, cursedItem, sign = -1)
        assertEquals(startingSpeed, reversed.speed)
    }

    @Test
    fun `item with no bonus fields is a no-op`() {
        val player = basePlayer()
        val plainItem = Item(name = "Plain Rock", kind = ItemKind.TRINKET, tier = 1, value = 1, maxDurability = 1)
        assertEquals(player, applyItemBonus(player, plainItem, sign = 1))
    }
}
