package eldoria.core.world

import eldoria.core.game.GameSession
import eldoria.core.model.CharacterClass
import eldoria.core.model.HiredCompanion
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.Perk
import eldoria.core.model.Race
import eldoria.core.model.Subclass
import java.io.File
import kotlin.random.Random
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/**
 * Direct round-trip test for the Phase 0 kotlinx.serialization + JSON
 * rewrite of SaveManager (previously plain java.io.Serializable object
 * streams). Deliberately bypasses actual gameplay (no interactive RNG
 * dependency on e.g. hostile-free `sleep` spots) and exercises every field
 * type in the Snapshot graph directly, including the "exotic" nested types
 * (HiredCompanion, an equipped Item with a MagicEffect, a non-string-keyed
 * nested map) that are easiest to silently break in a serialization rewrite.
 */
class SaveManagerTest {

    @BeforeTest
    @AfterTest
    fun cleanSaveFiles() {
        File("eldoria_save.json").delete()
        File("eldoria_save.json.tmp").delete()
    }

    private fun buildSnapshot(): GameSession.Snapshot {
        val rng = Random(42)
        val player = PlayerCharacterFactory.create("RoundTripHero", Race.DWARF, CharacterClass.PALADIN, rng)
            .copy(
                gold = 777,
                level = 3,
                perks = mapOf(Perk.TOUGHNESS to 1, Perk.IRON_SKIN to 3),
                subclass = Subclass.VAMPIRE,
                companion = HiredCompanion(
                    name = "Loyal Retainer",
                    attackBonus = 4,
                    armorClass = 14,
                    damage = eldoria.core.model.DiceFormula(1, eldoria.core.model.DieType.D8, 2),
                    originLocationId = "loc-1",
                    hiredAtMillis = 1_700_000_000_000L,
                ),
                inventory = listOf(
                    Item(
                        name = "Ring of Cursed Fortune",
                        kind = ItemKind.TRINKET,
                        tier = 3,
                        magicEffect = eldoria.core.model.MagicEffect("Cursed Luck", "willpower", -2, beneficial = false),
                        value = 250,
                        maxDurability = 1,
                    ),
                ),
            )
        return GameSession.Snapshot(
            seed = 123456789L,
            player = player,
            locationId = "loc-1",
            homeLocationId = "loc-1",
            subRealmId = "dungeon-3",
            subRealmRoomId = "room-7",
            gameTick = 42,
            discoveredLocations = setOf("loc-1", "loc-2", "loc-3"),
            // Int-keyed inner map -- not string keys, the case that needs
            // kotlinx.serialization's structured-map-key JSON support.
            defeatedAt = mapOf("loc-2" to mapOf(0 to 5, 3 to 12)),
            departedAt = mapOf("loc-1" to 40),
            takenItems = mapOf("loc-2" to setOf("Rusty Key")),
            discoveredQuests = setOf("quest-a"),
            completedQuests = setOf("quest-a"),
            bestiary = setOf("Goblin Scavenger", "Dire Wolf"),
            finalBattleUnlocked = true,
            finalBattleWon = false,
            completedSideQuests = setOf("side-1", "side-2"),
        )
    }

    @Test
    fun `save then load round-trips every field exactly`() {
        val original = buildSnapshot()

        assertFalse(SaveManager.exists(), "no stray save file should exist before the test writes one")
        SaveManager.save(original)
        assertTrue(SaveManager.exists())

        val loaded = SaveManager.load()
        assertNotNull(loaded)
        assertEquals(original, loaded, "round-tripped snapshot must be structurally identical to the original")
    }

    @Test
    fun `load returns null when no save exists`() {
        assertFalse(SaveManager.exists())
        assertEquals(null, SaveManager.load())
    }

    @Test
    fun `save overwrites a previous save rather than versioning it`() {
        SaveManager.save(buildSnapshot())
        val second = buildSnapshot().copy(gameTick = 999)
        SaveManager.save(second)

        val loaded = SaveManager.load()
        assertEquals(999, loaded?.gameTick)
        assertFalse(File("eldoria_save.json.tmp").exists(), "temp file must not linger after a successful save")
    }
}
