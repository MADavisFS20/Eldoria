package eldoria.core.model

/**
 * One resolution path for a SideQuestKind, triggered by `resolve <keyword>`.
 * Every resolution pays out *something* real (gold and/or reputation, a few
 * pay a material too) -- no side quest in the game is reward-free.
 */
data class SideQuestResolution(
    val keyword: String,
    val label: String,
    val outcomeLine: String,
    val reputationDelta: Int,
    val goldDelta: Int,
    val materialReward: String? = null,
)

/**
 * 34 small, self-contained side quests -- one NPC, a punchy hook line, and
 * one or two resolution paths, each with a real payout. Deliberately
 * breadth over depth: this is 34 flavorful moments, not 34 branching
 * questlines, distributed across all 12 cities (see WorldGenerator). Half
 * are drawn from classic RPG side-quest tropes, half lean into mature
 * themes (crime, addiction, grief, corruption, war) in the Witcher
 * 3/Skyrim/Fallout register -- no explicit content, ever.
 */
enum class SideQuestKind(
    val title: String,
    val giverFlavor: String,
    val hookLine: String,
    val resolutions: List<SideQuestResolution>,
) {
    PETRIFIED_THIEF(
        "The Statue That Isn't",
        "a wide-grinning curiosities merchant",
        "\"Genuine petrified art, direct from a cockatrice's lair!\" the merchant says, gesturing at a suspiciously lifelike, suspiciously human-shaped statue in the corner. You'd swear it just twitched.",
        listOf(SideQuestResolution(
            "free", "Buy the statue and break the curse (25g)",
            "You pay, touch the statue, and it gasps back to life -- a thief the merchant had been fencing as \"art\" for months. Grateful and light-fingered, they slip something into your pocket before bolting.",
            reputationDelta = 8, goldDelta = -25, materialReward = "Stolen Trinket",
        )),
    ),
    UNDERGROUND_DICE_DEN(
        "High Stakes",
        "a gravel-voiced gambler in a back room",
        "Dice clatter across a stained table. \"House rules: you match my wager, we roll, high number wins double.\" A crowd's already forming to watch you lose your shirt.",
        listOf(SideQuestResolution(
            "gamble", "Wager 20g on a single d20 roll, double or nothing",
            "The die skitters, spins, and drops. Whatever it shows, the crowd roars either way -- this table's seen bigger swings than yours.",
            reputationDelta = 0, goldDelta = 40, // net effect modeled as a straight payout for simplicity; framed as a win
        )),
    ),
    RIVAL_TREASURE_HUNTER(
        "Race You There",
        "a smug treasure hunter sizing up your gear",
        "\"You look like the dungeon-diving sort,\" they say, tapping a rolled-up map. \"Word is there's a legendary find nearby. Race you to it -- winner keeps the bragging rights, and I hear the winner usually eats better too.\"",
        listOf(SideQuestResolution(
            "race", "Accept the bragging-rights wager",
            "You shake on it. Whether or not you ever cross paths with them again, word gets around that you don't back down from a challenge -- and they toss over a good-luck coin purse before you go.",
            reputationDelta = 5, goldDelta = 30,
        )),
    ),
    STRANGE_BREW_HERMIT(
        "A Taste of Something Else",
        "a wild-eyed hermit stirring a smoking pot",
        "\"Drink this,\" the hermit says, thrusting a bubbling cup at you, \"and the world gets a little louder, a little stranger, for a good long while.\" It smells like lightning and old moss.",
        listOf(SideQuestResolution(
            "drink", "Drink the strange brew",
            "The world tilts, colors hum, and for one dizzy moment you swear a passing bird wished you good luck. The hermit cackles and presses a small pouch of coin into your hand \"for science.\"",
            reputationDelta = 2, goldDelta = 15,
        )),
    ),
    RIDDLE_KEEPER(
        "The Riddle at the Gate",
        "an old riddle-keeper who blocks the good gossip behind a puzzle",
        "\"Answer me this, traveler: I have cities, but no houses; forests, but no trees; rivers, but no water. What am I?\" (type 'resolve map' if you know it)",
        listOf(SideQuestResolution(
            "map", "Answer: a map",
            "\"Sharp one, aren't you!\" the riddle-keeper laughs, delighted, and presses a fat coin purse into your hands. \"Been years since anyone got that on the first try.\"",
            reputationDelta = 6, goldDelta = 45,
        )),
    ),
    TWO_SUITORS(
        "A Matter of the Heart",
        "a nervous villager who can't choose between two suitors",
        "\"I need someone impartial,\" they whisper. \"There's two who'd have my hand, and I can't pick without breaking a heart. Would you... decide for me?\"",
        listOf(
            SideQuestResolution(
                "steady", "Push them toward the steady, reliable suitor",
                "You make the case for stability, and they nod slowly, relieved to have the weight lifted. A quiet wedding follows, and a grateful gift arrives at your door.",
                reputationDelta = 6, goldDelta = 20,
            ),
            SideQuestResolution(
                "wild", "Push them toward the wild, passionate suitor",
                "You make the case for following the heart over the head, and they laugh -- really laugh -- for the first time in the conversation. They insist you take something for the nerve of it.",
                reputationDelta = 4, goldDelta = 20,
            ),
        ),
    ),
    SKULL_AND_RUIN(
        "The Skull Collector",
        "a temple curator obsessed with cursed relics",
        "\"Bring me something with a little death in it,\" the curator says, eyes gleaming, \"a skull, a shard, anything that still remembers being alive -- and I'll pay well over its weight in gold.\"",
        listOf(SideQuestResolution(
            "sell", "Hand over a grim curiosity from your travels",
            "The curator's hands shake with excitement as they turn the thing over, murmuring appraisals only they understand, and pay out without haggling once.",
            reputationDelta = 3, goldDelta = 55,
        )),
    ),
    RAIDERS_OR_CAPTIVES(
        "Which Side of the Cage",
        "a village elder, afraid of the wrong people",
        "\"Raiders took the old mill,\" the elder says, wringing their hands, \"but... something's strange. The folk they're holding aren't screaming to be freed. I don't understand it, and I'm afraid to ask why.\"",
        listOf(
            SideQuestResolution(
                "raiders", "Side with the village, drive off the raiders",
                "You clear the mill by force, and the village breathes easy again -- whatever the \"captives\" were hiding from, it's not your problem to untangle today. The elder pays your fee gladly.",
                reputationDelta = 10, goldDelta = 40,
            ),
            SideQuestResolution(
                "captives", "Investigate first -- the captives were hiding from something worse",
                "The truth is uglier than raiders: those \"captives\" were fleeing a debt collector who'd have sold them off entirely. You help them vanish instead, and they leave you what little they have left.",
                reputationDelta = 15, goldDelta = 15,
            ),
        ),
    ),
    BOUNTY_BOARD(
        "Posted Bounty",
        "a battered wooden board nailed outside the guard post",
        "A fresh notice, ink still tacky: coin on the head of something dangerous prowling the wilds nearby, no questions asked about the state it comes back in.",
        listOf(SideQuestResolution(
            "hunt", "Take the bounty and hunt the wilds for trouble",
            "You go looking for a fight and, this being the Kingdom's countryside, you don't have to look long. You return blood-spattered and owed -- the guards pay out without counting twice.",
            reputationDelta = 5, goldDelta = 50,
        )),
    ),
    SMUGGLERS_CARGO(
        "Cargo of Convenient Silence",
        "a nervous dockhand who won't meet your eyes",
        "\"There's a shipment coming in tonight that isn't on any manifest,\" they mutter. \"I could use a hand making sure it disappears quiet-like. Or... if you'd rather, I could use a hand making sure it doesn't disappear at all.\"",
        listOf(
            SideQuestResolution(
                "smuggle", "Help move the cargo quietly, no questions asked",
                "It's done before dawn, no names exchanged, no questions answered. Whatever was in those crates, it's someone else's problem now -- and your cut is real coin.",
                reputationDelta = -5, goldDelta = 60,
            ),
            SideQuestResolution(
                "report", "Report the smuggling to the harbor authorities instead",
                "The dockhand pales as the harbor guard descends, but the authorities are grateful for the tip -- and quietly generous, since a smuggling ring just lost a whole shipment on your say-so.",
                reputationDelta = 12, goldDelta = 30,
            ),
        ),
    ),
    UNDERGROUND_ARENA(
        "The Pit",
        "a scarred pit boss looking you up and down",
        "\"Three fights, back to back, no rest between,\" the pit boss says, cracking their knuckles. \"Win all three and the purse is yours. Lose, and you walk out poorer and sorer. Well?\"",
        listOf(SideQuestResolution(
            "fight", "Enter the pit and fight the gauntlet",
            "Three brutal, breathless bouts later, the crowd's on its feet and the pit boss is counting coin into your hand, visibly annoyed at how much of it that is.",
            reputationDelta = 10, goldDelta = 75,
        )),
    ),
    WAR_PROFITEER(
        "Blood Money",
        "a well-dressed arms dealer with too clean a conscience",
        "You catch the dealer's ledger by accident -- weapons sold to a village's militia, and the exact same weapons sold to the raiders burning that village down. They notice you noticing.",
        listOf(
            SideQuestResolution(
                "expose", "Expose the dealer publicly",
                "The city guard drags the dealer off in chains within the hour, and the militia's relieved captain presses a reward into your hands, genuinely grateful someone finally caught them.",
                reputationDelta = 15, goldDelta = 35,
            ),
            SideQuestResolution(
                "cut", "Take a cut to keep quiet",
                "The dealer pays well for silence, sliding a heavy purse across the table without a word. You pocket it. Somewhere out there, that village is still burning either way.",
                reputationDelta = -12, goldDelta = 80,
            ),
        ),
    ),
    THE_HABIT(
        "A Habit Worth Breaking",
        "a once-noble figure, hands shaking, eyes hollow",
        "They used to be somebody in this city. Now they're begging in an alley for coin toward \"medicine\" that's clearly anything but. \"Just enough to take the edge off,\" they plead. \"That's all I need.\"",
        listOf(
            SideQuestResolution(
                "help", "Pay for a healer to help them get clean instead",
                "It's a hard week for them, and a harder one for you watching it, but they come out the other side with clear eyes for the first time in years. Their family, tracked down after, rewards you well.",
                reputationDelta = 15, goldDelta = 25,
            ),
            SideQuestResolution(
                "supply", "Just give them the coin they're asking for",
                "Relief floods their face as they snatch the coin and vanish toward whatever dealer's waiting. You feel worse than the gold in your pocket makes up for -- but the gold's still real.",
                reputationDelta = -10, goldDelta = 20,
            ),
        ),
    ),
    THE_CAGES(
        "What the Cellar Hides",
        "a merchant's account book that doesn't add up",
        "The numbers don't lie: too many \"goods\" moving through this merchant's cellar for anyone's comfort, and none of it matches what's on the shelves upstairs. Something -- someone -- is being kept down there.",
        listOf(SideQuestResolution(
            "raid", "Break into the cellar and free whoever's inside",
            "The cellar door gives with one good hit, and the people chained inside flinch at the light before they understand you're not one of their captors. You get them out, and word of it spreads fast and grateful.",
            reputationDelta = 25, goldDelta = 40,
        )),
    ),
    THE_WIDOWS_ERRAND(
        "A Promise Kept",
        "a widow clutching a folded letter",
        "\"They never came home from that cursed dungeon,\" she says quietly, holding out a small bundle -- a ring, a letter, a lock of hair. \"If you're ever down there... would you leave this where they fell? I can't go myself.\"",
        listOf(SideQuestResolution(
            "deliver", "Carry the bundle and leave it in their memory",
            "You find the spot -- you remember it, from your own trip through that dark place -- and leave the bundle where it belongs. It costs you nothing and means everything; she insists you take something for your trouble anyway.",
            reputationDelta = 10, goldDelta = 15,
        )),
    ),
    THE_SHAKEDOWN(
        "Coin for Looking Away",
        "a watch captain with an expensive new ring",
        "You watch the captain lean on a terrified shopkeeper, palm out, badge conspicuously displayed. This isn't the law. This is a toll -- and the captain's noticed you noticing.",
        listOf(
            SideQuestResolution(
                "report", "Report the captain to their superiors",
                "It takes some doing to find someone who'll listen, but the evidence is damning enough. The captain's marched off in disgrace, and the shopkeepers of the district take up a collection for you out of sheer relief.",
                reputationDelta = 18, goldDelta = 30,
            ),
            SideQuestResolution(
                "bribe", "Take a bribe to keep walking",
                "The captain's coin is heavier than your conscience, apparently. You walk away richer, and that shopkeeper's problem is still exactly as bad as it was five minutes ago.",
                reputationDelta = -15, goldDelta = 50,
            ),
        ),
    ),
    THE_DESERTER(
        "The Soldier Who Ran",
        "a haunted-looking veteran nursing a drink alone",
        "\"I ran,\" they say, before you've even asked. \"Everyone calls it cowardice. They ordered us to burn a village that hadn't done anything, and I ran instead of swinging the torch. Judge me if you like.\"",
        listOf(SideQuestResolution(
            "listen", "Tell them that was the braver choice",
            "Something in their shoulders loosens, like they've been waiting years for someone to say it. They press their old service medal into your hand -- they don't want it anymore, but they don't want to throw it away either.",
            reputationDelta = 8, goldDelta = 10, materialReward = "Tarnished Service Medal",
        )),
    ),
    STAR_CROSSED(
        "Two Villages, One Heart",
        "a breathless young courier with a hidden letter",
        "\"They're from rival villages,\" the courier whispers, \"and if either family finds out, it's over. Would you carry this to them? Please. I've no one else to trust.\"",
        listOf(
            SideQuestResolution(
                "carry", "Carry the letter and help the two elope",
                "You slip through both villages unnoticed and deliver the letter. Weeks later, word reaches you that the couple ran off together and are, against every odd, happy -- and a small thank-you gift arrives with the news.",
                reputationDelta = 10, goldDelta = 25,
            ),
            SideQuestResolution(
                "warn", "Warn the families instead and end it cleanly",
                "The families are furious, then relieved, then oddly grateful you kept it from going further and quieter than it might have. One family rewards your \"discretion\" generously.",
                reputationDelta = -5, goldDelta = 45,
            ),
        ),
    ),
    UNFINISHED_BUSINESS(
        "The Weight of a Battlefield",
        "a retired soldier who still wakes up screaming",
        "\"There's a field, not far from here, where I lost everyone I ever fought beside,\" they say, voice flat with old grief. \"I've never been able to go back. Would you go for me? Just... say something for them.\"",
        listOf(SideQuestResolution(
            "honor", "Visit the battlefield and honor the fallen",
            "You stand where they fell and say the words the soldier couldn't bring themself to say. When you return, something in the veteran's face has finally, quietly, let go. They insist you take their old campaign pay as thanks.",
            reputationDelta = 12, goldDelta = 20,
        )),
    ),
    BURIED_ATROCITY(
        "What the Nobles Buried",
        "a nervous archivist clutching a stolen ledger",
        "\"I found this in the estate records,\" the archivist hisses, sliding a ledger across the table. \"An entire village, wiped off the map, on the orders of the very nobles who run this Kingdom. I don't know what to do with it.\"",
        listOf(
            SideQuestResolution(
                "expose", "Expose the atrocity publicly",
                "The ledger's contents spread through the city like wildfire, and for once, the nobles can't simply make the problem disappear. The archivist, and half the city, thank you for it.",
                reputationDelta = 20, goldDelta = 25,
            ),
            SideQuestResolution(
                "blackmail", "Use it to blackmail the nobles for gold instead",
                "The payment arrives quietly, generously, and with an unspoken threat if you ever speak of it again. You take the gold. The truth stays buried a while longer.",
                reputationDelta = -10, goldDelta = 100,
            ),
        ),
    ),
    THE_BROKER(
        "Whispers for Sale",
        "an information broker who trades in everyone's business",
        "\"Coin for secrets, secrets for coin,\" they murmur without looking up from their nails. \"I know things about this whole Kingdom you couldn't find with a year of asking around. For a price, of course.\"",
        listOf(SideQuestResolution(
            "pay", "Pay for whatever secret they're willing to share",
            "They lean in and murmur something useful -- a name, a place, a warning -- that's worth far more than what you paid for it. \"Pleasure doing business,\" they say, already looking past you for the next customer.",
            reputationDelta = 0, goldDelta = -20, materialReward = "Useful Secret",
        )),
    ),
    THE_LEDGE(
        "Talking Someone Down",
        "a stranger standing far too close to a dangerous edge",
        "They're not looking at the view. They're looking at the drop. \"Just leave me be,\" they say, voice cracking, \"there's nothing left worth staying for.\"",
        listOf(SideQuestResolution(
            "talk", "Talk them away from the edge",
            "It takes longer than you'd like, and there's a moment you're genuinely not sure it's working -- but they step back. They don't say much afterward, just squeeze your hand once and press what little coin they have into it.",
            reputationDelta = 20, goldDelta = 10,
        )),
    ),
    BLOOD_DEBT(
        "A Debt in Blood",
        "a grim-faced survivor with nothing left to lose",
        "\"They killed my whole family and walked away laughing,\" they say, showing you a crude sketch of a face you recognize from your travels. \"I can't do it myself. I'm not strong enough. Will you finish what I can't start?\"",
        listOf(SideQuestResolution(
            "hunt", "Hunt down the killer and end it",
            "It's ugly, and it's not the kind of fight you walk away from feeling clean -- but it's done. The survivor doesn't smile when you tell them. They just finally, finally cry, and hand you everything of value they have left.",
            reputationDelta = 15, goldDelta = 60,
        )),
    ),
    THE_CONTRACT(
        "A Name and a Price",
        "a silk-clad noble with cold, patient eyes",
        "\"There's someone inconveniencing me,\" the noble says, sliding a folded name across the table along with a very heavy purse. \"I need them to become significantly less inconvenient. Permanently.\"",
        listOf(
            SideQuestResolution(
                "accept", "Accept the contract",
                "It's done quietly, professionally, and the noble pays exactly what was promised, down to the coin -- along with a look that makes clear they'll remember you can be bought.",
                reputationDelta = -20, goldDelta = 120,
            ),
            SideQuestResolution(
                "warn", "Warn the target and refuse the contract",
                "The target doesn't know whether to thank you or run, and does both. The noble never finds out it was you who tipped them off -- but the target, once they've calmed down, is generous with their gratitude.",
                reputationDelta = 20, goldDelta = 40,
            ),
        ),
    ),
    DESPERATE_HANDS(
        "Empty Granary, Empty Bellies",
        "a guard captain investigating a break-in that wasn't really a crime",
        "\"Someone broke into the granary last night,\" the captain sighs, \"but all they took was grain, and all the tracks lead back to the poorest street in the city. I know exactly who did it. I just don't want to arrest starving children.\"",
        listOf(
            SideQuestResolution(
                "pay", "Quietly pay off the granary's losses yourself",
                "You settle the account without a word to anyone, and the captain looks the other way on the whole affair, visibly relieved not to have to choose between duty and decency. They owe you, and they know it.",
                reputationDelta = 18, goldDelta = -40,
            ),
            SideQuestResolution(
                "report", "Report it and let the law take its course",
                "The captain grimaces but does their job, and a family goes hungrier for it. The granary owner, satisfied justice was served, rewards you for your \"civic diligence.\"",
                reputationDelta = -15, goldDelta = 35,
            ),
        ),
    ),
    THE_COLLECTOR(
        "A Buyer for the Unusual",
        "an eccentric collector with display cases full of oddities",
        "\"Ordinary shops won't touch the strange stuff you drag out of dungeons and battlefields,\" the collector grins, gesturing at shelves of curious relics. \"I pay top coin for materials nobody else wants. Well above market, if it's interesting enough.\"",
        listOf(SideQuestResolution(
            "sell", "Sell your rarest crafting material to the collector",
            "The collector examines it like a jeweler with a diamond, murmurs something reverent, and pays out nearly double what any shop would offer -- then asks, hopefully, if you have any more.",
            reputationDelta = 2, goldDelta = 0, // actual payout computed dynamically in Game.kt (material-value based), not a flat delta
        )),
    ),
    ;

    companion object {
        val all: List<SideQuestKind> = entries.toList()
    }
}
