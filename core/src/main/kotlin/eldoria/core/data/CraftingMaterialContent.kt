package eldoria.core.data

import eldoria.core.model.Biome
import eldoria.core.model.SkillType

/** A gatherable crafting reagent, found in a specific biome, that feeds one trainer-locked crafting skill. */
data class MaterialTemplate(val name: String, val feedsSkill: SkillType)

/**
 * Where the raw materials for each crafting skill come from. Every
 * crafting SkillType has at least two biome sources so a player isn't
 * stuck if they've only explored one part of the world. Dropped by
 * defeating hostile creatures (see Game.kt combat) -- not sold in shops,
 * on purpose, so gathering stays tied to actually adventuring.
 */
object CraftingMaterialContentRegistry {
    private val byBiome: Map<Biome, List<MaterialTemplate>> = mapOf(
        Biome.MOUNTAINS to listOf(
            MaterialTemplate("Iron Ore", SkillType.BLACKSMITHING),
            MaterialTemplate("Raw Gemstone", SkillType.ENCHANTING),
        ),
        Biome.PLAINS to listOf(
            MaterialTemplate("Medicinal Herbs", SkillType.ALCHEMY),
            MaterialTemplate("Prime Hide", SkillType.LEATHERWORKING),
        ),
        Biome.DESERT to listOf(
            MaterialTemplate("Sun-cured Hide", SkillType.LEATHERWORKING),
            MaterialTemplate("Glass Sand", SkillType.ENCHANTING),
        ),
        Biome.JUNGLE to listOf(
            MaterialTemplate("Rare Jungle Herbs", SkillType.ALCHEMY),
            MaterialTemplate("Straight-Grain Wood", SkillType.WOODWORKING),
        ),
        Biome.TUNDRA to listOf(
            MaterialTemplate("Frost Ore", SkillType.BLACKSMITHING),
            MaterialTemplate("Thick Pelt", SkillType.LEATHERWORKING),
        ),
        Biome.SEA to listOf(
            MaterialTemplate("Kelp Extract", SkillType.ALCHEMY),
            MaterialTemplate("Driftwood", SkillType.WOODWORKING),
        ),
    )

    fun materialsFor(biome: Biome): List<MaterialTemplate> = byBiome.getValue(biome)

    val all: List<MaterialTemplate> = byBiome.values.flatten()
}
