package eldoria.core.data

import eldoria.core.model.Biome
import eldoria.core.model.SkillType

/**
 * A named NPC found in a specific city who can teach one trainer-locked
 * skill. `greeting` is what they say when spoken to; `teachOffer` is what
 * they say when they offer to actually train the player in `skill`.
 */
data class TrainerTemplate(val name: String, val skill: SkillType, val greeting: String, val teachOffer: String)

/**
 * Where to find a teacher for every magic school and crafting skill. Exactly
 * `WorldConfig.citiesPerBiome` (2) trainers per biome -- list size is
 * load-bearing, WorldGenerator places trainer[i] in city[i] of that biome.
 * Every trainer-locked SkillType appears at least once across all 6 biomes
 * (Blacksmithing and Restoration appear twice, for redundancy); nothing is
 * unreachable.
 */
object SkillTrainerContentRegistry {
    private val trainersByBiome: Map<Biome, List<TrainerTemplate>> = mapOf(
        Biome.MOUNTAINS to listOf(
            TrainerTemplate(
                "Borin Ironfist, Dwarven Master Smith", SkillType.BLACKSMITHING,
                greeting = "Borin Ironfist wipes soot from his brow and eyes your gear with a critical squint.",
                teachOffer = "\"That blade's a disgrace. Stay a while and I'll teach you to swing a hammer proper -- Blacksmithing's no mystery, just fire, iron, and patience.\"",
            ),
            TrainerTemplate(
                "Old Thrun, Runic Mystic", SkillType.ENCHANTING,
                greeting = "Old Thrun traces a glowing rune in the air, watching it fade before it touches the ground.",
                teachOffer = "\"Every blade and ring can hold a whisper of magic, if you know how to bind it. I can show you the runes, if you've the patience for Enchanting.\"",
            ),
        ),
        Biome.PLAINS to listOf(
            TrainerTemplate(
                "Sister Wren, Temple Healer", SkillType.RESTORATION,
                greeting = "Sister Wren looks up from bandaging a farmhand's arm and offers you a tired, kind smile.",
                teachOffer = "\"The light doesn't just heal wounds, child -- it mends what fear and steel break. Let me teach you Restoration, and you'll never stand helpless over a dying friend.\"",
            ),
            TrainerTemplate(
                "Mother Fallow, Herbwife", SkillType.ALCHEMY,
                greeting = "Mother Fallow is elbow-deep in a basket of roots and dried petals, muttering names of plants under her breath.",
                teachOffer = "\"Half of what grows in these fields will cure you, and the other half will kill you -- the trick is knowing which. Learn Alchemy from me and you'll never guess wrong again.\"",
            ),
        ),
        Biome.DESERT to listOf(
            TrainerTemplate(
                "Zahra the Bright, Sunfire Mystic", SkillType.DESTRUCTION,
                greeting = "Zahra the Bright watches a small flame dance across her open palm without ever touching her skin.",
                teachOffer = "\"Fire, frost, lightning -- the desert taught me to command all three. Study Destruction under me, and your enemies will learn to fear your shadow.\"",
            ),
            TrainerTemplate(
                "Kesh Veyra, Mirage Seer", SkillType.ILLUSION,
                greeting = "Kesh Veyra's outline shimmers faintly in the heat, and you can't quite tell if that's the desert air or her doing.",
                teachOffer = "\"What the eye believes, the sword obeys. Let me teach you Illusion, and you'll win fights your enemy never even knew they were in.\"",
            ),
        ),
        Biome.JUNGLE to listOf(
            TrainerTemplate(
                "Itzel the Bound, Spirit Caller", SkillType.CONJURATION,
                greeting = "Itzel the Bound murmurs to something unseen just past your shoulder, then turns to greet you properly.",
                teachOffer = "\"The spirits of this jungle will fight at your side, if you learn to ask them right. I can teach you Conjuration, if you're not afraid of what answers.\"",
            ),
            TrainerTemplate(
                "Old Kael, Bowyer", SkillType.WOODWORKING,
                greeting = "Old Kael turns a half-finished bow stave over in his hands, checking the grain against the light.",
                teachOffer = "\"Any fool can whittle a stick. Learn Woodworking from me and you'll be carving bows and arrows worth carrying into a real fight.\"",
            ),
        ),
        Biome.TUNDRA to listOf(
            TrainerTemplate(
                "Vigdis Coldhand, Frostshaper", SkillType.ALTERATION,
                greeting = "Vigdis Coldhand rests a bare hand on the ice wall beside her, and frost creeps outward from her fingertips.",
                teachOffer = "\"Stone, ice, even flesh -- the shape of a thing is only ever a suggestion. Let me teach you Alteration, and you'll learn to bend the rules the world thinks are fixed.\"",
            ),
            TrainerTemplate(
                "Ragnar, Master Smith of the North", SkillType.BLACKSMITHING,
                greeting = "Ragnar's hammer rings against the anvil in a steady rhythm that doesn't break as he glances your way.",
                teachOffer = "\"Southern steel is soft. Learn Blacksmithing from a northerner and you'll forge gear that laughs at the cold.\"",
            ),
        ),
        Biome.SEA to listOf(
            TrainerTemplate(
                "Old Barnabus, Sailmaker", SkillType.LEATHERWORKING,
                greeting = "Old Barnabus sits cross-legged on the dock, a needle flashing through a stretch of tanned hide.",
                teachOffer = "\"Sailcloth, boots, a good jerkin -- it's all the same skill, just different leather. Let me teach you Leatherworking and you'll never buy shoddy gear again.\"",
            ),
            TrainerTemplate(
                "Priestess Marin of the Tide", SkillType.RESTORATION,
                greeting = "Priestess Marin stands at the tideline with her eyes closed, murmuring a prayer timed to the waves.",
                teachOffer = "\"The sea gives and the sea takes, but a healer's hands can hold the balance. Let me teach you Restoration, in the old tidewater way.\"",
            ),
        ),
    )

    /** The trainer placed in the `cityIndex`-th city of `biome` (0-based, matches WorldGenerator's city ordering). */
    fun trainerFor(biome: Biome, cityIndex: Int): TrainerTemplate? =
        trainersByBiome[biome]?.getOrNull(cityIndex)

    val all: List<TrainerTemplate> = trainersByBiome.values.flatten()
}
