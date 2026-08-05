package eldoria.core.world

import eldoria.core.model.ItemKind
import eldoria.core.model.StatusEffect
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** Covers the Phase 1 additions to StatGenerator: the new equip-slot item generators and the legendary-weapon status roll. */
class StatGeneratorPhase1Test {

    @Test
    fun `armorItem defaults to the chest slot`() {
        val item = StatGenerator.armorItem("Test Armor", tier = 2, rng = Random(1))
        assertEquals(ItemKind.ARMOR, item.kind)
        assertNotNull(item.armorClassBonus)
    }

    @Test
    fun `armorItem on OFFHAND and HEAD slots grants a smaller bonus than chest at the same tier`() {
        val tier = 3
        val chest = StatGenerator.armorItem("Chest", tier, Random(1))
        val offhand = StatGenerator.armorItem("Offhand", tier, Random(1), slot = ItemKind.OFFHAND)
        val head = StatGenerator.armorItem("Head", tier, Random(1), slot = ItemKind.HEAD)

        assertEquals(ItemKind.OFFHAND, offhand.kind)
        assertEquals(ItemKind.HEAD, head.kind)
        assertTrue(offhand.armorClassBonus!! <= chest.armorClassBonus!!)
        assertTrue(head.armorClassBonus!! <= chest.armorClassBonus!!)
        assertTrue(offhand.armorClassBonus!! >= 1, "should floor at +1, never 0 or negative")
    }

    @Test
    fun `accessoryItem always rolls a beneficial magicEffect`() {
        // Different seeds to exercise multiple rolls of the underlying 50/50 template list.
        for (seed in 1..25) {
            val ring = StatGenerator.accessoryItem("Test Ring", tier = 2, rng = Random(seed.toLong()), slot = ItemKind.RING)
            assertEquals(ItemKind.RING, ring.kind)
            assertNotNull(ring.magicEffect)
            assertTrue(ring.magicEffect!!.beneficial, "accessory items must never roll a curse")
            assertNull(ring.armorClassBonus, "rings/amulets carry their bonus via magicEffect, not armorClassBonus")
        }
    }

    @Test
    fun `legendary weapons always inflict a status, non-legendary weapons never do`() {
        val legendary = StatGenerator.weaponItem("Legendary Blade", tier = 3, rng = Random(1), legendary = true)
        assertNotNull(legendary.inflictsStatus)
        assertTrue(legendary.inflictsStatus in StatusEffect.entries)

        val mundane = StatGenerator.weaponItem("Plain Sword", tier = 3, rng = Random(1), legendary = false)
        assertNull(mundane.inflictsStatus)
    }

    @Test
    fun `CombatMath crit threshold widens the crit range without disturbing the fumble rule`() {
        val vanilla = CombatMath.AttackRoll(naturalD20 = 19, total = 25, critThreshold = 20)
        assertTrue(!vanilla.isCritical, "natural 19 should not crit at the default threshold")

        val widened = CombatMath.AttackRoll(naturalD20 = 19, total = 25, critThreshold = 18)
        assertTrue(widened.isCritical, "natural 19 should crit once Perk.CRITICAL_FOCUS lowers the threshold to 18")

        val fumble = CombatMath.AttackRoll(naturalD20 = 1, total = 30, critThreshold = 10)
        assertTrue(fumble.isFumble, "a natural 1 is always a fumble regardless of crit threshold")
        assertTrue(!fumble.isCritical, "natural 1 must never also count as a crit, even with a very wide threshold")
    }
}
