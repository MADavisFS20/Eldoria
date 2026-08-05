package eldoria.core.data

import eldoria.core.model.Biome
import eldoria.core.model.Disposition
import eldoria.core.model.GameLocation
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.PopulationTier
import eldoria.core.model.SpawnEntry
import eldoria.core.model.SpawnKind
import eldoria.core.model.StatBlock
import eldoria.core.model.StatusEffect
import eldoria.core.model.TerrainKind
import eldoria.core.world.StatGenerator
import kotlin.random.Random

/**
 * The Python prototype's 15 hand-authored, tightly connected locations
 * (Oakhaven Village and its surrounding woods/mountains/coast), spliced
 * onto the deterministically-generated start city (see WorldGenerator's
 * `graft` call, right before it returns the World) so every new game keeps
 * this same tested content while Kotlin's much larger procedural world
 * remains reachable beyond it -- Oakhaven's `west` exit is the one
 * deliberate gateway out (see `graft`'s doc).
 *
 * Deliberately NOT wired through the procedural SideQuestKind/pickBeings
 * machinery: the Python source's quests are fetch-quests gated on specific
 * items or kill counts, resolved through a yes/no accept during `talk` and
 * an automatic turn-in on a later `talk` -- a different shape than
 * SideQuestKind's "resolve <keyword>" flavor-quest model (see
 * model/SideQuest.kt), and SpawnEntry.offersSideQuest is one-quest-per-NPC
 * while several of these NPCs (Elder Theron, Mountain Guide) give more
 * than one. Rather than force-fit either constraint, this is a small,
 * self-contained, faithfully-ported dialogue/quest system of its own,
 * driven from Game.kt's `talk()` (see `handleHomeRegionNpc`) using plain
 * string quest ids in GameSession.activeHomeRegionQuests/completedSideQuests
 * (see GameSession's doc on why NOT discoveredQuests).
 */
object HomeRegionContent {

    // --- Quest ids (GameSession.activeHomeRegionQuests / completedSideQuests keys) ---
    const val QUEST_ANCIENT_RELIC = "ancient_relic"
    const val QUEST_POISONED_WATERS = "poisoned_waters"
    const val QUEST_GOBLIN_OUTBREAK = "goblin_outbreak"
    const val QUEST_LOST_CARGO = "lost_cargo"
    const val QUEST_MOUNTAIN_RESCUE = "mountain_rescue"
    const val QUEST_SLAY_THE_WYRM = "slay_the_wyrm"
    const val QUEST_ALCHEMICAL_FUNGI = "alchemical_fungi"
    const val QUEST_ANCIENT_COMPASS = "ancient_compass"

    val questTitles: Map<String, String> = mapOf(
        QUEST_ANCIENT_RELIC to "The Ancient Relic",
        QUEST_POISONED_WATERS to "The Poisoned Waters",
        QUEST_GOBLIN_OUTBREAK to "Goblin Outbreak",
        QUEST_LOST_CARGO to "Lost Cargo",
        QUEST_MOUNTAIN_RESCUE to "Mountain Rescue",
        QUEST_SLAY_THE_WYRM to "Slay the Wyrm",
        QUEST_ALCHEMICAL_FUNGI to "Alchemical Fungi",
        QUEST_ANCIENT_COMPASS to "The Ancient Compass",
    )

    // --- Named NPCs (exact names Game.kt's handleHomeRegionNpc matches on) ---
    const val ELDER_THERON = "Elder Theron"
    const val FISHERMAN_FINN = "Fisherman Finn"
    const val MOUNTAIN_GUIDE = "Mountain Guide"
    const val ARCANE_VENDOR = "Arcane Vendor"
    const val ANCIENT_SCHOLAR = "Ancient Scholar"
    const val LOST_MINER = "Lost Miner"

    // Trader names deliberately contain a DialogueContentRegistry TRADER
    // keyword (trader/merchant/keeper/vendor) so Game.kt's openShop() finds
    // them with zero changes -- see world/ShopGenerator.kt's doc.
    const val OAKHAVEN_MERCHANT = "Oakhaven General Merchant"
    const val COASTAL_TRADER = "Coastal Market Trader"
    // Ironstone Outpost Keeper: the Python source defined a fourth shop
    // (`mountain_shop`) but never actually attached it to any location --
    // fixed here rather than ported faithfully, since leaving a fully
    // stocked shop permanently unreachable reads as an oversight, not
    // content worth preserving.
    const val MOUNTAIN_KEEPER = "Ironstone Outpost Keeper"

    // --- Quest item names (checked by name in Game.kt's handleHomeRegionNpc) ---
    const val ITEM_ANCIENT_RELIC = "Ancient Relic"
    const val ITEM_SWAMP_HERB = "Swamp Herb"
    const val ITEM_SHIP_MANIFEST = "Ship's Manifest"
    const val ITEM_LOST_MINER_NOTE = "Lost Miner's Note"
    const val ITEM_ANCIENT_COMPASS = "Ancient Compass"
    const val ITEM_GLOWING_MUSHROOM = "Glowing Mushroom"
    const val SWAMP_HERB_REQUIRED = 3
    const val GLOWING_MUSHROOM_REQUIRED = 2
    const val GOBLINS_REQUIRED = 3

    private fun enemy(name: String, tier: Int, seed: Long, resistances: Set<StatusEffect> = emptySet()): SpawnEntry =
        SpawnEntry(
            name = name,
            kind = SpawnKind.CREATURE,
            disposition = Disposition.HOSTILE,
            stats = StatGenerator.creatureStats(tier, Random(seed)).copy(statusResistances = resistances),
        )

    private fun npc(name: String, tier: Int = 1, seed: Long): SpawnEntry =
        SpawnEntry(
            name = name,
            kind = SpawnKind.NPC,
            disposition = Disposition.PASSIVE,
            stats = StatGenerator.creatureStats(tier, Random(seed)),
        )

    private fun goblin(seed: Long) = enemy("Goblin Scavenger", tier = 1, seed = seed)
    private fun direWolf(seed: Long) = enemy("Dire Wolf", tier = 1, seed = seed)
    private fun mountainGoat(seed: Long) = enemy("Mountain Goat", tier = 1, seed = seed)
    private fun giantToad(seed: Long) = enemy("Giant Toad", tier = 2, seed = seed, resistances = setOf(StatusEffect.BURN))
    private fun banditOutlaw(seed: Long) = enemy("Bandit Outlaw", tier = 2, seed = seed)
    private fun giantCrab(seed: Long) = enemy("Giant Crab", tier = 2, seed = seed, resistances = setOf(StatusEffect.POISON))
    private fun shadowCultist(seed: Long) = enemy("Shadow Cultist", tier = 3, seed = seed)
    private fun skeletalWarrior(seed: Long) = enemy("Skeletal Warrior", tier = 3, seed = seed, resistances = setOf(StatusEffect.POISON))
    private fun stoneGolem(seed: Long) = enemy("Stone Golem", tier = 4, seed = seed, resistances = setOf(StatusEffect.POISON, StatusEffect.BURN))
    private fun ancientDragon(seed: Long) = enemy("Ancient Flame Dragon", tier = 5, seed = seed, resistances = setOf(StatusEffect.BURN))

    private fun questItem(name: String, tier: Int, seed: Long): Item = StatGenerator.questItem(name, tier, Random(seed))
    private fun material(name: String, seed: Long): Item = StatGenerator.questItem(name, tier = 1, rng = Random(seed)).copy(kind = ItemKind.MATERIAL, value = 5)

    /**
     * Splices the 15 home-region locations into an already-generated
     * location map, anchored at (anchorX, anchorY) -- the same tile
     * Game.kt's start-city selection will land on (see WorldGenerator's
     * call site, which passes the deterministically-chosen start city's
     * own coordinates). Offsets are unique but NOT geometry-consistent
     * with each location's cardinal exits (MapRenderer's spatial display
     * is cosmetic-only, confirmed non-load-bearing -- see the Phase 2
     * research this was built from); every location's `exits` map is
     * hand-set to Python's original graph regardless of where it actually
     * sits on the grid.
     *
     * `exits` intentionally point INTO 14 ids this function itself
     * creates -- a fully closed loop, matching the Python source's
     * original topology exactly -- except Oakhaven's `west`, which is
     * deliberately left pointing at whatever real generated tile already
     * existed there before the graft (untouched by this function, since
     * it's not one of the 15 offsets below): the one gateway from the
     * tested home region out into Kotlin's much larger procedural world.
     */
    fun graft(locations: MutableMap<String, GameLocation>, anchorX: Int, anchorY: Int) {
        fun id(dx: Int, dy: Int) = "${anchorX + dx}_${anchorY + dy}"

        val idOakhaven = id(0, 0)
        val idWhisperingWoods = id(0, -1)
        val idDeepWoods = id(0, -2)
        val idShadowCaves = id(1, -1)
        val idSunkenCitadel = id(2, -1)
        val idOldRoad = id(1, 0)
        val idIronstoneFoothills = id(2, 0)
        val idIronstonePass = id(2, 1)
        val idDragonsPeak = id(2, 2)
        val idEasternSwamps = id(0, 1)
        val idCoastalTown = id(1, 1)
        val idSunkenShipwreck = id(1, 2)
        val idMountainPassNorth = id(3, 0)
        val idAncientRuins = id(-1, -2)
        val idForgottenCrypt = id(-1, -3)

        fun loc(
            locId: String, dx: Int, dy: Int, name: String, description: String,
            exits: Map<String, String>, populationTier: PopulationTier, difficultyTier: Int,
            beings: List<SpawnEntry> = emptyList(), items: List<Item> = emptyList(),
        ) {
            locations[locId] = GameLocation(
                id = locId, x = anchorX + dx, y = anchorY + dy, biome = Biome.PLAINS,
                name = name, description = description, populationTier = populationTier,
                difficultyTier = difficultyTier, difficultyScore = difficultyTier * 20,
                beings = beings, exits = exits, terrain = TerrainKind.LAND, items = items,
            )
        }

        val existingWestNeighbor = locations[id(-1, 0)]?.id ?: idOakhaven // falls back to a self-loop only in the pathological case that tile doesn't exist

        loc(
            idOakhaven, 0, 0, "Oakhaven Village",
            "A serene village surrounding a central square. The air smells of fresh bread and damp earth.",
            mapOf("north" to idWhisperingWoods, "east" to idOldRoad, "south" to idEasternSwamps, "west" to existingWestNeighbor),
            PopulationTier.CITY, difficultyTier = 1,
            beings = listOf(npc(ELDER_THERON, seed = 101), npc(OAKHAVEN_MERCHANT, seed = 102)),
        )
        loc(
            idWhisperingWoods, 0, -1, "Whispering Woods",
            "Dense forest with howling wind through misty trees. Ancient, gnarled trees loom overhead.",
            mapOf("south" to idOakhaven, "north" to idDeepWoods, "east" to idShadowCaves),
            PopulationTier.WILDERNESS, difficultyTier = 1,
            beings = listOf(direWolf(201), goblin(202)),
        )
        loc(
            idDeepWoods, 0, -2, "Deep Whispering Woods",
            "Pitch dark canopy where sunlight cannot reach. Strange sounds echo from the shadows.",
            mapOf("south" to idWhisperingWoods, "west" to idAncientRuins),
            PopulationTier.WILDERNESS, difficultyTier = 2,
            beings = listOf(goblin(203), direWolf(204)),
            items = listOf(questItem(ITEM_ANCIENT_RELIC, tier = 2, seed = 301)),
        )
        loc(
            idShadowCaves, 1, -1, "Shadow Caves",
            "Damp limestone cave network dripping with glowing flora. The air is cool and still.",
            mapOf("west" to idWhisperingWoods, "east" to idSunkenCitadel),
            PopulationTier.WILDERNESS, difficultyTier = 2,
            beings = listOf(goblin(205), giantToad(206)),
            items = listOf(material(ITEM_GLOWING_MUSHROOM, seed = 302), material(ITEM_GLOWING_MUSHROOM, seed = 303)),
        )
        loc(
            idSunkenCitadel, 2, -1, "Sunken Citadel Courtyard",
            "Ancient flooded stone fortress radiating dark power. Water laps at crumbling walls.",
            mapOf("west" to idShadowCaves),
            PopulationTier.CITY, difficultyTier = 3,
            beings = listOf(npc(ARCANE_VENDOR, seed = 103), shadowCultist(207), skeletalWarrior(208)),
        )
        loc(
            idOldRoad, 1, 0, "Old Forest Road",
            "Long dirt path connecting distant provinces. Wagon tracks are faintly visible.",
            mapOf("west" to idOakhaven, "east" to idIronstoneFoothills, "south" to idCoastalTown),
            PopulationTier.WILDERNESS, difficultyTier = 1,
            beings = listOf(goblin(209), banditOutlaw(210)),
        )
        loc(
            idIronstoneFoothills, 2, 0, "Ironstone Foothills",
            "Rocky ascending terrain surrounded by jagged cliff faces. The wind picks up here.",
            mapOf("west" to idOldRoad, "north" to idIronstonePass, "east" to idMountainPassNorth),
            PopulationTier.CITY, difficultyTier = 2,
            beings = listOf(npc(MOUNTAIN_GUIDE, seed = 104), npc(MOUNTAIN_KEEPER, seed = 105), banditOutlaw(211), mountainGoat(212)),
        )
        loc(
            idIronstonePass, 2, 1, "Ironstone Mountain Pass",
            "Freezing mountain path with howling blizzards. The air is thin and cold.",
            mapOf("south" to idIronstoneFoothills, "up" to idDragonsPeak),
            PopulationTier.WILDERNESS, difficultyTier = 4,
            beings = listOf(stoneGolem(213), mountainGoat(214)),
        )
        loc(
            idDragonsPeak, 2, 2, "Dragon's Peak Summit",
            "High volcanic summit covered in ancient scorch marks. A faint smell of sulfur lingers.",
            mapOf("down" to idIronstonePass),
            PopulationTier.WILDERNESS, difficultyTier = 5,
            beings = listOf(ancientDragon(215)),
        )
        loc(
            idEasternSwamps, 0, 1, "Eastern Swamps",
            "A murky, humid marshland. Strange plants and buzzing insects fill the air.",
            mapOf("north" to idOakhaven),
            PopulationTier.WILDERNESS, difficultyTier = 1,
            beings = listOf(giantToad(216), direWolf(217)),
            items = List(SWAMP_HERB_REQUIRED) { material(ITEM_SWAMP_HERB, seed = 310L + it) },
        )
        loc(
            idCoastalTown, 1, 1, "Coastal Town of Port Eldoria",
            "A bustling port town with the scent of salt and fish. Ships dock constantly.",
            mapOf("north" to idOldRoad, "east" to idSunkenShipwreck),
            PopulationTier.CITY, difficultyTier = 2,
            beings = listOf(npc(FISHERMAN_FINN, seed = 106), npc(COASTAL_TRADER, seed = 107)),
        )
        loc(
            idSunkenShipwreck, 1, 2, "Sunken Shipwreck",
            "The remains of a grand ship, half-submerged in shallow waters.",
            mapOf("west" to idCoastalTown),
            PopulationTier.WILDERNESS, difficultyTier = 2,
            beings = listOf(giantCrab(218)),
            items = listOf(questItem(ITEM_SHIP_MANIFEST, tier = 2, seed = 304)),
        )
        loc(
            idMountainPassNorth, 3, 0, "Northern Mountain Pass",
            "A narrow, icy path winding through towering peaks.",
            mapOf("west" to idIronstoneFoothills, "north" to idForgottenCrypt),
            PopulationTier.WILDERNESS, difficultyTier = 3,
            beings = listOf(mountainGoat(219), stoneGolem(220), npc(LOST_MINER, seed = 108)),
        )
        loc(
            idAncientRuins, -1, -2, "Ancient Ruins",
            "Crumbling stone structures overgrown with vines.",
            mapOf("east" to idDeepWoods, "north" to idForgottenCrypt),
            PopulationTier.WILDERNESS, difficultyTier = 3,
            beings = listOf(skeletalWarrior(221), shadowCultist(222), npc(ANCIENT_SCHOLAR, seed = 109)),
        )
        loc(
            idForgottenCrypt, -1, -3, "Forgotten Crypt",
            "A dark, musty crypt beneath the ancient ruins.",
            mapOf("south" to idAncientRuins, "west" to idMountainPassNorth),
            PopulationTier.WILDERNESS, difficultyTier = 4,
            beings = listOf(skeletalWarrior(223)),
            items = listOf(questItem(ITEM_ANCIENT_COMPASS, tier = 3, seed = 305)),
        )
    }
}
