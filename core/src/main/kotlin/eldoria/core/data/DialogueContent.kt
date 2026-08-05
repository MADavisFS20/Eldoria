package eldoria.core.data

import eldoria.core.model.Biome
import eldoria.core.model.QuestType
import kotlin.random.Random

/** Broad conversational role a passive civilian NPC falls into, inferred from their template name (see [DialogueContentRegistry.archetypeFor]). */
enum class NpcArchetype { TRADER, GUIDE, LABORER, HEALER, MYSTIC, ENTERTAINER, GENERIC }

/**
 * Hand-written dialogue banks so every NPC says something that actually
 * makes sense for who they are, without needing one bespoke line per
 * individual NPC (there are thousands of NPC instances across the world,
 * drawn from ~44 name templates). Trainers are the exception -- they're few
 * and unique, so they get bespoke lines directly on TrainerTemplate.
 *
 * Passive NPCs are classified into a small archetype by keyword match on
 * their template name, then given a varied, biome/location-aware line.
 * Hostile beings don't "converse" -- they get a threat/taunt line instead,
 * fitting an ambush rather than a chat.
 */
object DialogueContentRegistry {

    fun archetypeFor(npcName: String): NpcArchetype {
        val n = npcName.lowercase()
        return when {
            listOf("trader", "merchant", "keeper", "vendor").any { it in n } -> NpcArchetype.TRADER
            listOf("guide", "sled driver", "pilgrim").any { it in n } -> NpcArchetype.GUIDE
            listOf("miner", "farmer", "shepherd", "miller", "fisher", "trapper", "sailor", "crier").any { it in n } -> NpcArchetype.LABORER
            listOf("healer", "herbalist", "priestess", "medic").any { it in n } -> NpcArchetype.HEALER
            listOf("elder", "shaman", "mystic", "seer", "fortune teller", "cultist").any { it in n } -> NpcArchetype.MYSTIC
            listOf("bard", "crier").any { it in n } -> NpcArchetype.ENTERTAINER
            else -> NpcArchetype.GENERIC
        }
    }

    private val TRADER_LINES = listOf(
        "\"Best prices this side of {location}, I promise you that.\"",
        "\"Buying or selling? Either way, step out of the sun and let's talk.\"",
        "\"Careful on the roads out of {location} -- I lost a whole cart to bandits last month.\"",
    )
    private val GUIDE_LINES = listOf(
        "\"Lost? Half the travelers through {location} are, first time. I can point you right.\"",
        "\"I know every safe path out of {location} and a few of the unsafe ones too.\"",
        "\"Stick to the marked trails past {location} -- the wild parts of this {biome} don't forgive mistakes.\"",
    )
    private val LABORER_LINES = listOf(
        "\"Long day's work, but {location}'s got to eat same as anywhere.\"",
        "\"Not much news out here -- just the same work, day after day.\"",
        "\"You get used to the {biome}, after enough years. Mostly.\"",
    )
    private val HEALER_LINES = listOf(
        "\"You look a little worse for wear. Sit a moment, let me look you over.\"",
        "\"Plenty of folk come through {location} needing patching up. You're not the first.\"",
        "\"Rest when you can. This road doesn't forgive the reckless.\"",
    )
    private val MYSTIC_LINES = listOf(
        "\"The {biome} speaks, if you know how to listen. Most don't.\"",
        "\"I've seen a great many travelers pass through {location}. You've an odd look about you.\"",
        "\"Fate is a strange thread. Yours seems tangled with something big.\"",
        "\"I sense a family torn apart, long ago, by cowards in fine clothes. Perhaps that means something to you.\"",
    )
    private val ENTERTAINER_LINES = listOf(
        "\"Care to hear a tale of {location}? I've a few worth the telling.\"",
        "\"Every town's got a story. This one's got three, if you buy the next round.\"",
        "\"You've the look of someone about to become a story themselves.\"",
    )
    private val GENERIC_LINES = listOf(
        "\"Welcome to {location}, stranger. Mind yourself out there.\"",
        "\"Don't see many new faces around {location}.\"",
        "\"Quiet day here in the {biome}. Suits me fine.\"",
        "\"The King's law forbids what the nobles do to peasant families, but out here, who's left to enforce it?\"",
    )

    private val HOSTILE_LINES = listOf(
        "\"{name} snarls and levels a weapon at you -- there'll be no talking your way out of this.\"",
        "\"{name} bars your path with a cold, hungry look.\"",
        "\"{name} doesn't wait for words before closing the distance.\"",
    )

    private fun fill(template: String, location: String, biome: Biome, name: String = ""): String =
        template.replace("{location}", location).replace("{biome}", biome.displayName.lowercase()).replace("{name}", name)

    fun civilianLine(npcName: String, location: String, biome: Biome, rng: Random): String {
        val bank = when (archetypeFor(npcName)) {
            NpcArchetype.TRADER -> TRADER_LINES
            NpcArchetype.GUIDE -> GUIDE_LINES
            NpcArchetype.LABORER -> LABORER_LINES
            NpcArchetype.HEALER -> HEALER_LINES
            NpcArchetype.MYSTIC -> MYSTIC_LINES
            NpcArchetype.ENTERTAINER -> ENTERTAINER_LINES
            NpcArchetype.GENERIC -> GENERIC_LINES
        }
        return fill(bank.random(rng), location, biome)
    }

    fun hostileLine(beingName: String, rng: Random): String = fill(HOSTILE_LINES.random(rng), "", Biome.PLAINS, beingName)

    private val TELEPATHY_LINES = listOf(
        "they think you're hiding something, and they're not wrong to wonder.",
        "they're far more afraid of the road ahead than they're letting on.",
        "they resent someone in this town, though they'd never say who out loud.",
        "they don't trust you as far as they could throw you -- smart of them.",
        "there's a debt owed to them that's gone unpaid far too long.",
        "they're quietly grateful you didn't ask about the scar.",
        "they know something about the nobles they'd never risk saying aloud.",
    )

    /** Bonus "surface thought" flavor for the TELEPATH_DEVICE artifact -- see Game.kt's `talk`. */
    fun telepathyLine(rng: Random): String = TELEPATHY_LINES.random(rng)

    private val CAPTIVE_RESCUE_LINES = listOf(
        "\"{name}! You... you actually came. I'd nearly given up hope of seeing the sky again. Thank you.\"",
        "\"{name} sags with relief. \\\"I owe you my life. Get me out of here, please.\\\"\"",
        "\"{name} wipes their eyes and manages a shaky laugh. \\\"Every hero in the old stories showed up exactly this late. Let's go.\\\"\"",
    )
    private val BOSS_TAUNT_LINES = listOf(
        "\"{name} lets out a bone-deep roar. \\\"None who enter here leave again!\\\"\"",
        "\"{name} sizes you up and grins. \\\"Another fool come to die in my domain.\\\"\"",
        "\"{name} doesn't waste breath on words -- only on the attack that follows.\"",
    )

    fun captiveRescueLine(captiveName: String, rng: Random): String = CAPTIVE_RESCUE_LINES.random(rng).replace("{name}", captiveName)
    fun bossTauntLine(bossName: String, rng: Random): String = BOSS_TAUNT_LINES.random(rng).replace("{name}", bossName)

    fun questFlavorLine(type: QuestType, rng: Random): String = when (type) {
        QuestType.RETRIEVE_ARTIFACT -> listOf(
            "Faint runes along the wall warn that only the worthy may claim what lies ahead.",
            "Old bloodstains on the floor suggest you're not the first to come looking for it.",
        ).random(rng)
        QuestType.DEFEAT_GUARDIAN -> listOf(
            "The air grows heavier the deeper you go, thick with something ancient and territorial.",
            "Claw marks score the walls, each one deep enough to fit a finger.",
        ).random(rng)
        QuestType.RESCUE_CAPTIVE -> listOf(
            "A faint, ragged voice calls for help somewhere deeper in.",
            "Scraps of torn cloth mark a trail further into the dark.",
        ).random(rng)
    }
}
