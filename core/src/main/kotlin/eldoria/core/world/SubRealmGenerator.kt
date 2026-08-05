package eldoria.core.world

import eldoria.core.data.SubRealmTheme
import eldoria.core.model.Biome
import eldoria.core.model.Disposition
import eldoria.core.model.Item
import eldoria.core.model.QuestType
import eldoria.core.model.RealmKind
import eldoria.core.model.SpawnEntry
import eldoria.core.model.SpawnKind
import eldoria.core.model.SubRealm
import eldoria.core.model.SubRealmQuest
import eldoria.core.model.SubRealmRoom
import kotlin.random.Random

/**
 * Builds one dungeon (tunnels/caves) or sky realm (cloud islands) as a graph
 * of rooms: a branching tunnel tree plus a few extra loop connections, with
 * difficulty rising from the entry room out to a single boss room that holds
 * the unique legendary item and quest item for that realm.
 */
object SubRealmGenerator {

    private val OPPOSITE = mapOf(
        "north" to "south", "south" to "north",
        "east" to "west", "west" to "east",
        "up" to "down", "down" to "up",
    )
    private val DIRECTIONS = listOf("north", "south", "east", "west", "up", "down")

    private fun <T> pickUnique(pool: List<T>, used: MutableSet<T>, rng: Random): T {
        val shuffled = pool.shuffled(rng)
        val fresh = shuffled.firstOrNull { it !in used }
        val choice = fresh ?: shuffled.first()
        used.add(choice)
        return choice
    }

    private data class RoomGraph(
        val adjacency: List<MutableSet<Int>>,
        val depth: IntArray,
        val tier: IntArray,
        val bossIndex: Int,
    )

    private fun buildRoomGraph(rng: Random, roomCount: Int): RoomGraph {
        val parent = IntArray(roomCount) { -1 }
        val depth = IntArray(roomCount)
        val childCount = IntArray(roomCount)
        val maxChildren = 3
        val frontier = ArrayDeque<Int>()
        frontier.addLast(0)

        for (i in 1 until roomCount) {
            var p = frontier.random(rng)
            var attempts = 0
            while (childCount[p] >= maxChildren && attempts < 10) {
                p = frontier.random(rng)
                attempts++
            }
            if (childCount[p] >= maxChildren) {
                p = (0 until i).firstOrNull { childCount[it] < maxChildren } ?: (i - 1)
            }
            parent[i] = p
            depth[i] = depth[p] + 1
            childCount[p]++
            frontier.addLast(i)
            if (frontier.size > 5) frontier.removeFirst()
        }

        val adjacency = List(roomCount) { mutableSetOf<Int>() }
        for (i in 1 until roomCount) {
            adjacency[i].add(parent[i])
            adjacency[parent[i]].add(i)
        }

        val extraEdges = (roomCount / 6).coerceAtLeast(0)
        var added = 0
        var guard = 0
        while (added < extraEdges && guard < extraEdges * 25 + 20) {
            guard++
            val a = rng.nextInt(roomCount)
            val b = rng.nextInt(roomCount)
            if (a == b) continue
            if (adjacency[a].size >= 5 || adjacency[b].size >= 5) continue
            if (kotlin.math.abs(depth[a] - depth[b]) > 1) continue
            if (b in adjacency[a]) continue
            adjacency[a].add(b)
            adjacency[b].add(a)
            added++
        }

        val maxDepth = (depth.maxOrNull() ?: 1).coerceAtLeast(1)
        val tier = IntArray(roomCount) { i -> (1 + (depth[i] * 4.0 / maxDepth)).toInt().coerceIn(1, 5) }
        val bossIndex = depth.indices.filter { depth[it] == maxDepth }.maxOrNull() ?: (roomCount - 1)
        return RoomGraph(adjacency, depth, tier, bossIndex)
    }

    private fun assignExits(rng: Random, graph: RoomGraph, roomCount: Int): Array<LinkedHashMap<String, Int>> {
        val used = Array(roomCount) { mutableSetOf<String>() }
        val exits = Array(roomCount) { LinkedHashMap<String, Int>() }
        val seenEdges = mutableSetOf<Long>()

        fun edgeKey(a: Int, b: Int) = (minOf(a, b).toLong() shl 32) or maxOf(a, b).toLong()

        for (a in 0 until roomCount) {
            for (b in graph.adjacency[a]) {
                val key = edgeKey(a, b)
                if (key in seenEdges) continue
                seenEdges.add(key)
                val candidates = DIRECTIONS.shuffled(rng)
                var connected = false
                for (d in candidates) {
                    val od = OPPOSITE.getValue(d)
                    if (d !in used[a] && od !in used[b]) {
                        used[a].add(d); used[b].add(od)
                        exits[a][d] = b
                        exits[b][od] = a
                        connected = true
                        break
                    }
                }
                if (!connected) {
                    exits[a]["passage_to_${b}"] = b
                    exits[b]["passage_to_${a}"] = a
                }
            }
        }
        return exits
    }

    fun generate(
        kind: RealmKind,
        biome: Biome,
        theme: SubRealmTheme,
        entranceLocationId: String,
        worldSeed: Long,
        roomCountRange: IntRange,
        usedRealmNames: MutableSet<String>,
        usedBossNames: MutableSet<String>,
        usedLegendaryNames: MutableSet<String>,
        usedQuestItemNames: MutableSet<String>,
    ): SubRealm {
        val realmSeed = DeterministicRandom.seed(worldSeed, entranceLocationId.hashCode().toLong(), kind.ordinal.toLong())
        val rng = Random(realmSeed)

        val baseRealmName = pickUnique(theme.realmNames, mutableSetOf(), rng)
        val realmName = if (baseRealmName in usedRealmNames) "$baseRealmName above the ${biome.displayName}" else baseRealmName
        usedRealmNames.add(realmName)

        val bossCreatureName = pickUnique(theme.bossCreatures, usedBossNames, rng)

        val weaponOrArmorIsWeapon = rng.nextBoolean()
        val base = if (weaponOrArmorIsWeapon) theme.weaponBases.random(rng) else theme.armorBases.random(rng)
        var legendaryName = "${theme.itemPrefixes.random(rng)} $base"
        var guard = 0
        while (legendaryName in usedLegendaryNames && guard < 20) {
            legendaryName = "${theme.itemPrefixes.random(rng)} $base"
            guard++
        }
        usedLegendaryNames.add(legendaryName)

        val questItemName = pickUnique(theme.questItemNames, usedQuestItemNames, rng)

        val questType = QuestType.entries.toTypedArray().random(rng)
        val captiveName = theme.captiveNames.random(rng)

        val roomCount = roomCountRange.random(rng)
        val graph = buildRoomGraph(rng, roomCount)
        val exits = assignExits(rng, graph, roomCount)
        val bossTier = graph.tier[graph.bossIndex]

        val legendaryItem = if (weaponOrArmorIsWeapon)
            StatGenerator.weaponItem(legendaryName, bossTier, rng, legendary = true)
        else
            StatGenerator.armorItem(legendaryName, bossTier, rng, legendary = true)
        val questItem = StatGenerator.questItem(questItemName, bossTier, rng)

        val realmIdBase = "${kind.name.lowercase()}_$entranceLocationId"

        val rooms = LinkedHashMap<String, SubRealmRoom>()
        for (i in 0 until roomCount) {
            val roomRng = Random(DeterministicRandom.seed(realmSeed, i.toLong()))
            val isBoss = i == graph.bossIndex
            val adjective = theme.roomAdjectives.random(roomRng)
            val feature = theme.roomFeatures.random(roomRng)
            val name = if (isBoss) "$adjective $feature (${theme.label} Sanctum)" else "$adjective $feature"

            val beings = mutableListOf<SpawnEntry>()
            val items = mutableListOf<Item>()

            if (isBoss) {
                beings.add(SpawnEntry(bossCreatureName, SpawnKind.CREATURE, Disposition.HOSTILE, StatGenerator.creatureStats(graph.tier[i], roomRng)))
                items.add(legendaryItem)
                items.add(questItem)
                if (questType == QuestType.RESCUE_CAPTIVE) {
                    beings.add(SpawnEntry(captiveName, SpawnKind.NPC, Disposition.PASSIVE, StatGenerator.creatureStats(1, roomRng)))
                }
            } else {
                val pool = theme.creaturesFor(graph.tier[i])
                if (pool.isNotEmpty() && roomRng.nextInt(100) < 70) {
                    val t = pool.random(roomRng)
                    val groupSize = if (t.packSize.last > 1) t.packSize.random(roomRng) else 1
                    repeat(groupSize) {
                        beings.add(SpawnEntry(t.name, SpawnKind.CREATURE, t.disposition, StatGenerator.creatureStats(graph.tier[i], roomRng)))
                    }
                }
            }

            val description = if (isBoss)
                "You enter the heart of ${theme.label}: the $name. $bossCreatureName lurks here, guarding the ${theme.itemPrefixes.random(roomRng).lowercase()} treasures of this place."
            else
                "A ${adjective.lowercase()} $feature, deep within $realmName."

            val id = "${realmIdBase}_room$i"
            rooms[id] = SubRealmRoom(
                id = id,
                name = name,
                description = description,
                difficultyTier = graph.tier[i],
                isBossRoom = isBoss,
                beings = beings,
                items = items,
                exits = exits[i].mapValues { (_, roomIndex) -> "${realmIdBase}_room$roomIndex" },
            )
        }

        val objective = when (questType) {
            QuestType.RETRIEVE_ARTIFACT -> "Deep within $realmName lies the $questItemName. Recover it before it is lost to the dark forever."
            QuestType.DEFEAT_GUARDIAN -> "$bossCreatureName has claimed $realmName as its lair. Slay it to reclaim these depths."
            QuestType.RESCUE_CAPTIVE -> "$captiveName has been trapped within $realmName, guarded by $bossCreatureName. Brave the depths and bring them home."
        }

        val quest = SubRealmQuest(
            title = realmName,
            type = questType,
            objective = objective,
            questItem = questItem,
            legendaryItem = legendaryItem,
        )

        return SubRealm(
            id = realmIdBase,
            kind = kind,
            name = realmName,
            biome = biome,
            entranceLocationId = entranceLocationId,
            entryRoomId = "${realmIdBase}_room0",
            bossRoomId = "${realmIdBase}_room${graph.bossIndex}",
            rooms = rooms,
            quest = quest,
        )
    }
}
