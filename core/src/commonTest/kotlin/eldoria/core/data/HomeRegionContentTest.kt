package eldoria.core.data

import eldoria.core.model.GameLocation
import eldoria.core.model.PopulationTier
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * Direct test of HomeRegionContent.graft() -- the pure, commonMain part of
 * the Phase 2 world-splice (WorldGenerator's call site and the deterministic
 * start-city selection it depends on are covered by the jvmMain smoke test
 * instead, since they need a full generated World).
 */
class HomeRegionContentTest {

    /** A minimal stand-in world: just enough neighbor tiles for graft() to have something to read/leave alone. */
    private fun fakeSurroundingLocations(anchorX: Int, anchorY: Int): MutableMap<String, GameLocation> {
        val map = mutableMapOf<String, GameLocation>()
        for (dx in -2..4) {
            for (dy in -4..3) {
                val x = anchorX + dx
                val y = anchorY + dy
                val id = "${x}_${y}"
                map[id] = GameLocation(
                    id = id, x = x, y = y, biome = eldoria.core.model.Biome.PLAINS,
                    name = "Wild $id", description = "placeholder",
                    populationTier = PopulationTier.WILDERNESS, difficultyTier = 1, difficultyScore = 20,
                    beings = emptyList(), exits = emptyMap(),
                )
            }
        }
        return map
    }

    @Test
    fun `graft adds exactly 15 locations`() {
        val locations = fakeSurroundingLocations(50, 50)
        val before = locations.size
        HomeRegionContent.graft(locations, 50, 50)
        // 15 locations replace 15 previously-wilderness tiles at the same
        // ids (the offsets are all pre-existing keys in fakeSurroundingLocations),
        // so total count is unchanged, but 15 specific entries must now be
        // the home-region content rather than the wilderness placeholder.
        assertEquals(before, locations.size, "graft replaces existing tiles at its offsets, it doesn't grow the map")
        val homeNames = setOf(
            "Oakhaven Village", "Whispering Woods", "Deep Whispering Woods", "Shadow Caves",
            "Sunken Citadel Courtyard", "Old Forest Road", "Ironstone Foothills", "Ironstone Mountain Pass",
            "Dragon's Peak Summit", "Eastern Swamps", "Coastal Town of Port Eldoria", "Sunken Shipwreck",
            "Northern Mountain Pass", "Ancient Ruins", "Forgotten Crypt",
        )
        assertEquals(15, homeNames.size)
        val actualNames = locations.values.map { it.name }.filter { it in homeNames }.toSet()
        assertEquals(homeNames, actualNames, "every one of the 15 named locations must be present in the map after graft")
    }

    @Test
    fun `every exit inside the home region resolves to a real location in the map`() {
        val locations = fakeSurroundingLocations(50, 50)
        HomeRegionContent.graft(locations, 50, 50)
        val oakhaven = locations.values.first { it.name == "Oakhaven Village" }
        val homeRegionIds = locations.values.filter {
            it.name in setOf(
                "Oakhaven Village", "Whispering Woods", "Deep Whispering Woods", "Shadow Caves",
                "Sunken Citadel Courtyard", "Old Forest Road", "Ironstone Foothills", "Ironstone Mountain Pass",
                "Dragon's Peak Summit", "Eastern Swamps", "Coastal Town of Port Eldoria", "Sunken Shipwreck",
                "Northern Mountain Pass", "Ancient Ruins", "Forgotten Crypt",
            )
        }.map { it.id }.toSet()

        for (loc in locations.values.filter { it.id in homeRegionIds }) {
            for ((direction, destId) in loc.exits) {
                assertTrue(destId in locations, "${loc.name}'s '$direction' exit points at $destId, which doesn't exist in the map")
            }
        }
        // Oakhaven's west exit is the one deliberate gateway out -- must NOT point at another home-region tile.
        val west = oakhaven.exits.getValue("west")
        assertTrue(west !in homeRegionIds, "Oakhaven's west exit should be the gateway to the wider world, not another home-region tile")
    }

    @Test
    fun `the home region graph is otherwise a closed loop except Oakhaven's west gateway`() {
        val locations = fakeSurroundingLocations(50, 50)
        HomeRegionContent.graft(locations, 50, 50)
        val homeRegionIds = locations.values.filter {
            it.name in setOf(
                "Oakhaven Village", "Whispering Woods", "Deep Whispering Woods", "Shadow Caves",
                "Sunken Citadel Courtyard", "Old Forest Road", "Ironstone Foothills", "Ironstone Mountain Pass",
                "Dragon's Peak Summit", "Eastern Swamps", "Coastal Town of Port Eldoria", "Sunken Shipwreck",
                "Northern Mountain Pass", "Ancient Ruins", "Forgotten Crypt",
            )
        }.map { it.id }.toSet()

        for (loc in locations.values.filter { it.id in homeRegionIds }) {
            val outsideExits = loc.exits.filterValues { it !in homeRegionIds }
            if (loc.name == "Oakhaven Village") {
                assertEquals(1, outsideExits.size, "Oakhaven should have exactly one exit leaving the home region (west)")
            } else {
                assertTrue(outsideExits.isEmpty(), "${loc.name} has an unexpected exit leaving the home region: $outsideExits")
            }
        }
    }

    @Test
    fun `named quest-giver NPCs are placed exactly where expected`() {
        val locations = fakeSurroundingLocations(50, 50)
        HomeRegionContent.graft(locations, 50, 50)
        val oakhaven = locations.values.first { it.name == "Oakhaven Village" }
        val ironstoneFoothills = locations.values.first { it.name == "Ironstone Foothills" }
        val sunkenCitadel = locations.values.first { it.name == "Sunken Citadel Courtyard" }

        assertTrue(oakhaven.beings.any { it.name == HomeRegionContent.ELDER_THERON })
        assertTrue(oakhaven.beings.any { it.name == HomeRegionContent.OAKHAVEN_MERCHANT })
        assertTrue(ironstoneFoothills.beings.any { it.name == HomeRegionContent.MOUNTAIN_GUIDE })
        assertTrue(ironstoneFoothills.beings.any { it.name == HomeRegionContent.MOUNTAIN_KEEPER })
        assertTrue(sunkenCitadel.beings.any { it.name == HomeRegionContent.ARCANE_VENDOR })
    }

    @Test
    fun `quest items are present at their source locations`() {
        val locations = fakeSurroundingLocations(50, 50)
        HomeRegionContent.graft(locations, 50, 50)
        val deepWoods = locations.values.first { it.name == "Deep Whispering Woods" }
        val shadowCaves = locations.values.first { it.name == "Shadow Caves" }
        val easternSwamps = locations.values.first { it.name == "Eastern Swamps" }

        assertTrue(deepWoods.items.any { it.name == HomeRegionContent.ITEM_ANCIENT_RELIC })
        assertEquals(HomeRegionContent.GLOWING_MUSHROOM_REQUIRED, shadowCaves.items.count { it.name == HomeRegionContent.ITEM_GLOWING_MUSHROOM })
        assertEquals(HomeRegionContent.SWAMP_HERB_REQUIRED, easternSwamps.items.count { it.name == HomeRegionContent.ITEM_SWAMP_HERB })
    }

    @Test
    fun `trader NPC names match a DialogueContentRegistry TRADER keyword`() {
        val traderNames = listOf(
            HomeRegionContent.OAKHAVEN_MERCHANT, HomeRegionContent.COASTAL_TRADER,
            HomeRegionContent.MOUNTAIN_KEEPER, HomeRegionContent.ARCANE_VENDOR,
        )
        for (name in traderNames) {
            assertEquals(NpcArchetype.TRADER, DialogueContentRegistry.archetypeFor(name), "$name must resolve to the TRADER archetype for Game.kt's openShop() to find it")
        }
    }
}
