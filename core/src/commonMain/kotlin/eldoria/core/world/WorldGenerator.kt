package eldoria.core.world

import eldoria.core.data.BiomeContentRegistry
import eldoria.core.data.DungeonContentRegistry
import eldoria.core.data.FamilyContentRegistry
import eldoria.core.data.HomeRegionContent
import eldoria.core.data.SkillTrainerContentRegistry
import eldoria.core.data.SkyContentRegistry
import eldoria.core.data.TrainerTemplate
import eldoria.core.model.ArtifactKind
import eldoria.core.model.Biome
import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.Disposition
import eldoria.core.model.GameLocation
import eldoria.core.model.HazardKind
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.PopulationTier
import eldoria.core.model.RealmKind
import eldoria.core.model.SideQuestKind
import eldoria.core.model.SpawnEntry
import eldoria.core.model.SpawnKind
import eldoria.core.model.SubRealm
import eldoria.core.model.Subclass
import eldoria.core.model.TerrainKind
import eldoria.core.model.World
import kotlin.random.Random

/**
 * Deterministic, fully hardcoded-rules world generator. No AI, no network,
 * no runtime text generation beyond combining fixed word banks. The same
 * seed always produces the exact same map.
 */
object WorldGenerator {

    private data class CellInfo(val biome: Biome, val tier: Int, val score: Int)

    private fun cellRandom(worldSeed: Long, x: Int, y: Int, salt: Int = 0): Random =
        DeterministicRandom.random(worldSeed, x.toLong(), y.toLong(), salt.toLong())

    private fun manhattan(a: Pair<Int, Int>, b: Pair<Int, Int>) =
        kotlin.math.abs(a.first - b.first) + kotlin.math.abs(a.second - b.second)

    private data class Portal(val subRealmId: String, val kind: RealmKind, val name: String, val description: String)

    fun generate(config: WorldConfig = WorldConfig()): World {
        require(config.width * config.height >= 10_000) { "Map must contain at least 10,000 locations" }

        val biomeOrder = Biome.entries.toList() // 6 bands, left (west) to right (east)
        val bandCount = biomeOrder.size

        // --- 1. Per-row jittered band boundaries (jagged borders between biomes) ---
        fun boundariesForRow(row: Int): IntArray {
            val w = config.width
            val ideal = IntArray(bandCount - 1) { i -> (w * (i + 1)) / bandCount }
            val jittered = IntArray(bandCount - 1)
            for (i in ideal.indices) {
                val r = cellRandom(config.seed, i, row, salt = 9001)
                jittered[i] = (ideal[i] + r.nextInt(-3, 4)).coerceIn(1, w - 1)
            }
            for (i in 1 until jittered.size) {
                if (jittered[i] <= jittered[i - 1] + 5) jittered[i] = jittered[i - 1] + 5
            }
            if (jittered.isNotEmpty() && jittered.last() >= w - 5) jittered[jittered.size - 1] = w - 5
            val boundaries = IntArray(bandCount + 1)
            boundaries[0] = 0
            for (i in jittered.indices) boundaries[i + 1] = jittered[i]
            boundaries[bandCount] = w
            return boundaries
        }

        // --- 2. Compute biome + difficulty for every cell ---
        val grid = Array(config.height) { arrayOfNulls<CellInfo>(config.width) }
        for (y in 0 until config.height) {
            val boundaries = boundariesForRow(y)
            for (x in 0 until config.width) {
                var bandIndex = bandCount - 1
                for (i in 0 until bandCount) {
                    if (x >= boundaries[i] && x < boundaries[i + 1]) {
                        bandIndex = i
                        break
                    }
                }
                val bandStart = boundaries[bandIndex]
                val bandEnd = boundaries[bandIndex + 1]
                val bandWidth = (bandEnd - bandStart).coerceAtLeast(1)
                val localX = x - bandStart
                val frac = localX.toDouble() / (bandWidth - 1).coerceAtLeast(1)
                val score = (1 + (frac * 99.0)).toInt().coerceIn(1, 100)
                val tier = (((score - 1) / 20) + 1).coerceIn(1, 5)
                grid[y][x] = CellInfo(biomeOrder[bandIndex], tier, score)
            }
        }

        // --- 2.5. Carve waterways: rivers cut west-to-east through the 5 land
        // biomes (crossing multiple biome bands), impassable on foot except at
        // periodic bridges. The Sea biome's own open water is decided later,
        // once we know which of its cells are settlements/portals (those stay
        // dry land; everything else in the Sea band becomes open water).
        val terrainGrid = Array(config.height) { Array(config.width) { TerrainKind.LAND } }
        run {
            val riverRng = DeterministicRandom.random(config.seed, 13131L)
            val riverRows = mutableListOf<Int>()
            repeat(config.riverCount) {
                var row = riverRng.nextInt(8, config.height - 8)
                var guard = 0
                while (riverRows.any { kotlin.math.abs(it - row) < 12 } && guard < 30) {
                    row = riverRng.nextInt(8, config.height - 8)
                    guard++
                }
                riverRows.add(row)
            }
            for (row in riverRows) {
                var y = row
                val path = mutableListOf<Pair<Int, Int>>()
                for (x in 0 until config.width) {
                    val stepRng = cellRandom(config.seed, x, row, salt = 7777)
                    if (stepRng.nextInt(100) < 35) y += stepRng.nextInt(-1, 2)
                    y = y.coerceIn(2, config.height - 3)
                    path.add(x to y)
                    terrainGrid[y][x] = TerrainKind.WATERWAY
                }
                path.forEachIndexed { i, (bx, by) -> if (i % config.bridgeSpacing == config.bridgeSpacing / 2) terrainGrid[by][bx] = TerrainKind.BRIDGE }
            }
        }

        // --- 3. Group cells by biome & tier for settlement/portal placement ---
        // Land biomes only offer LAND cells as candidates (river/bridge cells are
        // never a settlement or dungeon site); the Sea biome offers every cell for
        // now -- whatever isn't claimed by a settlement/portal becomes open water below.
        val cellsByBiomeTier = HashMap<Biome, MutableMap<Int, MutableList<Pair<Int, Int>>>>()
        for (b in biomeOrder) cellsByBiomeTier[b] = HashMap()
        for (y in 0 until config.height) {
            for (x in 0 until config.width) {
                val info = grid[y][x]!!
                if (info.biome != Biome.SEA && terrainGrid[y][x] != TerrainKind.LAND) continue
                cellsByBiomeTier.getValue(info.biome).getOrPut(info.tier) { mutableListOf() }.add(x to y)
            }
        }

        fun placePoints(
            candidates: List<Pair<Int, Int>>,
            count: Int,
            minDist: Int,
            rng: Random,
            excluded: MutableSet<Pair<Int, Int>>,
        ): List<Pair<Int, Int>> {
            if (count <= 0) return emptyList()
            val shuffled = candidates.shuffled(rng)
            val chosen = mutableListOf<Pair<Int, Int>>()
            var dist = minDist
            while (chosen.size < count && dist >= 0) {
                for (c in shuffled) {
                    if (chosen.size >= count) break
                    if (c in excluded) continue
                    if (chosen.all { manhattan(it, c) >= dist }) chosen.add(c)
                }
                dist -= 3
            }
            excluded.addAll(chosen)
            return chosen
        }

        data class Settlement(val pos: Pair<Int, Int>, val name: String, val tier: PopulationTier)

        val settlementsByBiome = HashMap<Biome, List<Settlement>>()
        val trainerAt = HashMap<Pair<Int, Int>, TrainerTemplate>()

        // Main-quest premise: exactly one village in the whole world hides the
        // player's long-lost family member. Picked deterministically off the
        // world seed, so a given seed always hides the same relation in the
        // same village.
        val familyRng = DeterministicRandom.random(config.seed, 424242L)
        val familyRelation = FamilyContentRegistry.candidates.random(familyRng)
        val familyBiome = biomeOrder.random(familyRng)
        val familyVillageIndex = familyRng.nextInt(config.citiesPerBiome * config.villagesPerCity)
        val familyMemberAt = HashMap<Pair<Int, Int>, FamilyContentRegistry.FamilyRelation>()

        // 34 small side quests (26 currently authored -- see model/SideQuest.kt), spread
        // roughly evenly across all 12 cities, deterministic per seed.
        val allSideQuests = SideQuestKind.all.shuffled(DeterministicRandom.random(config.seed, 24681357L))
        val totalCities = biomeOrder.size * config.citiesPerBiome
        val questCountForCity = List(totalCities) { i -> allSideQuests.size / totalCities + (if (i < allSideQuests.size % totalCities) 1 else 0) }
        val sideQuestAt = HashMap<Pair<Int, Int>, List<SideQuestKind>>()
        var globalCityIndex = 0
        var questCursor = 0

        for (biome in biomeOrder) {
            val content = BiomeContentRegistry[biome]
            val excluded = mutableSetOf<Pair<Int, Int>>()
            val rng = DeterministicRandom.random(config.seed, biome.ordinal.toLong(), 42L)

            val cityCandidates = cellsByBiomeTier.getValue(biome)[1].orEmpty()
            val cities = placePoints(cityCandidates, config.citiesPerBiome, minDist = 20, rng, excluded)

            val villageCandidates =
                (cellsByBiomeTier.getValue(biome)[1].orEmpty() + cellsByBiomeTier.getValue(biome)[2].orEmpty())
            val villageCount = config.citiesPerBiome * config.villagesPerCity
            val villages = placePoints(villageCandidates, villageCount, minDist = 7, rng, excluded)

            val settlements = mutableListOf<Settlement>()
            cities.forEachIndexed { i, pos ->
                settlements.add(Settlement(pos, content.cityNames[i % content.cityNames.size], PopulationTier.CITY))
                SkillTrainerContentRegistry.trainerFor(biome, i)?.let { trainerAt[pos] = it }
                val questCount = questCountForCity[globalCityIndex]
                sideQuestAt[pos] = allSideQuests.subList(questCursor, questCursor + questCount)
                questCursor += questCount
                globalCityIndex++
            }
            villages.forEachIndexed { i, pos ->
                settlements.add(Settlement(pos, content.villageNames[i % content.villageNames.size], PopulationTier.COUNTRYSIDE))
                if (biome == familyBiome && i == familyVillageIndex) familyMemberAt[pos] = familyRelation
            }
            settlementsByBiome[biome] = settlements
        }

        val settlementAt = HashMap<Pair<Int, Int>, Settlement>()
        settlementsByBiome.values.flatten().forEach { settlementAt[it.pos] = it }

        // --- 4. Place dungeon (underground) and beanstalk (sky) portals ---
        val excludedCells = settlementAt.keys.toMutableSet()
        val allSubRealms = LinkedHashMap<String, SubRealm>()
        val portalAt = HashMap<Pair<Int, Int>, Portal>()
        val usedRealmNames = mutableSetOf<String>()
        val usedBossNames = mutableSetOf<String>()
        val usedLegendaryNames = mutableSetOf<String>()
        val usedQuestItemNames = mutableSetOf<String>()
        var skyVariantCounter = 0

        for (biome in biomeOrder) {
            val rng = DeterministicRandom.random(config.seed, biome.ordinal.toLong(), 777L)

            // Dungeon mouths hide in the more dangerous reaches of the biome where possible.
            val dangerousCandidates = (3..5).flatMap { cellsByBiomeTier.getValue(biome)[it].orEmpty() }
            val allBiomeCells = cellsByBiomeTier.getValue(biome).values.flatten()
            val dungeonCandidates = if (dangerousCandidates.size >= config.dungeonsPerBiome * 3) dangerousCandidates else allBiomeCells

            val dungeonSpots = placePoints(dungeonCandidates, config.dungeonsPerBiome, minDist = 15, rng, excludedCells)
            val dungeonTheme = DungeonContentRegistry[biome]
            for (spot in dungeonSpots) {
                val locId = "${spot.first}_${spot.second}"
                val subRealm = SubRealmGenerator.generate(
                    kind = RealmKind.DUNGEON,
                    biome = biome,
                    theme = dungeonTheme,
                    entranceLocationId = locId,
                    worldSeed = config.seed,
                    roomCountRange = config.dungeonRoomCountRange,
                    usedRealmNames = usedRealmNames,
                    usedBossNames = usedBossNames,
                    usedLegendaryNames = usedLegendaryNames,
                    usedQuestItemNames = usedQuestItemNames,
                )
                allSubRealms[subRealm.id] = subRealm
                portalAt[spot] = Portal(
                    subRealm.id, RealmKind.DUNGEON,
                    "Entrance to ${subRealm.name}",
                    "A dark cave mouth yawns in the earth here, leading down into ${subRealm.name}. Something ancient stirs below.",
                )
            }

            // Beanstalks can sprout anywhere in the biome, not just its dangerous edges.
            val beanstalkSpots = placePoints(allBiomeCells, config.beanstalksPerBiome, minDist = 15, rng, excludedCells)
            for (spot in beanstalkSpots) {
                val locId = "${spot.first}_${spot.second}"
                val variant = SkyContentRegistry.variants[skyVariantCounter % SkyContentRegistry.variants.size]
                skyVariantCounter++
                val subRealm = SubRealmGenerator.generate(
                    kind = RealmKind.SKY_REALM,
                    biome = biome,
                    theme = variant,
                    entranceLocationId = locId,
                    worldSeed = config.seed,
                    roomCountRange = config.skyRoomCountRange,
                    usedRealmNames = usedRealmNames,
                    usedBossNames = usedBossNames,
                    usedLegendaryNames = usedLegendaryNames,
                    usedQuestItemNames = usedQuestItemNames,
                )
                allSubRealms[subRealm.id] = subRealm
                portalAt[spot] = Portal(
                    subRealm.id, RealmKind.SKY_REALM,
                    "Beanstalk to ${subRealm.name}",
                    "An impossibly tall beanstalk climbs into the clouds here, leading up into ${subRealm.name}.",
                )
            }
        }

        // --- 4.5. Everything in the Sea band that isn't a settlement or portal is open water. ---
        for (y in 0 until config.height) {
            for (x in 0 until config.width) {
                if (grid[y][x]!!.biome == Biome.SEA && (x to y) !in settlementAt && (x to y) !in portalAt) {
                    terrainGrid[y][x] = TerrainKind.WATERWAY
                }
            }
        }

        // --- 4.6. Three sunken treasures, hidden on random open-sea tiles -- a small side quest for a boat owner to go find. ---
        val treasureRng = DeterministicRandom.random(config.seed, 24680L)
        val seaWaterCells = (0 until config.height).flatMap { y -> (0 until config.width).map { x -> x to y } }
            .filter { (x, y) -> grid[y][x]!!.biome == Biome.SEA && terrainGrid[y][x] == TerrainKind.WATERWAY }
        val treasureNames = listOf("Sunken Treasure Chest", "Barnacled Strongbox", "Corsair's Buried Hoard")
        val treasureAt = HashMap<Pair<Int, Int>, Item>()
        seaWaterCells.shuffled(treasureRng).take(3).forEachIndexed { i, pos ->
            val value = DiceFormula(6, DieType.D20, 150).roll(treasureRng)
            treasureAt[pos] = Item(
                name = treasureNames[i % treasureNames.size], kind = ItemKind.TRINKET, tier = 5,
                value = value, maxDurability = 1, isLegendary = true,
            )
        }

        // --- 4.7. Vampire and Werewolf curse-givers -- exactly one of each, in a
        // fittingly dangerous corner of the world, mutually exclusive once a
        // player picks one (see model/Subclass.kt, Game.kt's `request`).
        val curseRng = DeterministicRandom.random(config.seed, 555999L)
        val subclassGiverAt = HashMap<Pair<Int, Int>, Subclass>()
        val vampireSpot = (4..5).flatMap { cellsByBiomeTier.getValue(Biome.TUNDRA)[it].orEmpty() }
            .filterNot { it in excludedCells }.randomOrNull(curseRng)
        vampireSpot?.let { subclassGiverAt[it] = Subclass.VAMPIRE; excludedCells.add(it) }
        val werewolfSpot = (4..5).flatMap { cellsByBiomeTier.getValue(Biome.JUNGLE)[it].orEmpty() }
            .filterNot { it in excludedCells }.randomOrNull(curseRng)
        werewolfSpot?.let { subclassGiverAt[it] = Subclass.WEREWOLF; excludedCells.add(it) }

        // --- 4.8. The Mad Scientist -- one homeless tinkerer, in exactly one city
        // in the whole world (that city stands in as "the Kingdom's most advanced").
        val madScienceRng = DeterministicRandom.random(config.seed, 741852L)
        val madScientistAt = settlementAt.entries.filter { it.value.tier == PopulationTier.CITY }
            .map { it.key }.randomOrNull(madScienceRng)

        // --- 4.9. Three hidden sci-fi artifacts, one each in a distant, dangerous
        // corner of Desert, Mountains, and Tundra -- picked up, they auto-activate
        // and stay with the character forever (see model/Artifact.kt, Game.kt's `take`).
        val artifactRng = DeterministicRandom.random(config.seed, 99001122L)
        val artifactBiomes = mapOf(
            Biome.DESERT to ArtifactKind.TELEPATH_DEVICE,
            Biome.MOUNTAINS to ArtifactKind.COERCION_DEVICE,
            Biome.TUNDRA to ArtifactKind.PRECOGNITION_DEVICE,
        )
        val artifactAt = HashMap<Pair<Int, Int>, Item>()
        for ((biome, kind) in artifactBiomes) {
            val spot = (4..5).flatMap { cellsByBiomeTier.getValue(biome)[it].orEmpty() }
                .filterNot { it in excludedCells }.randomOrNull(artifactRng) ?: continue
            excludedCells.add(spot)
            artifactAt[spot] = Item(name = kind.itemName, kind = ItemKind.TRINKET, tier = 5, value = 0, maxDurability = 1, isLegendary = true)
        }

        // --- 5. Build every GameLocation ---
        fun wildernessName(biome: Biome, x: Int, y: Int): String {
            val content = BiomeContentRegistry[biome]
            val rng = cellRandom(config.seed, x, y, salt = 1)
            val adjective = content.adjectives.random(rng)
            val feature = content.features.random(rng)
            return if (rng.nextInt(100) < 30) {
                "${content.qualifiers.random(rng)} $adjective $feature"
            } else {
                "$adjective $feature"
            }
        }

        fun wildernessDescription(biome: Biome, name: String, tier: Int): String {
            val dangerLine = when (tier) {
                1 -> "It feels peaceful here; little seems capable of doing you harm."
                2 -> "A faint sense of caution lingers in the air."
                3 -> "This place feels genuinely dangerous."
                4 -> "Every sound puts you on edge; something powerful could be near."
                else -> "A deep, ancient dread hangs over this place."
            }
            return "You stand in the $name, deep within the ${biome.displayName.lowercase()}. $dangerLine"
        }

        fun settlementDescription(biome: Biome, name: String, tier: PopulationTier): String =
            if (tier == PopulationTier.CITY)
                "$name rises before you, a major hub of civilization amid the ${biome.displayName.lowercase()}, bustling with residents and travelers."
            else
                "$name is a small, close-knit settlement in the ${biome.displayName.lowercase()}, quiet but for the daily business of its few residents."

        fun riverName(biome: Biome, terrain: TerrainKind): String =
            if (terrain == TerrainKind.BRIDGE) "${biome.displayName} River Crossing" else "${biome.displayName} River"

        fun riverDescription(biome: Biome, terrain: TerrainKind): String =
            if (terrain == TerrainKind.BRIDGE)
                "A weathered bridge carries the path across the river here, water rushing beneath the planks."
            else
                "A river cuts across the ${biome.displayName.lowercase()} here -- too deep and swift to cross on foot. You would need a boat, or a bridge."

        // Wilderness is mostly empty on purpose -- the world should feel like open
        // country you can walk through, not a monster closet on every tile.
        fun pickBeings(biome: Biome, tier: Int, populationTier: PopulationTier, x: Int, y: Int): List<SpawnEntry> {
            val content = BiomeContentRegistry[biome]
            val rng = cellRandom(config.seed, x, y, salt = 2)
            val beings = mutableListOf<SpawnEntry>()
            when (populationTier) {
                PopulationTier.WILDERNESS -> {
                    val pool = content.creaturesFor(tier)
                    if (pool.isNotEmpty()) {
                        // Roll how many separate creature *encounters* this tile has (usually 0 or 1),
                        // then for each encounter, roll a template and spawn its whole pack size at
                        // once -- a lone Yeti, but wolves and raiders show up 2-4 at a time together.
                        val roll = rng.nextInt(100)
                        val encounters = when {
                            roll < 55 -> 0
                            roll < 90 -> 1
                            else -> 2
                        }
                        repeat(encounters) {
                            val t = pool.random(rng)
                            val groupSize = if (t.packSize.last > 1) t.packSize.random(rng) else 1
                            repeat(groupSize) {
                                beings.add(SpawnEntry(t.name, SpawnKind.CREATURE, t.disposition, StatGenerator.creatureStats(tier, rng)))
                            }
                        }
                    }
                    if (rng.nextInt(100) < 5) {
                        val npcPool = content.npcsFor(tier)
                        if (npcPool.isNotEmpty()) {
                            val t = npcPool.random(rng)
                            beings.add(SpawnEntry(t.name, SpawnKind.NPC, t.disposition, StatGenerator.creatureStats(tier, rng)))
                        }
                    }
                    subclassGiverAt[x to y]?.let { subclass ->
                        val name = if (subclass == Subclass.VAMPIRE) "Countess Mireille, the Pale Widow" else "Kael Thornfang, the Lone Howler"
                        beings.add(
                            SpawnEntry(
                                name, SpawnKind.NPC, Disposition.PASSIVE,
                                StatGenerator.creatureStats(5, rng), offersSubclass = subclass,
                            )
                        )
                    }
                }
                PopulationTier.COUNTRYSIDE, PopulationTier.CITY -> {
                    val npcPool = content.npcsFor(tier).filter { it.disposition == Disposition.PASSIVE }
                    val count = if (populationTier == PopulationTier.CITY) rng.nextInt(4, 7) else rng.nextInt(2, 5)
                    val chosenNpcs = npcPool.shuffled(rng).take(count)
                    // Every city (not village) has exactly one of its civilians willing to be hired as a companion,
                    // plus a couple more each carrying one of the world's 26 small side quests.
                    val companionPick = if (populationTier == PopulationTier.CITY) chosenNpcs.randomOrNull(rng) else null
                    val questsHere = if (populationTier == PopulationTier.CITY) sideQuestAt[x to y].orEmpty() else emptyList()
                    val questAssignment = chosenNpcs.filter { it != companionPick }.shuffled(rng).zip(questsHere).toMap()
                    chosenNpcs.forEach { t ->
                        beings.add(
                            SpawnEntry(
                                t.name, SpawnKind.NPC, t.disposition, StatGenerator.creatureStats(tier, rng),
                                offersCompanionship = t == companionPick,
                                offersSideQuest = questAssignment[t],
                            )
                        )
                    }
                    if (rng.nextInt(100) < 8) {
                        val hostilePool = content.npcsFor(tier).filter { it.disposition == Disposition.HOSTILE }
                        if (hostilePool.isNotEmpty()) {
                            val t = hostilePool.random(rng)
                            beings.add(SpawnEntry(t.name, SpawnKind.NPC, t.disposition, StatGenerator.creatureStats(tier, rng)))
                        }
                    }
                    trainerAt[x to y]?.let { trainer ->
                        beings.add(
                            SpawnEntry(
                                trainer.name, SpawnKind.NPC, Disposition.PASSIVE,
                                StatGenerator.creatureStats(tier, rng), teachesSkill = trainer.skill,
                            )
                        )
                    }
                    familyMemberAt[x to y]?.let { relation ->
                        beings.add(
                            SpawnEntry(
                                "${relation.name}, your long-lost ${relation.relation}", SpawnKind.NPC, Disposition.PASSIVE,
                                StatGenerator.creatureStats(tier, rng), isFamilyMember = true,
                            )
                        )
                    }
                    if (madScientistAt == (x to y)) {
                        beings.add(
                            SpawnEntry(
                                "Barnaby \"Bolt\" Higgins, the Homeless Tinkerer", SpawnKind.NPC, Disposition.PASSIVE,
                                StatGenerator.creatureStats(1, rng), offersBionicUpgrade = true,
                            )
                        )
                    }
                }
            }
            return beings
        }

        // Each biome has a couple of native environmental dangers (quicksand in the
        // desert, a cliff edge in the mountains, and so on) -- rare, and only ever on
        // plain wilderness ground (Sea's are on open water instead), never a settlement/river/portal.
        fun hazardFor(biome: Biome, x: Int, y: Int, terrain: TerrainKind, populationTier: PopulationTier): HazardKind? {
            if (populationTier != PopulationTier.WILDERNESS) return null
            val eligible = if (biome == Biome.SEA) terrain == TerrainKind.WATERWAY else terrain == TerrainKind.LAND
            if (!eligible) return null
            val rng = cellRandom(config.seed, x, y, salt = 8888)
            if (rng.nextInt(1000) >= 25) return null // ~2.5% of eligible tiles
            return HazardKind.forBiome(biome).random(rng)
        }

        val locations = HashMap<String, GameLocation>(config.width * config.height)
        for (y in 0 until config.height) {
            for (x in 0 until config.width) {
                val info = grid[y][x]!!
                val terrain = terrainGrid[y][x]
                val settlement = settlementAt[x to y]
                val portal = portalAt[x to y]
                val populationTier = settlement?.tier ?: PopulationTier.WILDERNESS
                // A river cutting through a *land* biome is its own kind of tile; the Sea biome's
                // open water reuses the normal (already nautical) wilderness name/description content.
                val isLandRiver = info.biome != Biome.SEA && terrain != TerrainKind.LAND
                val hazard = hazardFor(info.biome, x, y, terrain, populationTier)

                val name = when {
                    settlement != null -> settlement.name
                    portal != null -> portal.name
                    isLandRiver -> riverName(info.biome, terrain)
                    else -> wildernessName(info.biome, x, y)
                }
                val treasure = treasureAt[x to y]
                val artifact = artifactAt[x to y]
                val description = when {
                    settlement != null -> settlementDescription(info.biome, name, populationTier) +
                        (if (madScientistAt == (x to y)) " Word has it this is the most advanced city in the whole Kingdom." else "")
                    portal != null -> portal.description
                    isLandRiver -> riverDescription(info.biome, terrain)
                    else -> wildernessDescription(info.biome, name, info.tier) +
                        (if (treasure != null) " Something glints beneath the waves here." else "") +
                        (if (artifact != null) " Something utterly out of place lies half-buried here, catching the light strangely." else "") +
                        (if (hazard != null) " ${hazard.encounterLine}" else "")
                }

                val exits = LinkedHashMap<String, String>()
                if (y > 0) exits["north"] = "${x}_${y - 1}"
                if (y < config.height - 1) exits["south"] = "${x}_${y + 1}"
                if (x < config.width - 1) exits["east"] = "${x + 1}_${y}"
                if (x > 0) exits["west"] = "${x - 1}_${y}"

                // River tiles in land biomes are just an obstacle to cross, not an encounter --
                // no wolves swimming the rapids. Sea water keeps its normal (nautical) encounters.
                val beings = when {
                    portal != null && settlement == null -> emptyList()
                    isLandRiver -> emptyList()
                    else -> pickBeings(info.biome, info.tier, populationTier, x, y)
                }

                val id = "${x}_${y}"
                locations[id] = GameLocation(
                    id = id,
                    x = x,
                    y = y,
                    biome = info.biome,
                    name = name,
                    description = description,
                    populationTier = populationTier,
                    difficultyTier = info.tier,
                    difficultyScore = info.score,
                    beings = beings,
                    exits = exits,
                    portalId = portal?.subRealmId,
                    portalKind = portal?.kind,
                    terrain = terrain,
                    items = listOfNotNull(treasure, artifact),
                    hazard = hazard,
                )
            }
        }

        // Splice the Python prototype's tested 15-location home region onto
        // whichever tile Game.kt's own start-city selection will land on --
        // same filter/tie-break rule duplicated here (rather than passed
        // in) so this stays correct even if Game.kt's own start-location
        // logic is ever read before this returns. See data/HomeRegionContent's doc.
        val homeAnchor = locations.values
            .filter { it.biome == Biome.PLAINS && it.populationTier == PopulationTier.CITY }
            .minByOrNull { it.id } ?: locations.values.first { it.populationTier == PopulationTier.CITY }
        HomeRegionContent.graft(locations, homeAnchor.x, homeAnchor.y)

        return World(config.width, config.height, config.seed, locations, allSubRealms)
    }
}
