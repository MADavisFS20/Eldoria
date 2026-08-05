package eldoria.core.game

import eldoria.core.model.GameLocation
import eldoria.core.model.Item
import eldoria.core.model.PlayerCharacter
import eldoria.core.model.SpawnEntry
import eldoria.core.model.SubRealm
import eldoria.core.model.SubRealmRoom
import eldoria.core.model.World
import kotlin.random.Random
import kotlinx.serialization.Serializable

/** Where the player is standing inside a sub-realm (dungeon/sky realm), if they're in one. */
data class SubRealmPosition(val subRealmId: String, val roomId: String)

/**
 * All the mutable runtime state a play session needs on top of the
 * immutable generated World: where the player is, what they've discovered
 * (for the fog-of-war map and bestiary), what's been defeated/looted, and
 * quest tracking. The World and PlayerCharacter models stay
 * immutable/generation-pure; this class is the one place session state is
 * allowed to live.
 *
 * Respawn rule (explicit user spec): a defeated being does NOT come back
 * just because time passes while you're standing there grinding -- it only
 * becomes eligible again once you've *left* its spot and a fair amount of
 * game time has passed since that departure. "Spot" for the overworld is
 * the single tile; for a dungeon/sky realm it's the *whole sub-realm* --
 * moving room to room inside one doesn't count as leaving it.
 */
class GameSession(
    val world: World,
    var player: PlayerCharacter,
    var locationId: String,
    val homeLocationId: String,
    val rng: Random,
) {
    companion object {
        const val RESPAWN_DELAY_TICKS = 40
    }

    var gameTick: Int = 0
        private set

    val discoveredLocations: MutableSet<String> = mutableSetOf(locationId)
    var subRealmPosition: SubRealmPosition? = null

    /** spotKey -> (being index in its static list) -> tick it was defeated at. */
    private val defeatedAt: MutableMap<String, MutableMap<Int, Int>> = mutableMapOf()

    /** spotKey -> tick the player most recently departed it (overworld: left the tile; sub-realm: exited the whole realm). */
    private val departedAt: MutableMap<String, Int> = mutableMapOf()

    private val takenItems: MutableMap<String, MutableSet<String>> = mutableMapOf()

    val discoveredQuests: MutableSet<String> = mutableSetOf()
    val completedQuests: MutableSet<String> = mutableSetOf()
    val bestiary: MutableSet<String> = mutableSetOf()

    /** Side quests (model/SideQuest.kt) resolved so far, by SideQuestKind.name -- each can only be resolved once. */
    val completedSideQuests: MutableSet<String> = mutableSetOf()

    /** Set once every sub-realm quest + the main family quest are complete -- see Game.kt's checkEndgameTrigger. */
    var finalBattleUnlocked: Boolean = false
    var finalBattleWon: Boolean = false

    /** Set by a random riverside/coastal encounter (Game.kt's maybeFerryEncounter); consumed by the 'ferry' command. */
    var ferrymanAvailable: Boolean = false

    /** Set by a random countryside encounter (Game.kt's maybeBalloonEncounter); consumed by the 'ride' command. */
    var balloonManAvailable: Boolean = false

    val currentLocation: GameLocation get() = world.locations.getValue(locationId)
    val inSubRealm: Boolean get() = subRealmPosition != null

    fun currentSubRealm(): SubRealm? = subRealmPosition?.let { world.subRealms[it.subRealmId] }
    fun currentRoom(): SubRealmRoom? = subRealmPosition?.let { pos -> world.subRealms[pos.subRealmId]?.rooms?.get(pos.roomId) }

    private fun spotKey(): String = currentRoom()?.id ?: locationId

    fun advanceTick() {
        gameTick++
    }

    /** Call right before changing locationId on the overworld (each spot's own respawn clock). */
    fun recordOverworldDeparture(oldLocationId: String) {
        departedAt[oldLocationId] = gameTick
    }

    /** Call when fully exiting a sub-realm back to the overworld -- resets the clock for every room in it at once. */
    fun recordSubRealmDeparture(subRealm: SubRealm) {
        for (roomId in subRealm.rooms.keys) departedAt[roomId] = gameTick
    }

    private fun isRespawnEligible(spot: String, beingIndex: Int): Boolean {
        val deathTick = defeatedAt[spot]?.get(beingIndex) ?: return true
        val departed = departedAt[spot] ?: return false
        return departed > deathTick && gameTick - departed >= RESPAWN_DELAY_TICKS
    }

    /** Living beings at the current spot, indexed exactly like the static list (index is the stable identity used by attack/defeat/talk). */
    fun currentBeings(): List<IndexedValue<SpawnEntry>> {
        val all = currentRoom()?.beings ?: currentLocation.beings
        val spot = spotKey()
        return all.withIndex().filter { (i, _) -> isRespawnEligible(spot, i) }
    }

    fun currentItems(): List<Item> {
        val itemsHere = currentRoom()?.items ?: currentLocation.items
        val gone = takenItems[spotKey()].orEmpty()
        return itemsHere.filterNot { it.name in gone }
    }

    fun markDefeated(beingIndex: Int, beingName: String) {
        defeatedAt.getOrPut(spotKey()) { mutableMapOf() }[beingIndex] = gameTick
        bestiary.add(beingName)
    }

    fun recordSeen(beingName: String) {
        bestiary.add(beingName)
    }

    fun markTaken(itemName: String) {
        takenItems.getOrPut(spotKey()) { mutableSetOf() }.add(itemName)
    }

    fun discover(id: String) {
        discoveredLocations.add(id)
    }

    /**
     * A flattened, disk-safe copy of every field save/load needs (see
     * world/SaveManager.kt). Deliberately does NOT include the World itself
     * (11,700+ generated locations) -- it's fully reproducible from `seed`,
     * so only the seed is saved, and the same in-memory World is reused for
     * an in-process death-reload (no need to regenerate at all in that case).
     */
    @Serializable
    data class Snapshot(
        val seed: Long,
        val player: PlayerCharacter,
        val locationId: String,
        val homeLocationId: String,
        val subRealmId: String?,
        val subRealmRoomId: String?,
        val gameTick: Int,
        val discoveredLocations: Set<String>,
        val defeatedAt: Map<String, Map<Int, Int>>,
        val departedAt: Map<String, Int>,
        val takenItems: Map<String, Set<String>>,
        val discoveredQuests: Set<String>,
        val completedQuests: Set<String>,
        val bestiary: Set<String>,
        val finalBattleUnlocked: Boolean,
        val finalBattleWon: Boolean,
        val completedSideQuests: Set<String>,
    )

    fun snapshot(): Snapshot = Snapshot(
        seed = world.seed,
        player = player,
        locationId = locationId,
        homeLocationId = homeLocationId,
        subRealmId = subRealmPosition?.subRealmId,
        subRealmRoomId = subRealmPosition?.roomId,
        gameTick = gameTick,
        discoveredLocations = discoveredLocations.toSet(),
        defeatedAt = defeatedAt.mapValues { it.value.toMap() },
        departedAt = departedAt.toMap(),
        takenItems = takenItems.mapValues { it.value.toSet() },
        discoveredQuests = discoveredQuests.toSet(),
        completedQuests = completedQuests.toSet(),
        bestiary = bestiary.toSet(),
        finalBattleUnlocked = finalBattleUnlocked,
        finalBattleWon = finalBattleWon,
        completedSideQuests = completedSideQuests.toSet(),
    )

    /** Restores every field in place from a snapshot taken against this same World (seed must match). */
    fun restoreFrom(snap: Snapshot) {
        require(snap.seed == world.seed) { "Save is for a different world seed" }
        player = snap.player
        locationId = snap.locationId
        subRealmPosition = if (snap.subRealmId != null && snap.subRealmRoomId != null) SubRealmPosition(snap.subRealmId, snap.subRealmRoomId) else null
        gameTick = snap.gameTick
        discoveredLocations.clear(); discoveredLocations.addAll(snap.discoveredLocations)
        defeatedAt.clear(); snap.defeatedAt.forEach { (k, v) -> defeatedAt[k] = v.toMutableMap() }
        departedAt.clear(); departedAt.putAll(snap.departedAt)
        takenItems.clear(); snap.takenItems.forEach { (k, v) -> takenItems[k] = v.toMutableSet() }
        discoveredQuests.clear(); discoveredQuests.addAll(snap.discoveredQuests)
        completedQuests.clear(); completedQuests.addAll(snap.completedQuests)
        bestiary.clear(); bestiary.addAll(snap.bestiary)
        finalBattleUnlocked = snap.finalBattleUnlocked
        finalBattleWon = snap.finalBattleWon
        completedSideQuests.clear(); completedSideQuests.addAll(snap.completedSideQuests)
    }
}
