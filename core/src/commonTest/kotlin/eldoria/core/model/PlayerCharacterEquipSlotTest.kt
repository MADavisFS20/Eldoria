package eldoria.core.model

import eldoria.core.world.PlayerCharacterFactory
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

/** Covers PlayerCharacter's new 6-slot equip lookup/update helpers (Phase 1's equipment-slot merge). */
class PlayerCharacterEquipSlotTest {

    private fun basePlayer() = PlayerCharacterFactory.create("Test", Race.HUMAN, CharacterClass.WARRIOR, Random(1))

    @Test
    fun `equippedInSlot reads the right field for each of the six slots`() {
        val player = basePlayer()
        val ring = Item(name = "Ring", kind = ItemKind.RING, tier = 1, value = 1, maxDurability = 1)
        val amulet = Item(name = "Amulet", kind = ItemKind.AMULET, tier = 1, value = 1, maxDurability = 1)
        val head = Item(name = "Head", kind = ItemKind.HEAD, tier = 1, value = 1, maxDurability = 1)
        val offhand = Item(name = "Offhand", kind = ItemKind.OFFHAND, tier = 1, value = 1, maxDurability = 1)

        val equipped = player.copy(equippedRing = ring, equippedAmulet = amulet, equippedHead = head, equippedOffhand = offhand)

        assertEquals(ring, equipped.equippedInSlot(ItemKind.RING))
        assertEquals(amulet, equipped.equippedInSlot(ItemKind.AMULET))
        assertEquals(head, equipped.equippedInSlot(ItemKind.HEAD))
        assertEquals(offhand, equipped.equippedInSlot(ItemKind.OFFHAND))
        assertEquals(player.equippedWeapon, equipped.equippedInSlot(ItemKind.WEAPON))
        assertEquals(player.equippedArmor, equipped.equippedInSlot(ItemKind.ARMOR))
    }

    @Test
    fun `equippedInSlot returns null for non-equippable kinds`() {
        val player = basePlayer()
        assertNull(player.equippedInSlot(ItemKind.QUEST_ITEM))
        assertNull(player.equippedInSlot(ItemKind.MATERIAL))
        assertNull(player.equippedInSlot(ItemKind.BOAT))
        assertNull(player.equippedInSlot(ItemKind.TRINKET))
    }

    @Test
    fun `withEquippedInSlot writes the right field and leaves the others untouched`() {
        val player = basePlayer()
        val ring = Item(name = "Ring", kind = ItemKind.RING, tier = 1, value = 1, maxDurability = 1)

        val updated = player.withEquippedInSlot(ItemKind.RING, ring)

        assertEquals(ring, updated.equippedRing)
        assertEquals(player.equippedWeapon, updated.equippedWeapon)
        assertEquals(player.equippedArmor, updated.equippedArmor)
        assertNull(updated.equippedAmulet)
    }
}
