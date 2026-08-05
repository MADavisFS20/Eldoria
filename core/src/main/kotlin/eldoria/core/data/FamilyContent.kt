package eldoria.core.data

/**
 * The game's main-quest premise: the player was taken from their family as
 * a child by the Kingdom of Eldoria's nobles -- in defiance of the king's
 * own law -- so they'd never grow strong enough to threaten the nobles'
 * standing. Now an adult, the player searches the kingdom for their family,
 * and the story pays off once every quest in the world is done: see
 * Game.kt's `checkEndgameTrigger`/`finalBattle` for the reunion + the final
 * battle against the three nobles responsible.
 *
 * One relation is picked deterministically per world seed (WorldGenerator)
 * and placed as a single findable NPC in one countryside village somewhere
 * in the world -- the same relation and NPC every time a given seed is
 * regenerated, per the engine's determinism rule. The other three are
 * revealed, already safe and waiting, in the endgame reunion scene rather
 * than placed as separate walkable NPCs.
 */
object FamilyContentRegistry {
    data class FamilyRelation(val relation: String, val name: String)
    data class Noble(val title: String, val name: String)

    val candidates: List<FamilyRelation> = listOf(
        FamilyRelation("mother", "Elara"),
        FamilyRelation("father", "Bran"),
        FamilyRelation("sister", "Wren"),
        FamilyRelation("brother", "Toma"),
    )

    val reunionLines: List<String> = listOf(
        "\"{name} freezes, then drops what they're holding. \\\"...it's you. After all these years, it's really you.\\\"\"",
        "\"{name}'s eyes fill with tears. \\\"I never stopped looking. I never stopped hoping. Come here.\\\"\"",
        "\"{name} pulls you into an embrace before you've said a single word. \\\"The nobles took you from us, but they couldn't take this.\\\"\"",
    )

    /** The three nobles responsible for the theft, fought in order of ascending menace in the final battle. */
    val nobles: List<Noble> = listOf(
        Noble("Mistress of Whispers", "Lady Seraphine Vex"),
        Noble("Warden of the Silent Decree", "Lord Malvorn Ashgrave"),
        Noble("the Iron Regent", "Duke Corvin Blackthorne"),
    )

    val grandReunionScene: String = """
        |Word reaches you before you've even had time to catch your breath from the last battle: a caravan,
        |quiet and unannounced, has arrived. And there, stepping down from it, are the faces you gave up
        |hoping to see -- your mother, your father, your sister, all of them, drawn by whispers that a child
        |stolen long ago had returned to fight for a kingdom that once turned its back on them.
        |
        |You are not looking for your family anymore. For the first time since you were a child, your family
        |is looking at you, and none of you can say a word.
    """.trimMargin()

    val throneCallToAction: String = """
        |But reunion is not the end of it. The nobles who tore your family apart still sit comfortably above
        |the law they broke -- Lady Seraphine Vex, Lord Malvorn Ashgrave, and Duke Corvin Blackthorne, the
        |Iron Regent himself. Every quest you have completed, every monster you've put down, has been a
        |step toward this. Your family did not come to say goodbye. They came to watch you finish it.
        |
        |Type 'confront' when you are ready to march on the throne room.
    """.trimMargin()

    /** Flavor for each noble going down in the sequential final fight -- normal combat, not the scripted finish. */
    val nobleFallLines: List<String> = listOf(
        "\"{name} staggers, crown of authority slipping from a face that never once looked at a peasant with pity.\"",
        "\"{name} collapses, the last of their borrowed power draining out with the blood.\"",
        "\"{name} falls to their knees. \\\"This throne was never meant to answer to the likes of you--\\\" It's the last thing they say.\"",
    )

    /**
     * The scripted, automatic finishing blow on the third and final noble --
     * NOT a normal dice-rolled attack. Deliberately the one moment in the
     * game that isn't resolved by CombatMath, because it isn't meant to be
     * a roll: it's the payoff of the whole story.
     */
    val finalStrikeLines: List<String> = listOf(
        """
        |Something rises in you that no trainer ever taught and no dungeon ever tested -- not strength, not
        |steel, not a spell drilled into memory, but something that was simply always there, waiting. It
        |floods up through you like a held breath finally released, and without a single conscious thought
        |you move, and light that answers to no school of magic you have ever learned pours out of you and
        |through {name}, and the Iron Regent's reign ends between one heartbeat and the next.
        """.trimMargin(),
        """
        |You don't decide to strike. Your body simply remembers something your mind never learned -- a warmth
        |welling up from somewhere under the ribs, old as a mother's arms, old as a father's hands, old as a
        |sister's laugh -- and it becomes light, and the light becomes a blow that {name} never sees coming
        |and never survives.
        """.trimMargin(),
    )

    val victoryEpilogue: String = """
        |The throne room falls silent. You stand over the last of the three nobles who broke the king's own
        |law to steal children from their families, and you feel -- not triumph, not even relief, but
        |something quieter. That strike didn't come from any skill you trained or any weapon you carried.
        |It came from the same place your family had been all along: not lost, not waiting to be found in
        |some far village, but carried with you the entire time, in your heart, in every step of this
        |journey, whether you knew it or not.
        |
        |You had been searching the whole kingdom for something that never once left you.
        |
        |=== THE END ===
    """.trimMargin()
}
