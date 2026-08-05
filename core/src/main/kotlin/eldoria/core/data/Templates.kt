package eldoria.core.data

import eldoria.core.model.Biome
import eldoria.core.model.Disposition

/**
 * A kind of creature that can spawn in a biome within a tier range (1..5,
 * easy..hard). `packSize` defaults to solitary (1..1); pack/swarm-type
 * creatures override it (e.g. 2..4) so they spawn together as a group
 * instead of as lone individuals.
 */
data class CreatureTemplate(
    val name: String,
    val disposition: Disposition,
    val minTier: Int,
    val maxTier: Int,
    val packSize: IntRange = 1..1,
)

/** A kind of NPC (civilian or otherwise) that can appear in a biome within a tier range. */
data class NpcTemplate(
    val name: String,
    val disposition: Disposition,
    val minTier: Int,
    val maxTier: Int,
)

/** All the hardcoded flavor content for one biome: names, terrain words, and populations. */
data class BiomeContent(
    val biome: Biome,
    val adjectives: List<String>,
    val features: List<String>,
    val qualifiers: List<String>,
    val cityNames: List<String>,
    val villageNames: List<String>,
    val creatures: List<CreatureTemplate>,
    val npcs: List<NpcTemplate>,
) {
    fun creaturesFor(tier: Int) = creatures.filter { tier in it.minTier..it.maxTier }
    fun npcsFor(tier: Int) = npcs.filter { tier in it.minTier..it.maxTier }
}
