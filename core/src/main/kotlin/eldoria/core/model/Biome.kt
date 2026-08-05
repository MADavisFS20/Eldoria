package eldoria.core.model

/**
 * The six main environments the world map is divided into. Order here also
 * defines their left-to-right band order in the generated map.
 */
enum class Biome(val displayName: String) {
    MOUNTAINS("Mountains"),
    PLAINS("Plains"),
    DESERT("Desert"),
    JUNGLE("Jungle"),
    TUNDRA("Tundra"),
    SEA("Sea"),
}

enum class PopulationTier {
    WILDERNESS,
    COUNTRYSIDE,
    CITY,
}

enum class Disposition {
    HOSTILE,
    PASSIVE,
}

enum class SpawnKind {
    CREATURE,
    NPC,
}
