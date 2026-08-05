package eldoria.core.model

/**
 * LAND is normal walkable ground. WATERWAY is open river/sea -- impassable
 * on foot, crossable only with a working boat. BRIDGE is a WATERWAY tile
 * that's always crossable on foot, so rivers cut through the map without
 * fully cutting it off.
 */
enum class TerrainKind { LAND, WATERWAY, BRIDGE }

/** A living being present at a location: a creature or an NPC, hostile or passive. */
data class SpawnEntry(
    val name: String,
    val kind: SpawnKind,
    val disposition: Disposition,
    val stats: StatBlock,
    /** Set when this NPC is a skill trainer: the one trainer-locked skill they can teach a player. */
    val teachesSkill: SkillType? = null,
    /** Set on the one NPC in the whole world who is the player's long-lost family -- see Game.kt's main quest. */
    val isFamilyMember: Boolean = false,
    /** Set on the one Vampire and one Werewolf NPC in the world -- each can grant their (mutually exclusive) curse once requested. */
    val offersSubclass: Subclass? = null,
    /** Set on the one Mad Scientist NPC in the world's most advanced city -- see Game.kt's bionic upgrade. */
    val offersBionicUpgrade: Boolean = false,
    /** Set on one civilian NPC per city -- can be hired as a companion, see Game.kt's `hire`. */
    val offersCompanionship: Boolean = false,
    /** Set on one civilian NPC per city -- a small side quest, see model/SideQuest.kt and Game.kt's `resolve`. */
    val offersSideQuest: SideQuestKind? = null,
)

/**
 * One tile of the world map. Every one of the 10,000+ map cells is a
 * GameLocation. Cities and countryside are named, populated settlements;
 * everything else is wilderness.
 */
data class GameLocation(
    val id: String,
    val x: Int,
    val y: Int,
    val biome: Biome,
    val name: String,
    val description: String,
    val populationTier: PopulationTier,
    /** 1 (easiest) .. 5 (hardest), gradient runs easy-to-hard across each biome. */
    val difficultyTier: Int,
    /** Fine-grained 1..100 difficulty score the tier is derived from. */
    val difficultyScore: Int,
    val beings: List<SpawnEntry>,
    /** direction ("north","south","east","west") -> destination location id */
    val exits: Map<String, String>,
    /** Set when this tile is a dungeon mouth or beanstalk: id into World.subRealms. */
    val portalId: String? = null,
    val portalKind: RealmKind? = null,
    val terrain: TerrainKind = TerrainKind.LAND,
    /** Loose items lying on this overworld tile -- currently just the 3 sunken-treasure side quest markers, see WorldGenerator. */
    val items: List<Item> = emptyList(),
    /** A natural danger native to this tile's biome (quicksand, a cliff edge, a riptide...) -- see model/Hazard.kt. */
    val hazard: HazardKind? = null,
) {
    val creatures: List<SpawnEntry> get() = beings.filter { it.kind == SpawnKind.CREATURE }
    val npcs: List<SpawnEntry> get() = beings.filter { it.kind == SpawnKind.NPC }
}

data class World(
    val width: Int,
    val height: Int,
    val seed: Long,
    val locations: Map<String, GameLocation>,
    val subRealms: Map<String, SubRealm> = emptyMap(),
) {
    fun locationAt(x: Int, y: Int): GameLocation? = locations["${x}_${y}"]
}
