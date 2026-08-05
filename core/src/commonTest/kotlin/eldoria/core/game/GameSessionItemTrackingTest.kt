package eldoria.core.game

import eldoria.core.model.Biome
import eldoria.core.model.GameLocation
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.PopulationTier
import eldoria.core.model.World
import eldoria.core.world.PlayerCharacterFactory
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * Regression test for a bug found while playtesting Phase 2's home region:
 * GameSession used to track taken ground items by NAME (a Set<String>), so
 * a location with several items sharing a name (e.g. three separate "Swamp
 * Herb" pickups, see data/HomeRegionContent.kt's Eastern Swamps) broke --
 * taking the first one hid ALL of them, since the filter couldn't tell the
 * physical items apart. Fixed by tracking by index instead (matching the
 * currentBeings()/defeatedAt pattern already used for beings).
 */
class GameSessionItemTrackingTest {

    private fun sessionWithDuplicateItems(): GameSession {
        val herb = Item(name = "Swamp Herb", kind = ItemKind.MATERIAL, tier = 1, value = 5, maxDurability = 1)
        val loc = GameLocation(
            id = "0_0", x = 0, y = 0, biome = Biome.PLAINS, name = "Swamp", description = "test",
            populationTier = PopulationTier.WILDERNESS, difficultyTier = 1, difficultyScore = 20,
            beings = emptyList(), exits = emptyMap(), items = listOf(herb, herb, herb),
        )
        val world = World(width = 1, height = 1, seed = 1L, locations = mapOf("0_0" to loc))
        val player = PlayerCharacterFactory.create("Test", eldoria.core.model.Race.HUMAN, eldoria.core.model.CharacterClass.WARRIOR, Random(1))
        return GameSession(world, player, "0_0", "0_0", Random(1))
    }

    @Test
    fun `three identically-named items can each be taken one at a time`() {
        val session = sessionWithDuplicateItems()

        assertEquals(3, session.currentItems().size)
        val first = session.currentItems().first()
        session.markTaken(first.index)

        assertEquals(2, session.currentItems().size, "taking one Swamp Herb must leave the other two available, not hide all three")

        val second = session.currentItems().first()
        session.markTaken(second.index)
        assertEquals(1, session.currentItems().size)

        val third = session.currentItems().first()
        session.markTaken(third.index)
        assertTrue(session.currentItems().isEmpty())
    }

    @Test
    fun `taken-item state round-trips through a snapshot`() {
        val session = sessionWithDuplicateItems()
        session.markTaken(session.currentItems().first().index)
        assertEquals(2, session.currentItems().size)

        val snap = session.snapshot()
        val restored = sessionWithDuplicateItems()
        restored.restoreFrom(snap)
        assertEquals(2, restored.currentItems().size, "exactly one of the three should still read as taken after restoring")
    }
}
