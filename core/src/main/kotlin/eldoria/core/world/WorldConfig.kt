package eldoria.core.world

/**
 * width * height must be >= 10,000. Default 130x90 = 11,700 map tiles,
 * split into 6 vertical biome bands (~1,950 tiles each).
 */
data class WorldConfig(
    val width: Int = 130,
    val height: Int = 90,
    val seed: Long = 1337L,
    val citiesPerBiome: Int = 2,
    val villagesPerCity: Int = 4,
    val dungeonsPerBiome: Int = 3,
    val dungeonRoomCountRange: IntRange = 12..20,
    val beanstalksPerBiome: Int = 2,
    val skyRoomCountRange: IntRange = 10..18,
    /** Rivers cutting west-to-east through the 5 land biomes -- impassable on foot except at bridges. */
    val riverCount: Int = 3,
    /** Roughly 1 bridge every this-many tiles along a river's length. */
    val bridgeSpacing: Int = 10,
)
