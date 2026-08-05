package eldoria.core

import eldoria.core.data.BiomeContentRegistry
import eldoria.core.data.CraftingMaterialContentRegistry
import eldoria.core.data.DialogueContentRegistry
import eldoria.core.data.FamilyContentRegistry
import eldoria.core.data.HomeRegionContent
import eldoria.core.data.SkillTrainerContentRegistry
import eldoria.core.game.AnsiText
import eldoria.core.game.CharacterPanel
import eldoria.core.game.GameSession
import eldoria.core.game.MapRenderer
import eldoria.core.game.SubRealmPosition
import eldoria.core.model.ArtifactKind
import eldoria.core.model.Biome
import eldoria.core.model.CharacterClass
import eldoria.core.model.DiceFormula
import eldoria.core.model.DieType
import eldoria.core.model.Disposition
import eldoria.core.model.GameLocation
import eldoria.core.model.HiredCompanion
import eldoria.core.model.Item
import eldoria.core.model.ItemKind
import eldoria.core.model.Perk
import eldoria.core.model.PlayerCharacter
import eldoria.core.model.PopulationTier
import eldoria.core.model.Race
import eldoria.core.model.RealmKind
import eldoria.core.model.SideQuestKind
import eldoria.core.model.SkillType
import eldoria.core.model.SpawnEntry
import eldoria.core.model.SpawnKind
import eldoria.core.model.StatBlock
import eldoria.core.model.StatusEffect
import eldoria.core.model.Subclass
import eldoria.core.model.TerrainKind
import eldoria.core.world.BoatGenerator
import eldoria.core.world.CombatMath
import eldoria.core.world.LevelProgression
import eldoria.core.world.PerkEffects
import eldoria.core.world.PlayerCharacterFactory
import eldoria.core.world.SaveManager
import eldoria.core.world.ShopGenerator
import eldoria.core.world.SkillProgression
import eldoria.core.world.WorldConfig
import eldoria.core.world.WorldGenerator
import kotlin.random.Random
import kotlinx.datetime.Clock

private const val AUTOSAVE_INTERVAL_MILLIS = 10L * 60 * 1000

private fun prompt(text: String): String {
    print("$text> ")
    return readlnOrNull()?.trim().orEmpty()
}

private fun say(s: String) = println(s)

fun main() {
    say(AnsiText.bold("=== ELDORIA ==="))
    say(
        AnsiText.dim(
            "As a child, you were taken from your family -- stolen away by the Kingdom's own nobles, in defiance of\n" +
                "the king's law, for fear that you would grow strong enough to threaten their soft, cowardly grip on\n" +
                "power. Now an adult, you set out across the Kingdom of Eldoria to find the family they tore from you."
        )
    )
    say("\nA text-scroll RPG. Type 'help' any time for the command list.\n")

    if (SaveManager.exists()) {
        val resp = prompt("A previous save was found. Continue that game? (y/n)")
        if (resp.startsWith("y", ignoreCase = true)) {
            val snap = SaveManager.load()
            if (snap != null) {
                val world = WorldGenerator.generate(WorldConfig(seed = snap.seed))
                val session = GameSession(world, snap.player, snap.locationId, snap.homeLocationId, Random.Default)
                session.restoreFrom(snap)
                say("\nWelcome back, ${session.player.name}.")
                describeLocation(session)
                runGameLoop(session)
                return
            }
        }
    }

    val world = WorldGenerator.generate(WorldConfig())

    val name = prompt("What is your name?").ifBlank { "Wanderer" }
    say("\nChoose your race:")
    Race.entries.forEachIndexed { i, r -> say("  ${i + 1}) ${r.displayName} -- ${r.lore} (${r.resistanceLore})") }
    val race = Race.entries.getOrElse(prompt("Race").toIntOrNull()?.minus(1) ?: -1) { Race.HUMAN }

    say("\nChoose your class:")
    CharacterClass.entries.forEachIndexed { i, c -> say("  ${i + 1}) ${c.displayName} -- ${c.description}") }
    val charClass = CharacterClass.entries.getOrElse(prompt("Class").toIntOrNull()?.minus(1) ?: -1) { CharacterClass.WARRIOR }

    val creationRng = Random.Default
    val player = PlayerCharacterFactory.create(name, race, charClass, creationRng)

    val startLocation = world.locations.values
        .filter { it.biome == Biome.PLAINS && it.populationTier == PopulationTier.CITY }
        .minByOrNull { it.id } ?: world.locations.values.first { it.populationTier == PopulationTier.CITY }

    val session = GameSession(world, player, startLocation.id, startLocation.id, Random.Default)
    session.discover(startLocation.id)

    say("\n${AnsiText.bold(player.name)} the ${race.displayName} ${charClass.displayName} awakens in ${AnsiText.yellow(startLocation.name)}.")
    say("Wielding ${player.equippedWeapon?.name}, wearing ${player.equippedArmor?.name}. ${player.gold}g in your pouch.\n")

    describeLocation(session)
    runGameLoop(session)
}

private fun runGameLoop(session: GameSession) {
    var lastShopStock: List<Item> = emptyList()
    var lastShopTrader: String? = null
    var lastAutosaveMillis = Clock.System.now().toEpochMilliseconds()

    while (true) {
        session.advanceTick()
        checkCompanionExpiry(session)
        if (Clock.System.now().toEpochMilliseconds() - lastAutosaveMillis >= AUTOSAVE_INTERVAL_MILLIS) {
            SaveManager.save(session.snapshot())
            lastAutosaveMillis = Clock.System.now().toEpochMilliseconds()
        }
        val input = prompt("\n").trim()
        if (input.isEmpty()) continue
        val parts = input.split(Regex("\\s+"), limit = 2)
        val cmd = parts[0].lowercase()
        val arg = parts.getOrNull(1)?.trim().orEmpty()
        val player = session.player

        when (cmd) {
            "quit", "q" -> {
                say("Farewell, ${player.name}.")
                return
            }
            "help", "?" -> printHelp()
            "look", "l" -> describeLocation(session)
            "map", "m" -> say(MapRenderer.render(session))
            "character", "c", "sheet" -> say(CharacterPanel.render(session.player))
            "inventory", "inv", "i" -> say(CharacterPanel.renderInventory(session.player))
            "journal", "quests" -> printJournal(session)
            "codex", "bestiary" -> printCodex(session)
            "north", "n", "south", "s", "east", "e", "west", "w", "up", "down" -> move(session, canonicalDirection(cmd))
            "go" -> move(session, arg)
            "enter", "descend" -> enterPortal(session)
            "leave", "surface" -> leaveSubRealm(session)
            "talk" -> talk(session, arg)
            "train", "learn" -> train(session, arg)
            "attack", "fight" -> attack(session, arg)
            "take", "get" -> take(session, arg)
            "equip", "wear", "wield" -> equip(session, arg)
            "craft" -> craft(session, arg)
            "perk" -> choosePerk(session, arg)
            "rest" -> rest(session)
            "sleep" -> sleep(session)
            "hire" -> hireCompanion(session)
            "shop", "trade" -> {
                val stock = openShop(session)
                if (stock != null) {
                    lastShopStock = stock.second
                    lastShopTrader = stock.first
                }
            }
            "buy" -> when {
                arg.equals("boat", ignoreCase = true) -> buyBoat(session)
                arg.equals("cannons", ignoreCase = true) -> buyCannons(session)
                else -> buy(session, arg, lastShopTrader, lastShopStock)
            }
            "sell" -> sell(session, arg)
            "travel" -> travel(session, arg)
            "sail" -> sail(session, arg)
            "boat" -> boatStatus(session)
            "repair" -> repairBoat(session)
            "ferry" -> acceptFerry(session, arg)
            "ride" -> rideBalloon(session, arg)
            "resolve" -> resolveSideQuest(session, arg)
            "request" -> requestSubclass(session, arg)
            "upgrade" -> requestBionicUpgrade(session, arg)
            "confront" -> finalBattle(session)
            else -> say("Not sure what you mean. Type 'help' for commands.")
        }

        if (!session.player.isAlive) handleDeath(session)
    }
}

private fun canonicalDirection(cmd: String): String = when (cmd) {
    "n" -> "north"; "s" -> "south"; "e" -> "east"; "w" -> "west"
    else -> cmd
}

private fun printHelp() {
    say(
        """
        |Movement: north/n, south/s, east/e, west/w, up, down, go <exit>
        |Look:      look/l, map/m, character/c, inventory/inv, journal, codex
        |People:    talk <name>, train <name>, attack <name>
        |Items:     take <item>, equip <item>, craft <skill>
        |Places:    enter (a dungeon/sky portal), leave (a sub-realm), travel <city>
        |Shop:      shop, buy <#>, sell <#>
        |Boats:     buy boat, buy cannons, boat, sail <sea port>, repair (at a Sea settlement), ferry (if a fisherman happens by)
        |Balloon:   ride <city> (if a wandering aeronaut happens by a village -- goes anywhere, discovered or not)
        |Endgame:   confront (once every quest is complete and it's been unlocked)
        |Curses:    request vampire/werewolf (from the one who offers it, one-time, mutually exclusive)
        |Side quests: talk <name> to hear an offer, then resolve <keyword> to settle it -- always pays out something
        |Bionics:   upgrade strength/agility/willpower (Mad Scientist only, once per character)
        |Companion: hire (from a willing city local), talk/attack <name> also affects them
        |Other:     rest, sleep (safe rest only, heals stamina too, autosaves), perk, help, quit
        """.trimMargin()
    )
}

private fun describeLocation(session: GameSession) {
    session.discover(session.locationId)
    val room = session.currentRoom()
    if (room != null) {
        say(AnsiText.bold(room.name))
        say(AnsiText.white(room.description))
        say(AnsiText.white("Exits: " + room.exits.keys.joinToString(", ")))
    } else {
        val loc = session.currentLocation
        say(AnsiText.bold(loc.name))
        say(AnsiText.white(loc.description))
        say(AnsiText.white("Exits: " + loc.exits.keys.joinToString(", ")))
        if (loc.portalId != null) {
            val kind = if (loc.portalKind == RealmKind.DUNGEON) "dungeon entrance" else "beanstalk into the sky"
            say(AnsiText.white("There is a $kind here. (enter)"))
        }
    }

    val beings = session.currentBeings()
    if (beings.isNotEmpty()) {
        say("You see:")
        for ((_, b) in beings) {
            session.recordSeen(b.name)
            val label = when {
                b.disposition == Disposition.HOSTILE -> AnsiText.red("${b.name} [hostile]")
                b.kind == SpawnKind.NPC -> AnsiText.blue(b.name)
                else -> AnsiText.white(b.name)
            }
            val trainerTag = if (b.teachesSkill != null) AnsiText.cyan(" (trainer: ${b.teachesSkill.displayName})") else ""
            val familyTag = if (b.isFamilyMember && MAIN_QUEST_ID !in session.completedQuests) AnsiText.cyan(" (something about them feels familiar...)") else ""
            val companionTag = if (b.offersCompanionship) AnsiText.cyan(" (will travel with you, for a price -- 'hire')") else ""
            say("  - $label$trainerTag$familyTag$companionTag")
        }
    }

    val items = session.currentItems()
    if (items.isNotEmpty()) {
        say("Items here:")
        for (it in items) say("  - ${AnsiText.yellow(it.value.name)}")
    }

    session.player.companion?.let { say(AnsiText.cyan("${it.name} is at your side.")) }
}

private fun move(session: GameSession, direction: String) {
    val room = session.currentRoom()
    if (room != null) {
        val destId = room.exits[direction] ?: run { say("You can't go that way."); return }
        session.subRealmPosition = SubRealmPosition(session.subRealmPosition!!.subRealmId, destId)
        describeLocation(session)
        return
    }
    val loc = session.currentLocation
    val destId = loc.exits[direction] ?: run { say("You can't go that way."); return }
    val dest = session.world.locations.getValue(destId)

    if (dest.terrain == TerrainKind.WATERWAY && !session.player.hasGills) {
        val boat = session.player.ownedBoat
        if (boat == null) { say(AnsiText.white("Deep water blocks your path here. You'd need a boat, or find a bridge.")); return }
        if (boat.isBroken) { say(AnsiText.white("The water blocks your path, and your wrecked boat won't carry you across.")); return }
        session.player = session.player.copy(ownedBoat = boat.worn((1..2).random(session.rng)))
        if (session.player.ownedBoat!!.isBroken) say(AnsiText.red("Your boat groans and takes on water -- it won't survive much more of this."))
    } else if (dest.terrain == TerrainKind.WATERWAY) {
        say(AnsiText.cyan("You slip beneath the surface and swim across effortlessly, gills flaring in the current."))
    }

    session.recordOverworldDeparture(session.locationId)
    session.locationId = destId
    session.discover(destId)
    describeLocation(session)
    resolveHazard(session, dest)
    maybeFerryEncounter(session, dest)
    maybeBalloonEncounter(session, dest)
}

/** Natural dangers (quicksand, a cliff edge, a riptide...) are a survivable AGI check on arrival, not a monster fight. */
private fun resolveHazard(session: GameSession, dest: GameLocation) {
    val hazard = dest.hazard ?: return
    say(AnsiText.red("\n${hazard.displayName}: ${hazard.encounterLine}"))
    val agiMod = StatBlock.modifierOf(session.player.agility)
    val roll = CombatMath.attackRoll(session.rng, agiMod)
    val dc = 10 + dest.difficultyTier
    if (roll >= dc) {
        say(AnsiText.white(hazard.avoidLine))
        return
    }
    say(AnsiText.red(hazard.failLine))
    if (hazard.hitsGear) {
        val wearAmount = (2..5).random(session.rng)
        val boat = session.player.ownedBoat
        when {
            dest.terrain == TerrainKind.WATERWAY && boat != null -> {
                session.player = session.player.copy(ownedBoat = boat.worn(wearAmount))
                say(AnsiText.dim("Your boat takes the worst of it."))
            }
            session.player.equippedArmor != null -> {
                session.player = session.player.copy(equippedArmor = session.player.equippedArmor!!.worn(wearAmount))
                say(AnsiText.dim("Your armor takes the worst of it."))
            }
            else -> {
                val dmg = DiceFormula(dest.difficultyTier, DieType.D6, 0).roll(session.rng).coerceAtLeast(1)
                session.player = session.player.copy(currentHealth = session.player.currentHealth - dmg)
                say(AnsiText.dim("You take $dmg damage."))
            }
        }
    } else {
        val dmg = DiceFormula(dest.difficultyTier, DieType.D6, 0).roll(session.rng).coerceAtLeast(1)
        session.player = session.player.copy(currentHealth = session.player.currentHealth - dmg)
        say(AnsiText.dim("You take $dmg damage."))
    }
}

private fun enterPortal(session: GameSession) {
    if (session.inSubRealm) { say("You're already inside."); return }
    val loc = session.currentLocation
    val subRealmId = loc.portalId ?: run { say("There's nothing to enter here."); return }
    val realm = session.world.subRealms.getValue(subRealmId)
    session.subRealmPosition = SubRealmPosition(realm.id, realm.entryRoomId)
    session.discoveredQuests.add(realm.id)
    say(AnsiText.bold("You enter ${realm.name}."))
    say(AnsiText.white("Quest: ${realm.quest.objective}"))
    say(AnsiText.dim(DialogueContentRegistry.questFlavorLine(realm.quest.type, session.rng)))
    describeLocation(session)
}

private fun leaveSubRealm(session: GameSession) {
    val realm = session.currentSubRealm() ?: run { say("You're not inside anywhere you can leave."); return }
    session.recordSubRealmDeparture(realm)
    session.subRealmPosition = null
    say(AnsiText.white("You climb back out into ${session.currentLocation.name}."))
    describeLocation(session)
}

private fun findBeing(session: GameSession, query: String): IndexedValue<SpawnEntry>? {
    if (query.isBlank()) return null
    return session.currentBeings().firstOrNull { it.value.name.lowercase().contains(query.lowercase()) }
}

private const val MAIN_QUEST_ID = "MAIN_QUEST_FAMILY"

private val COMPANION_LINES = listOf(
    "\"Good to have company on a road like this,\" they say.",
    "\"Been a while since I trusted someone at my back this much.\"",
    "\"Wherever you're headed, I'm in. Been enjoying this more than I expected.\"",
    "\"Don't go getting yourself killed. I'd have to explain that back home.\"",
)

private fun askYesNo(text: String): Boolean = prompt("$text (yes/no)").lowercase().startsWith("y")

/**
 * The Python prototype's 6 named home-region NPCs (see
 * data/HomeRegionContent.kt) get their exact original dialogue trees
 * ported here rather than fit into SpawnEntry.offersSideQuest, which is
 * one-quest-per-NPC (these NPCs give up to three). Returns true if this
 * being was a home-region NPC and the dialogue was handled -- talk()
 * falls through to the normal archetype/trainer/etc. chain otherwise.
 */
private fun handleHomeRegionNpc(session: GameSession, being: SpawnEntry): Boolean {
    fun offerQuest(id: String, hookLine: String) {
        say(AnsiText.blue("\"$hookLine\""))
        if (askYesNo("Accept quest '${HomeRegionContent.questTitles.getValue(id)}'?")) {
            session.activeHomeRegionQuests.add(id)
            say(AnsiText.bold("[QUEST ACCEPTED]: ${HomeRegionContent.questTitles.getValue(id)}"))
        }
    }

    fun completeQuest(id: String, xp: Int, gold: Int, line: String) {
        session.activeHomeRegionQuests.remove(id)
        session.completedSideQuests.add(id)
        session.player = LevelProgression.applyExperience(session.player.copy(gold = session.player.gold + gold), xp, session.rng)
        say(AnsiText.blue("\"$line\""))
        say(AnsiText.bold("[QUEST COMPLETE]: ${HomeRegionContent.questTitles.getValue(id)} (+$xp XP, +${gold}g)"))
    }

    /** Consumes `count` copies of a named item from inventory, or returns false (and takes nothing) if there aren't enough. */
    fun consumeItems(name: String, count: Int): Boolean {
        val matching = session.player.inventory.filter { it.name == name }
        if (matching.size < count) return false
        session.player = session.player.copy(inventory = session.player.inventory - matching.take(count).toSet())
        return true
    }

    when (being.name) {
        HomeRegionContent.ELDER_THERON -> {
            say(AnsiText.blue("You approach ${being.name}."))
            val relic = HomeRegionContent.QUEST_ANCIENT_RELIC
            when {
                relic in session.completedSideQuests -> {}
                relic in session.activeHomeRegionQuests ->
                    if (consumeItems(HomeRegionContent.ITEM_ANCIENT_RELIC, 1))
                        completeQuest(relic, 150, 100, "You have returned the relic! Oakhaven is safer thanks to you, hero.")
                    else say(AnsiText.blue("\"Have you found the ancient relic yet? The village depends on it.\""))
                else -> offerQuest(relic, "The Whispering Woods hide an ancient relic, vital to our village's protection. Will you seek it out?")
            }
            val poison = HomeRegionContent.QUEST_POISONED_WATERS
            when {
                poison in session.completedSideQuests -> {}
                poison in session.activeHomeRegionQuests ->
                    if (consumeItems(HomeRegionContent.ITEM_SWAMP_HERB, HomeRegionContent.SWAMP_HERB_REQUIRED))
                        completeQuest(poison, 180, 120, "Excellent! These herbs will surely help. Thank you, adventurer.")
                    else say(AnsiText.blue("\"The waters still run foul. Have you found enough Swamp Herbs yet?\""))
                else -> offerQuest(poison, "Our water supply from the swamps has become tainted. If you could gather ${HomeRegionContent.SWAMP_HERB_REQUIRED} Swamp Herbs, it might help purify it.")
            }
            val goblins = HomeRegionContent.QUEST_GOBLIN_OUTBREAK
            val goblinsSlain = session.questCounters["Goblin Scavenger"] ?: 0
            when {
                goblins in session.completedSideQuests -> {}
                goblins in session.activeHomeRegionQuests ->
                    if (goblinsSlain >= HomeRegionContent.GOBLINS_REQUIRED)
                        completeQuest(goblins, 120, 80, "The roads are safer already. You have our thanks, goblin-slayer.")
                    else say(AnsiText.blue("\"The goblins still prowl. ${HomeRegionContent.GOBLINS_REQUIRED - goblinsSlain} more must fall.\""))
                else -> offerQuest(goblins, "Goblins have been raiding the roads and woods. Cull at least ${HomeRegionContent.GOBLINS_REQUIRED} of them and Oakhaven will reward you.")
            }
            return true
        }
        HomeRegionContent.FISHERMAN_FINN -> {
            say(AnsiText.blue("You approach ${being.name}."))
            val cargo = HomeRegionContent.QUEST_LOST_CARGO
            when {
                cargo in session.completedSideQuests -> say(AnsiText.blue("\"Bless yer soul, still keeping the coast safe, are ye?\""))
                cargo in session.activeHomeRegionQuests ->
                    if (consumeItems(HomeRegionContent.ITEM_SHIP_MANIFEST, 1))
                        completeQuest(cargo, 250, 150, "Bless yer soul! Me manifest! Now I can sort out this mess. Here's a little something for yer trouble.")
                    else say(AnsiText.blue("\"Any luck with me manifest, eh? It's down in that sunken wreck, I reckon.\""))
                else -> offerQuest(cargo, "Me cargo, lost in the shipwreck! If ye could find me manifest, I'd be mighty grateful.")
            }
            return true
        }
        HomeRegionContent.MOUNTAIN_GUIDE -> {
            say(AnsiText.blue("You approach ${being.name}."))
            val rescue = HomeRegionContent.QUEST_MOUNTAIN_RESCUE
            when {
                rescue in session.completedSideQuests -> {}
                rescue in session.activeHomeRegionQuests ->
                    if (consumeItems(HomeRegionContent.ITEM_LOST_MINER_NOTE, 1))
                        completeQuest(rescue, 300, 200, "A note from poor old Borin... at least we know what happened. Thank you for bringing closure.")
                    else say(AnsiText.blue("\"Still no sign of the lost miner? Be careful up there, it's treacherous.\""))
                else -> offerQuest(rescue, "A miner went missing in the northern pass. If you find him, or at least a note from him, I'd pay handsomely.")
            }
            val dragon = HomeRegionContent.QUEST_SLAY_THE_WYRM
            when {
                dragon in session.completedSideQuests -> {}
                dragon in session.activeHomeRegionQuests -> say(AnsiText.blue("\"The wyrm still lives -- I can see its smoke from here. Take the pass up to the peak, and gods be with you.\""))
                else -> offerQuest(dragon, "An ancient dragon slumbers atop Dragon's Peak. Slay it, and your name will be sung for generations. Few return from that summit...")
            }
            return true
        }
        HomeRegionContent.ARCANE_VENDOR -> {
            say(AnsiText.blue("You approach ${being.name}."))
            val fungi = HomeRegionContent.QUEST_ALCHEMICAL_FUNGI
            when {
                fungi in session.completedSideQuests -> say(AnsiText.blue("\"Our transaction was complete. Was there something else?\""))
                fungi in session.activeHomeRegionQuests ->
                    if (consumeItems(HomeRegionContent.ITEM_GLOWING_MUSHROOM, HomeRegionContent.GLOWING_MUSHROOM_REQUIRED))
                        completeQuest(fungi, 100, 60, "Ahh, they still glow with cave-light. Perfect. Our transaction is complete.")
                    else say(AnsiText.blue("\"No mushrooms yet? The Shadow Caves lie west of here.\""))
                else -> offerQuest(fungi, "I require reagents... Glowing Mushrooms from the Shadow Caves. Bring me ${HomeRegionContent.GLOWING_MUSHROOM_REQUIRED} and I shall make it worth your while.")
            }
            return true
        }
        HomeRegionContent.ANCIENT_SCHOLAR -> {
            say(AnsiText.blue("You approach ${being.name}."))
            val compass = HomeRegionContent.QUEST_ANCIENT_COMPASS
            when {
                compass in session.completedSideQuests -> {}
                compass in session.activeHomeRegionQuests ->
                    if (consumeItems(HomeRegionContent.ITEM_ANCIENT_COMPASS, 1))
                        completeQuest(compass, 400, 300, "Incredible! The Ancient Compass! Its magic is palpable. You have done a great service!")
                    else say(AnsiText.blue("\"The compass... it must be here somewhere. Keep searching the crypts.\""))
                else -> offerQuest(compass, "The legends speak of an Ancient Compass, hidden deep within these ruins. It holds immense power. Will you brave the dangers to find it?")
            }
            return true
        }
        HomeRegionContent.LOST_MINER -> {
            say(AnsiText.blue("You approach ${being.name}."))
            val rescue = HomeRegionContent.QUEST_MOUNTAIN_RESCUE
            if (rescue in session.activeHomeRegionQuests && rescue !in session.completedSideQuests) {
                say(AnsiText.blue("\"Oh, thank the heavens! I'm trapped! I dropped my note somewhere nearby, please take it to the guide in the south!\""))
                if (session.player.inventory.none { it.name == HomeRegionContent.ITEM_LOST_MINER_NOTE }) {
                    val note = Item(name = HomeRegionContent.ITEM_LOST_MINER_NOTE, kind = ItemKind.QUEST_ITEM, tier = 1, value = 0, maxDurability = 1)
                    session.player = session.player.copy(inventory = session.player.inventory + note)
                    say(AnsiText.yellow("You received the ${HomeRegionContent.ITEM_LOST_MINER_NOTE}."))
                }
            } else {
                say(AnsiText.blue("\"Just need to rest a bit... then I'll try to find my way out.\""))
            }
            return true
        }
        else -> return false
    }
}

private fun talk(session: GameSession, arg: String) {
    val companion = session.player.companion
    if (companion != null && arg.isNotBlank() && arg.lowercase() in companion.name.lowercase()) {
        say(AnsiText.cyan(COMPANION_LINES.random(session.rng)))
        return
    }
    val found = findBeing(session, arg) ?: run { say("There's no one here by that name."); return }
    val being = found.value
    if (being.disposition == Disposition.HOSTILE) {
        say(DialogueContentRegistry.hostileLine(being.name, session.rng))
        if (ArtifactKind.TELEPATH_DEVICE in session.player.artifacts) {
            say(AnsiText.cyan("You brush against their surface thoughts: roughly ${being.stats.maxHealth} health, armor rated about ${being.stats.armorClass}."))
        }
        return
    }
    if (handleHomeRegionNpc(session, being)) return
    if (being.isFamilyMember) {
        if (MAIN_QUEST_ID in session.completedQuests) {
            say(AnsiText.blue("\"Every day you're still here is a good day,\" they say, smiling."))
            return
        }
        say(AnsiText.bold(FamilyContentRegistry.reunionLines.random(session.rng).replace("{name}", being.name)))
        session.completedQuests.add(MAIN_QUEST_ID)
        val repDelta = 25
        session.player = session.player.copy(reputation = (session.player.reputation + repDelta).coerceIn(-100, 100))
        say(AnsiText.bold("MAIN QUEST COMPLETE: after all these years, you've found your family."))
        say(AnsiText.dim("Your reputation rises -- word travels fast of the stolen child who came home."))
        checkEndgameTrigger(session)
        return
    }
    val trainer = if (being.teachesSkill != null) SkillTrainerContentRegistry.all.firstOrNull { it.name == being.name } else null
    if (trainer != null) {
        say(AnsiText.blue(trainer.greeting))
        if (!session.player.knowsSkill(trainer.skill)) say(AnsiText.blue(trainer.teachOffer) + AnsiText.dim(" (type 'train ${trainer.skill.displayName.lowercase()}')"))
        else say(AnsiText.dim("(You already know ${trainer.skill.displayName}.)"))
        return
    }
    if (being.offersSubclass != null) {
        val offer = being.offersSubclass
        when {
            session.player.subclass == offer -> say(AnsiText.dim("You already carry ${offer.displayName}'s curse. There's nothing more they can give you."))
            session.player.subclass != null -> say(AnsiText.blue("\"${offer.displayName}'s curse and your own don't mix,\" they say, almost pitying. \"You made your choice already.\""))
            else -> {
                say(AnsiText.blue("\"You want what I have,\" they say, studying you. \"${offer.strengthDescription} But know this -- ${offer.weaknessDescription.replaceFirstChar { it.lowercase() }}\""))
                say(AnsiText.dim("(type 'request ${offer.name.lowercase()}' to accept -- this cannot be undone, and you can never take the other path)"))
            }
        }
        return
    }
    if (being.offersBionicUpgrade) {
        if (session.player.bionicUpgradeUsed) {
            say(AnsiText.blue("\"Only got the one working rig, friend. Already used yours.\""))
        } else {
            say(
                AnsiText.blue(
                    "\"Heh heh -- steel, ore, and a bit of GENIUS, that's all it takes!\" the old man cackles, tapping a crude " +
                        "bionic contraption strapped to his own arm. \"Modest price, and I'll wire one basic ability of yours up " +
                        "PAST what nature gave you. Strength, quickness, or wits -- your choice, permanent, +5. One customer, one rig, no refunds!\""
                )
            )
            say(AnsiText.dim("(type 'upgrade strength', 'upgrade agility', or 'upgrade willpower' for ${BIONIC_UPGRADE_COST}g)"))
        }
        return
    }
    if (being.offersSideQuest != null) {
        val quest = being.offersSideQuest
        if (quest.name in session.completedSideQuests) {
            say(AnsiText.blue("\"Good on you for helping, back there,\" they say, with the easy warmth of someone who still remembers what you did."))
        } else {
            say(AnsiText.bold(quest.title))
            say(AnsiText.blue(quest.hookLine))
            for (r in quest.resolutions) say(AnsiText.dim("  (type 'resolve ${r.keyword}' -- ${r.label})"))
        }
        return
    }
    val loc = session.currentRoom()?.name ?: session.currentLocation.name
    val biome = session.currentSubRealm()?.biome ?: session.currentLocation.biome
    say(AnsiText.blue(DialogueContentRegistry.civilianLine(being.name, loc, biome, session.rng)))
    if (ArtifactKind.TELEPATH_DEVICE in session.player.artifacts) {
        say(AnsiText.cyan("You catch their surface thoughts: ${DialogueContentRegistry.telepathyLine(session.rng)}"))
    }
}

private fun train(session: GameSession, arg: String) {
    val trainerBeing = session.currentBeings().map { it.value }.firstOrNull { it.teachesSkill != null }
    if (trainerBeing == null) { say("No one here can train you."); return }
    val trainer = SkillTrainerContentRegistry.all.first { it.name == trainerBeing.name }
    if (session.player.knowsSkill(trainer.skill)) { say("You already know ${trainer.skill.displayName}."); return }
    session.player = SkillProgression.learnSkillFromTrainer(session.player, trainer.skill)
    say(AnsiText.blue(trainer.teachOffer))
    say(AnsiText.bold("You have learned ${trainer.skill.displayName}! (starting level ${session.player.skillLevel(trainer.skill)})"))
}

private fun brokerHint(session: GameSession): String {
    val familyBiome = session.world.locations.values.firstOrNull { loc -> loc.beings.any { it.isFamilyMember } }?.biome?.displayName
    val hints = listOfNotNull(
        familyBiome?.let { "Word is a certain someone you've been looking for is somewhere in the $it." },
        "There's a homeless tinkerer in one of the cities who'll bolt something remarkable onto you, for a price.",
        "Sailors mutter about something enormous in the deep sea -- the Big Kahoon-a, they call it. Best have a strong boat, and better cannons.",
        "Not every curse is a bad trade. Ask around the wilder corners of the Kingdom if you're feeling reckless -- a bite or a bargain, your pick.",
        "Rivers cut clean through this Kingdom now. A boat gets you across, or so I hear, something stranger might too.",
    )
    return hints.random(session.rng)
}

/** Three back-to-back bouts against generated pit fighters, difficulty rising with the city's tier -- lose any bout and the gauntlet ends. */
private fun fightArenaGauntlet(session: GameSession): Boolean {
    val tier = session.currentLocation.difficultyTier.coerceAtLeast(1)
    for (round in 1..3) {
        val foeName = "Pit Fighter ${listOf("Grimjaw", "Blackscar", "Ironhide", "Stonefist").random(session.rng)}"
        val foeStats = eldoria.core.world.StatGenerator.creatureStats((tier + round - 1).coerceAtMost(5), session.rng)
        say(AnsiText.red("\nBout $round: $foeName steps into the pit."))
        var foeHp = foeStats.maxHealth
        var combatRound = 0
        while (foeHp > 0 && session.player.isAlive && combatRound < 20) {
            combatRound++
            val playerRoll = CombatMath.attackRoll(session.rng, session.player.attackBonus)
            if (CombatMath.isHit(playerRoll, foeStats.armorClass)) {
                val dmg = (session.player.equippedWeapon?.damage ?: session.player.unarmedDamage).roll(session.rng).coerceAtLeast(1)
                foeHp -= dmg
                say("  You hit $foeName for $dmg damage.")
            } else {
                say(AnsiText.dim("  You miss $foeName."))
            }
            if (foeHp <= 0) break
            val foeRoll = CombatMath.attackRoll(session.rng, foeStats.attackBonus)
            if (CombatMath.isHit(foeRoll, session.player.armorClass)) {
                val dmg = foeStats.damage.roll(session.rng).coerceAtLeast(1)
                session.player = session.player.copy(currentHealth = session.player.currentHealth - dmg)
                say(AnsiText.red("  $foeName hits you for $dmg damage."))
            } else {
                say(AnsiText.dim("  $foeName misses."))
            }
        }
        if (!session.player.isAlive) { handleDeath(session); return false }
        if (foeHp > 0) return false
        say(AnsiText.bold("  $foeName goes down!"))
    }
    return true
}

private fun resolveSideQuest(session: GameSession, arg: String) {
    val being = session.currentBeings().map { it.value }.firstOrNull { it.offersSideQuest != null }
    if (being == null) { say("There's no one here with unfinished business for you."); return }
    val quest = being.offersSideQuest!!
    if (quest.name in session.completedSideQuests) { say("You've already settled things with ${being.name}."); return }
    val resolution = quest.resolutions.firstOrNull { it.keyword.equals(arg, ignoreCase = true) }
    if (resolution == null) {
        say("That's not one of the choices ${being.name} gave you. Options: " + quest.resolutions.joinToString(", ") { it.keyword })
        return
    }

    when (quest) {
        SideQuestKind.UNDERGROUND_DICE_DEN -> {
            if (session.player.gold < 20) { say("You need 20g on hand to sit at this table."); return }
            val roll = DiceFormula(1, DieType.D20).roll(session.rng)
            val won = roll >= 11
            session.player = session.player.copy(gold = session.player.gold + if (won) 20 else -20)
            say(AnsiText.bold("The die shows $roll. ${if (won) "You win -- the table groans as the gambler pays out double." else "You lose -- the gambler sweeps your coin away without a flicker of sympathy."}"))
            session.completedSideQuests.add(quest.name)
        }
        SideQuestKind.THE_COLLECTOR -> {
            val material = session.player.materials.entries.filter { it.value > 0 }.maxByOrNull { it.value }
            if (material == null) { say("\"Come back when you've actually got something interesting on you,\" the collector sighs."); return }
            val payout = (30..80).random(session.rng)
            session.player = session.player.copy(
                materials = session.player.materials + (material.key to material.value - 1),
                gold = session.player.gold + payout,
            )
            say(AnsiText.bold("The collector pays ${payout}g for your ${material.key}, practically vibrating with excitement."))
            session.completedSideQuests.add(quest.name)
        }
        SideQuestKind.THE_BROKER -> {
            if (session.player.gold < 20) { say("\"Twenty gold, or don't waste my time,\" the broker says flatly."); return }
            val hint = brokerHint(session)
            session.player = session.player.copy(gold = session.player.gold - 20)
            say(AnsiText.bold("The broker leans in close: \"$hint\""))
            session.completedSideQuests.add(quest.name)
        }
        SideQuestKind.UNDERGROUND_ARENA -> {
            val won = fightArenaGauntlet(session)
            if (!session.player.isAlive) return
            if (won) {
                session.player = session.player.copy(
                    reputation = (session.player.reputation + resolution.reputationDelta).coerceIn(-100, 100),
                    gold = session.player.gold + resolution.goldDelta,
                )
                say(AnsiText.bold(resolution.outcomeLine))
                session.completedSideQuests.add(quest.name)
            } else {
                say(AnsiText.red("You're beaten before the gauntlet's done. The pit boss shrugs and shows you the door -- no shame in it, but no purse either."))
            }
        }
        else -> {
            if (resolution.goldDelta < 0 && session.player.gold + resolution.goldDelta < 0) {
                say("You can't afford that right now (${-resolution.goldDelta}g needed)."); return
            }
            session.player = session.player.copy(
                reputation = (session.player.reputation + resolution.reputationDelta).coerceIn(-100, 100),
                gold = session.player.gold + resolution.goldDelta,
            )
            resolution.materialReward?.let { mat ->
                session.player = session.player.copy(materials = session.player.materials + (mat to (session.player.materials[mat] ?: 0) + 1))
            }
            say(AnsiText.bold(resolution.outcomeLine))
            session.completedSideQuests.add(quest.name)
        }
    }
}

private const val BIONIC_UPGRADE_COST = 75

/** Vampire or Werewolf -- permanent, one-time, and mutually exclusive: taking one locks the other out forever for this character. */
private fun requestSubclass(session: GameSession, arg: String) {
    val giver = session.currentBeings().map { it.value }.firstOrNull { it.offersSubclass != null }
    if (giver == null) { say("No one here can offer you that."); return }
    val offer = giver.offersSubclass!!
    if (!arg.contains(offer.name, ignoreCase = true) && arg.isNotBlank() && !offer.displayName.contains(arg, ignoreCase = true)) {
        say("Ask them plainly -- 'request ${offer.displayName.lowercase()}'."); return
    }
    if (session.player.subclass == offer) { say("You already carry that curse."); return }
    if (session.player.subclass != null) { say("You've already given yourself to ${session.player.subclass!!.displayName}'s curse -- there's no room for another."); return }

    session.player = session.player.copy(
        subclass = offer,
        strength = session.player.strength + offer.strengthBonus,
        agility = session.player.agility + offer.agilityBonus,
        willpower = session.player.willpower + offer.willpowerBonus,
        maxHealth = (session.player.maxHealth + offer.maxHealthBonus).coerceAtLeast(1),
        currentHealth = (session.player.currentHealth + offer.maxHealthBonus).coerceAtLeast(1),
        armorClass = session.player.armorClass + offer.armorClassBonus,
    )
    say(AnsiText.bold(offer.lore))
    say(AnsiText.bold("You are now a ${offer.displayName}."))
    say(AnsiText.dim("Strength: ${offer.strengthDescription}"))
    say(AnsiText.dim("Weakness: ${offer.weaknessDescription}"))
}

/** The Mad Scientist's one-time +5 ability bionic implant -- permanent, once per character. */
private fun requestBionicUpgrade(session: GameSession, arg: String) {
    val scientist = session.currentBeings().map { it.value }.firstOrNull { it.offersBionicUpgrade }
    if (scientist == null) { say("There's no one here who can do that."); return }
    if (session.player.bionicUpgradeUsed) { say("\"Told you -- one rig, one customer. That's you, already done.\""); return }
    if (session.player.gold < BIONIC_UPGRADE_COST) { say("\"Come back with ${BIONIC_UPGRADE_COST}g and we'll talk business.\""); return }

    val updated = when {
        arg.contains("str", ignoreCase = true) -> session.player.copy(strength = session.player.strength + 5)
        arg.contains("agi", ignoreCase = true) -> session.player.copy(agility = session.player.agility + 5)
        arg.contains("wil", ignoreCase = true) -> session.player.copy(willpower = session.player.willpower + 5)
        else -> { say("Choose one: 'upgrade strength', 'upgrade agility', or 'upgrade willpower'."); return }
    }
    session.player = updated.copy(gold = updated.gold - BIONIC_UPGRADE_COST, bionicUpgradeUsed = true)
    say(AnsiText.red("Rusty tools whir and spark against your skin -- it hurts more than you expected, then it doesn't hurt at all."))
    say(AnsiText.bold("\"Steel and ore, friend. Steel and ore.\" The bionic upgrade takes hold, permanently."))
}

private fun weaponSkillFor(item: Item?): SkillType = when {
    item == null -> SkillType.UNARMED
    item.name.contains("Bow", ignoreCase = true) -> SkillType.ARCHERY
    item.name.contains("Staff", ignoreCase = true) || item.name.contains("Mace", ignoreCase = true) -> SkillType.ONE_HANDED
    item.name.contains("Great", ignoreCase = true) || item.name.contains("Maul", ignoreCase = true) || item.name.contains("Warhammer", ignoreCase = true) -> SkillType.TWO_HANDED
    else -> SkillType.ONE_HANDED
}

private fun attack(session: GameSession, arg: String) {
    if (session.player.companion != null && arg.isNotBlank() && arg.lowercase() in session.player.companion!!.name.lowercase()) {
        say("You can't attack your own companion."); return
    }
    val found = findBeing(session, arg) ?: run { say("There's nothing here by that name to fight."); return }
    val (index, target) = found
    var targetHp = target.stats.maxHealth
    val weaponSkill = weaponSkillFor(session.player.equippedWeapon)
    val tier = session.currentRoom()?.difficultyTier ?: session.currentLocation.difficultyTier
    // Perk.CRITICAL_FOCUS lowers the crit threshold by 1 per rank (nat 20, then 19+, ...); floored so a fumble (nat 1) is never in reach.
    val critThreshold = (20 - session.player.perkRank(Perk.CRITICAL_FOCUS)).coerceAtLeast(15)

    // Enemy-side status effect (see model/StatusEffect.kt) -- combat-local
    // only, never persisted, matching the source prototype where only the
    // player's attacks ever inflict a status, never the reverse.
    var targetStatus: StatusEffect? = null
    var targetStatusTurns = 0

    if (target.disposition != Disposition.HOSTILE) say(AnsiText.red("You raise your weapon against ${target.name}! This will not go unnoticed."))
    else say(AnsiText.red(DialogueContentRegistry.hostileLine(target.name, session.rng)))

    var round = 0
    while (targetHp > 0 && session.player.isAlive && round < 30) {
        round++
        session.player = session.player.copy(currentStamina = (session.player.currentStamina - 1).coerceAtLeast(0))
        val exhausted = session.player.isExhausted
        val exhaustionPenalty = if (exhausted) 2 else 0
        val playerRoll = CombatMath.attackRollDetailed(session.rng, session.player.attackBonus - exhaustionPenalty, critThreshold)
        if (exhausted && round == 1) say(AnsiText.dim("  You're exhausted -- your strikes are slower and less sure."))
        if (playerRoll.isFumble) {
            say(AnsiText.dim("  You fumble badly and swing at nothing. (natural 1)"))
        } else if (CombatMath.isHit(playerRoll, target.stats.armorClass)) {
            val subclass = session.player.subclass
            val rage = if (subclass != null && session.player.currentHealth * 2 < session.player.maxHealth) subclass.lowHealthRageBonus else 0
            val weapon = session.player.equippedWeapon
            val weaponDamage = weapon?.damage ?: session.player.unarmedDamage
            val dmg = (if (playerRoll.isCritical) CombatMath.criticalDamage(weaponDamage, session.rng) else weaponDamage.roll(session.rng)).coerceAtLeast(1) + rage
            targetHp -= dmg
            val rageNote = if (rage > 0) AnsiText.red(" (rage +$rage)") else ""
            val critNote = if (playerRoll.isCritical) AnsiText.bold(" CRITICAL HIT!") else ""
            say("  You strike ${target.name} for $dmg damage.$rageNote$critNote (roll ${playerRoll.total} vs AC ${target.stats.armorClass})")
            session.player = SkillProgression.gainSkillUse(session.player, weaponSkill, session.rng)
            if (subclass != null && subclass.lifestealPercent > 0) {
                val healed = (dmg * subclass.lifestealPercent / 100.0).toInt().coerceAtLeast(1)
                val newHealth = (session.player.currentHealth + healed).coerceAtMost(session.player.maxHealth)
                session.player = session.player.copy(currentHealth = newHealth)
                say(AnsiText.dim("  The wound feeds you -- you recover $healed health."))
            }
            weapon?.inflictsStatus?.let { effect ->
                if (effect in target.stats.statusResistances) {
                    say(AnsiText.dim("  ${target.name} resists the ${effect.displayName.lowercase()}."))
                } else {
                    targetStatus = effect
                    targetStatusTurns = effect.defaultTurns
                    say(AnsiText.red("  ${target.name} is afflicted with ${effect.displayName}!"))
                }
            }
        } else {
            say(AnsiText.dim("  You swing at ${target.name} and miss. (roll ${playerRoll.total} vs AC ${target.stats.armorClass})"))
        }
        if (targetHp <= 0) break

        session.player.companion?.let { comp ->
            val compRoll = CombatMath.attackRoll(session.rng, comp.attackBonus)
            if (CombatMath.isHit(compRoll, target.stats.armorClass)) {
                val compDmg = comp.damage.roll(session.rng).coerceAtLeast(1)
                targetHp -= compDmg
                say(AnsiText.cyan("  ${comp.name} strikes ${target.name} for $compDmg damage."))
            } else {
                say(AnsiText.dim("  ${comp.name} attacks ${target.name} and misses."))
            }
        }
        if (targetHp <= 0) break

        var foeSkipsTurn = false
        targetStatus?.let { status ->
            if (status.perTurnDamage > 0) {
                targetHp -= status.perTurnDamage
                say(AnsiText.red("  ${target.name} suffers ${status.perTurnDamage} ${status.displayName.lowercase()} damage!"))
            }
            foeSkipsTurn = status.skipsTurn
            if (foeSkipsTurn) say(AnsiText.cyan("  ${target.name} is frozen solid and cannot act!"))
            targetStatusTurns--
            if (targetStatusTurns <= 0) {
                say(AnsiText.dim("  The ${status.displayName.lowercase()} on ${target.name} fades."))
                targetStatus = null
            }
        }
        if (targetHp <= 0) break

        if (!foeSkipsTurn) {
            val foeRoll = CombatMath.attackRollDetailed(session.rng, target.stats.attackBonus)
            if (foeRoll.isFumble) {
                say(AnsiText.dim("  ${target.name} fumbles and misses badly. (natural 1)"))
            } else if (CombatMath.isHit(foeRoll, session.player.armorClass)) {
                var dmg = if (foeRoll.isCritical) CombatMath.criticalDamage(target.stats.damage, session.rng) else target.stats.damage.roll(session.rng)
                dmg = dmg.coerceAtLeast(1)
                target.stats.magicDamage?.let { dmg += it.roll(session.rng) }
                val resisted = (dmg * session.player.race.magicResistancePercent / 100.0).toInt()
                dmg = (dmg - resisted).coerceAtLeast(1)
                val newHp = session.player.currentHealth - dmg
                session.player = session.player.copy(currentHealth = newHp)
                val critNote = if (foeRoll.isCritical) AnsiText.bold(" CRITICAL HIT!") else ""
                say("  ${target.name} hits you for $dmg damage.$critNote (roll ${foeRoll.total} vs your AC ${session.player.armorClass})")
            } else {
                say(AnsiText.dim("  ${target.name} attacks and misses. (roll ${foeRoll.total} vs your AC ${session.player.armorClass})"))
            }
        }
        if (!session.player.isAlive) return
    }

    if (targetHp <= 0) {
        say(AnsiText.bold("You have defeated ${target.name}!"))
        session.markDefeated(index, target.name)
        session.incrementQuestCounter(target.name)
        if (target.name == "Ancient Flame Dragon" && HomeRegionContent.QUEST_SLAY_THE_WYRM in session.activeHomeRegionQuests) {
            session.activeHomeRegionQuests.remove(HomeRegionContent.QUEST_SLAY_THE_WYRM)
            session.completedSideQuests.add(HomeRegionContent.QUEST_SLAY_THE_WYRM)
            val trophy = Item(name = "Dragon Scale Trophy", kind = ItemKind.TRINKET, tier = 5, value = 750, maxDurability = 1, isLegendary = true)
            session.player = session.player.copy(inventory = session.player.inventory + trophy, gold = session.player.gold + 1000)
            session.player = LevelProgression.applyExperience(session.player, 1000, session.rng)
            say(AnsiText.bold("[QUEST COMPLETE]: Slay the Wyrm (+1000 XP, +1000g, Dragon Scale Trophy)"))
        }
        val xp = LevelProgression.xpForDefeating(tier, session.rng)
        val before = session.player.level
        session.player = LevelProgression.applyExperience(session.player, xp, session.rng)
        say("You gain $xp experience.")
        if (session.player.level > before) say(AnsiText.bold("You reached level ${session.player.level}!"))
        if (session.player.pendingPerkChoices > 0) say(AnsiText.cyan("You have a perk choice available! Type 'perk' to choose."))

        val repDelta = if (target.disposition == Disposition.HOSTILE) (1..3).random(session.rng) else -20
        session.player = session.player.copy(reputation = (session.player.reputation + repDelta).coerceIn(-100, 100))
        if (repDelta < 0) say(AnsiText.red("Word of this will spread. Your reputation suffers."))

        if (target.kind == SpawnKind.CREATURE && target.disposition == Disposition.HOSTILE && session.rng.nextInt(100) < 30) {
            val biome = session.currentSubRealm()?.biome ?: session.currentLocation.biome
            val material = CraftingMaterialContentRegistry.materialsFor(biome).random(session.rng)
            session.player = session.player.copy(materials = session.player.materials + (material.name to (session.player.materials[material.name] ?: 0) + 1))
            say(AnsiText.yellow("${target.name} dropped: ${material.name}"))
        }

        val realm = session.currentSubRealm()
        if (realm != null && index == realm.rooms.getValue(realm.bossRoomId).beings.indexOf(target) && session.currentRoom()?.isBossRoom == true) {
            say(AnsiText.bold("The way to ${realm.quest.title}'s treasures lies open."))
        }
    }
}

private fun take(session: GameSession, arg: String) {
    val indexed = session.currentItems().firstOrNull { it.value.name.lowercase().contains(arg.lowercase()) }
    if (indexed == null) { say("You don't see that here."); return }
    val item = indexed.value
    session.markTaken(indexed.index)

    val artifact = ArtifactKind.entries.firstOrNull { it.itemName == item.name }
    if (artifact != null) {
        say(AnsiText.bold(artifact.activationLine))
        session.player = session.player.copy(
            artifacts = session.player.artifacts + artifact,
            attackBonus = session.player.attackBonus + artifact.attackBonus,
            armorClass = session.player.armorClass + artifact.armorClassBonus,
        )
        say(AnsiText.dim("(${item.name} is now a permanent part of you.)"))
        return
    }

    session.player = session.player.copy(inventory = session.player.inventory + item)
    say(AnsiText.yellow("You take the ${item.name}."))
    val realm = session.currentSubRealm()
    if (realm != null && session.currentRoom()?.isBossRoom == true && item.name == realm.quest.questItem.name) {
        session.completedQuests.add(realm.id)
        say(AnsiText.bold("Quest complete: ${realm.quest.title}!"))
        val repDelta = (5..10).random(session.rng)
        session.player = session.player.copy(reputation = (session.player.reputation + repDelta).coerceIn(-100, 100))
        checkEndgameTrigger(session)
    }
}

/**
 * Adds (sign=1) or removes (sign=-1) an equipped item's passive bonus.
 * armorClassBonus covers the three physical slots (chest/offhand/head);
 * magicEffect covers rings/amulets (see Item.kt's doc on why they share
 * that field instead of dedicated hp/mp/atk/def bonus fields). Weapons
 * carry no passive bonus of their own -- their damage is read live off
 * equippedWeapon at attack-time, not baked into a stat here.
 */
internal fun applyItemBonus(player: PlayerCharacter, item: Item, sign: Int): PlayerCharacter {
    var p = player
    item.armorClassBonus?.let { p = p.copy(armorClass = p.armorClass + it * sign) }
    item.magicEffect?.let { effect ->
        val delta = effect.magnitude * (if (effect.beneficial) 1 else -1) * sign
        p = when (effect.affectedTrait) {
            "strength" -> p.copy(strength = p.strength + delta)
            "agility" -> p.copy(agility = p.agility + delta)
            "willpower" -> p.copy(willpower = p.willpower + delta)
            "armorClass" -> p.copy(armorClass = p.armorClass + delta)
            "speed" -> p.copy(speed = p.speed + delta)
            else -> p
        }
    }
    return p
}

private val EQUIPPABLE_KINDS = setOf(ItemKind.WEAPON, ItemKind.ARMOR, ItemKind.OFFHAND, ItemKind.HEAD, ItemKind.RING, ItemKind.AMULET)

private fun equip(session: GameSession, arg: String) {
    val item = session.player.inventory.firstOrNull { it.name.lowercase().contains(arg.lowercase()) }
    if (item == null) { say("You don't have that."); return }
    if (item.kind !in EQUIPPABLE_KINDS) { say("You can't equip that."); return }

    var player = session.player
    val previous = player.equippedInSlot(item.kind)
    if (previous != null) {
        player = applyItemBonus(player, previous, sign = -1)
        player = player.copy(inventory = player.inventory + previous)
    }
    player = player.withEquippedInSlot(item.kind, item).copy(inventory = player.inventory - item)
    player = applyItemBonus(player, item, sign = 1)

    session.player = player
    val swapNote = if (previous != null) " (${previous.name} returned to your pack)" else ""
    say(AnsiText.yellow("You equip the ${item.name}.$swapNote"))
}

private fun craft(session: GameSession, arg: String) {
    val skill = SkillType.entries.firstOrNull { it.category.name == "CRAFTING" && it.displayName.lowercase().contains(arg.lowercase()) }
    if (skill == null) { say("Craft what? Try: blacksmithing, alchemy, enchanting, woodworking, leatherworking."); return }
    if (!session.player.knowsSkill(skill)) { say("You haven't learned ${skill.displayName} yet."); return }
    val material = session.player.materials.entries.firstOrNull { (name, count) ->
        count >= 2 && CraftingMaterialContentRegistry.all.any { it.name == name && it.feedsSkill == skill }
    }
    if (material == null) { say("You need at least 2 of a matching material for ${skill.displayName}."); return }

    val tier = ((session.player.skillLevel(skill)) / 20 + 1).coerceIn(1, 5)
    val crafted = when (skill) {
        SkillType.BLACKSMITHING -> eldoria.core.world.StatGenerator.weaponItem("Handforged ${material.key.removeSuffix("Ore").trim()} Blade", tier, session.rng)
        SkillType.LEATHERWORKING -> eldoria.core.world.StatGenerator.armorItem("Tailored ${material.key} Armor", tier, session.rng)
        SkillType.ENCHANTING -> eldoria.core.world.StatGenerator.weaponItem("Enchanted ${material.key} Charm", tier, session.rng, legendary = true)
        SkillType.WOODWORKING -> eldoria.core.world.StatGenerator.weaponItem("Carved ${material.key} Bow", tier, session.rng)
        SkillType.ALCHEMY -> eldoria.core.world.StatGenerator.questItem("${material.key} Elixir", tier, session.rng)
        else -> { say("Can't craft that."); return }
    }

    session.player = session.player.copy(
        materials = session.player.materials + (material.key to material.value - 2),
        inventory = session.player.inventory + crafted,
    )
    session.player = SkillProgression.gainSkillUse(session.player, skill, session.rng)
    say(AnsiText.bold("Using ${material.key}, you craft: ${crafted.name}!"))
    say(AnsiText.dim("${skill.displayName} is now level ${session.player.skillLevel(skill)}."))
}

private fun choosePerk(session: GameSession, arg: String) {
    if (session.player.pendingPerkChoices <= 0) { say("You have no perk choices banked right now."); return }
    // Every perk can be picked repeatedly (perks is a stack count, see
    // PlayerCharacter.perks' doc) -- ported from the Python prototype,
    // where every perk was stackable with no cap.
    val available = Perk.entries.toList()
    val choice = arg.toIntOrNull()
    if (choice == null || choice !in 1..available.size) {
        say("Choose a perk (type 'perk <number>'):")
        available.forEachIndexed { i, p ->
            val rank = session.player.perkRank(p)
            val rankNote = if (rank > 0) " (rank $rank)" else ""
            say("  ${i + 1}) ${p.displayName}$rankNote -- ${p.description}")
        }
        return
    }
    session.player = PerkEffects.applyPerk(session.player, available[choice - 1])
    say(AnsiText.bold("You gained the perk: ${available[choice - 1].displayName}!"))
}

private fun rest(session: GameSession) {
    session.player = session.player.copy(
        currentHealth = session.player.maxHealth,
        currentStamina = session.player.maxStamina,
        secondWindReady = true,
    )
    repeat(GameSession.RESPAWN_DELAY_TICKS) { session.advanceTick() }
    say(AnsiText.white("You rest and recover to full health and stamina. Time passes."))
}

/** True if a location has no HOSTILE being on it -- used both for the current spot (session-aware) and neighboring spots (raw world data). */
private fun isClearOfHostiles(beings: List<SpawnEntry>): Boolean = beings.none { it.disposition == Disposition.HOSTILE }

private fun sleep(session: GameSession) {
    val hereClear = isClearOfHostiles(session.currentBeings().map { it.value })
    val room = session.currentRoom()
    val neighborsClear = if (room != null) {
        room.exits.values.all { roomId -> isClearOfHostiles(session.currentSubRealm()?.rooms?.get(roomId)?.beings.orEmpty()) }
    } else {
        session.currentLocation.exits.values.all { locId -> isClearOfHostiles(session.world.locations[locId]?.beings.orEmpty()) }
    }
    if (!hereClear || !neighborsClear) {
        say(AnsiText.red("You can't risk sleeping -- there's danger too close by, here or just beyond."))
        return
    }
    session.player = session.player.copy(
        currentHealth = session.player.maxHealth,
        currentStamina = session.player.maxStamina,
        secondWindReady = true,
    )
    repeat(GameSession.RESPAWN_DELAY_TICKS) { session.advanceTick() }
    say(AnsiText.white("You find a safe spot and sleep. You wake with your health and stamina fully restored."))
    SaveManager.save(session.snapshot())
    say(AnsiText.dim("(game saved)"))
}

/** One civilian per city offers to be hired; following, fighting alongside, and a one-time revive are all handled through this. */
private fun hireCompanion(session: GameSession) {
    if (session.player.companion != null) { say("You've already got company. They'll wander off eventually."); return }
    val candidate = session.currentBeings().map { it.value }.firstOrNull { it.offersCompanionship }
    if (candidate == null) { say("No one here is looking for work."); return }
    val cost = session.currentLocation.difficultyTier * 25
    if (session.player.gold < cost) { say("${candidate.name} wants ${cost}g to travel with you -- you're short."); return }
    session.player = session.player.copy(
        gold = session.player.gold - cost,
        companion = HiredCompanion(
            name = candidate.name,
            attackBonus = candidate.stats.attackBonus,
            armorClass = candidate.stats.armorClass,
            damage = candidate.stats.damage,
            originLocationId = session.locationId,
            hiredAtMillis = Clock.System.now().toEpochMilliseconds(),
        ),
    )
    say(AnsiText.bold("${candidate.name} shoulders their gear and falls in beside you. \"Lead the way.\""))
}

private fun checkCompanionExpiry(session: GameSession) {
    val companion = session.player.companion ?: return
    if (Clock.System.now().toEpochMilliseconds() - companion.hiredAtMillis >= HiredCompanion.EMPLOYMENT_DURATION_MILLIS) {
        say(AnsiText.dim("\n${companion.name} claps you on the shoulder. \"That's my time up -- I'm heading back.\" They turn back toward ${session.world.locations[companion.originLocationId]?.name ?: "home"}."))
        session.player = session.player.copy(companion = null)
    }
}

/** Master Trader perk (+15/+25) and the Coercion Device artifact (+20, from unnoticed pain) stack, buying and selling both. */
private fun buyDiscountPercent(player: PlayerCharacter): Int =
    (if (Perk.MASTER_TRADER in player.perks) 15 else 0) + (if (ArtifactKind.COERCION_DEVICE in player.artifacts) 20 else 0)

private fun sellBonusPercent(player: PlayerCharacter): Int =
    (if (Perk.MASTER_TRADER in player.perks) 25 else 0) + (if (ArtifactKind.COERCION_DEVICE in player.artifacts) 20 else 0)

private fun openShop(session: GameSession): Pair<String, List<Item>>? {
    val trader = session.currentBeings().map { it.value }
        .firstOrNull { it.disposition == Disposition.PASSIVE && DialogueContentRegistry.archetypeFor(it.name) == eldoria.core.data.NpcArchetype.TRADER }
    if (trader == null) { say("There's no merchant here."); return null }
    val stock = ShopGenerator.inventoryFor(trader.name, session.locationId, session.currentLocation.difficultyTier, session.world.seed)
    val discount = buyDiscountPercent(session.player)
    say(AnsiText.blue("${trader.name} shows you their wares:"))
    stock.forEachIndexed { i, it -> say("  ${i + 1}) ${it.name} -- ${ShopGenerator.buyPrice(it, discount)}g") }
    say(AnsiText.dim("(buy <#> to purchase, sell <#> to sell one of your own items)"))
    return trader.name to stock
}

private fun buy(session: GameSession, arg: String, traderName: String?, stock: List<Item>) {
    val idx = arg.toIntOrNull()
    if (traderName == null || idx == null || idx !in 1..stock.size) { say("Open a shop first ('shop'), then buy <#>."); return }
    val item = stock[idx - 1]
    val price = ShopGenerator.buyPrice(item, buyDiscountPercent(session.player))
    if (session.player.gold < price) { say("You can't afford that (need ${price}g)."); return }
    session.player = session.player.copy(gold = session.player.gold - price, inventory = session.player.inventory + item)
    say(AnsiText.yellow("You buy the ${item.name} for ${price}g."))
}

private fun sell(session: GameSession, arg: String) {
    val idx = arg.toIntOrNull()
    if (idx == null || idx !in 1..session.player.inventory.size) { say("sell <#> -- check 'inventory' for numbers."); return }
    val item = session.player.inventory[idx - 1]
    val p = session.player
    // Defensive: equip() already removes an item from inventory the moment
    // it's equipped, so this shouldn't normally trigger, but was missed for
    // all 4 of Phase 1's new slots (only weapon/armor were checked) --
    // covering all six here rather than trusting that invariant elsewhere.
    if (item == p.equippedWeapon || item == p.equippedArmor || item == p.equippedOffhand || item == p.equippedHead || item == p.equippedRing || item == p.equippedAmulet) {
        say("You can't sell what you have equipped."); return
    }
    val price = ShopGenerator.sellBackPrice(item, sellBonusPercent(session.player))
    session.player = session.player.copy(gold = session.player.gold + price, inventory = session.player.inventory - item)
    say(AnsiText.yellow("You sell the ${item.name} for ${price}g."))
}

private fun travel(session: GameSession, arg: String) {
    if (arg.isBlank()) { say("Travel where? Name a city you've discovered."); return }
    val dest = session.discoveredLocations.mapNotNull { session.world.locations[it] }
        .firstOrNull { it.populationTier == PopulationTier.CITY && it.name.lowercase().contains(arg.lowercase()) }
    if (dest == null) { say("You haven't discovered a city by that name."); return }
    session.subRealmPosition = null
    session.recordOverworldDeparture(session.locationId)
    session.locationId = dest.id
    say(AnsiText.white("You make the long journey to ${dest.name}, the road blurring past in a montage of travel."))
    describeLocation(session)
}

private fun handleDeath(session: GameSession) {
    say(AnsiText.red("You have fallen..."))

    val companion = session.player.companion
    if (companion != null && !companion.reviveUsed) {
        val healed = (session.player.maxHealth * 0.4).toInt().coerceAtLeast(1)
        session.player = session.player.copy(currentHealth = healed, companion = companion.copy(reviveUsed = true))
        say(AnsiText.bold("${companion.name} hauls you back from the brink! \"Not on my watch. Not today.\""))
        say(AnsiText.dim("(${companion.name} can't do that again this employment.)"))
        return
    }
    if (Perk.SECOND_WIND in session.player.perks && session.player.secondWindReady) {
        session.player = session.player.copy(currentHealth = 1, secondWindReady = false)
        say(AnsiText.bold("Second Wind saves you at the last moment! You stand at 1 health."))
        return
    }

    val snapshot = SaveManager.load()
    if (snapshot != null) {
        session.restoreFrom(snapshot)
        say(AnsiText.red("Darkness takes you... and the world reforms around your last save."))
        say(AnsiText.dim("You wake in ${session.currentLocation.name}."))
        describeLocation(session)
        return
    }

    // No save exists yet (e.g. death before the first autosave) -- fall back to a simple respawn.
    val lostGold = session.player.gold / 2
    session.player = session.player.copy(
        currentHealth = session.player.maxHealth,
        gold = session.player.gold - lostGold,
        reputation = (session.player.reputation - 5).coerceIn(-100, 100),
    )
    session.subRealmPosition = null
    session.locationId = session.homeLocationId
    session.discover(session.homeLocationId)
    say(AnsiText.red("(No save found yet.) You wake in ${session.currentLocation.name}, having lost ${lostGold}g."))
    describeLocation(session)
}

private fun printJournal(session: GameSession) {
    say(AnsiText.bold("Journal:"))
    val mainStatus = if (MAIN_QUEST_ID in session.completedQuests) AnsiText.green("[complete]") else AnsiText.yellow("[active]")
    say("  $mainStatus Find Your Family: stolen as a child by the Kingdom's nobles, you search Eldoria for the family they tore you from.")
    if (session.finalBattleWon) {
        say("  ${AnsiText.green("[complete]")} Confront the Nobles: the throne has answered for what it did to your family.")
    } else if (session.finalBattleUnlocked) {
        say("  ${AnsiText.yellow("[active]")} Confront the Nobles: your family is safe and waiting. Type 'confront' when ready.")
    }
    val homeQuests = HomeRegionContent.questTitles.keys.filter { it in session.activeHomeRegionQuests || it in session.completedSideQuests }
    if (homeQuests.isNotEmpty()) {
        say(AnsiText.bold("Home region quests:"))
        for (id in homeQuests) {
            val status = if (id in session.completedSideQuests) AnsiText.green("[complete]") else AnsiText.yellow("[active]")
            say("  $status ${HomeRegionContent.questTitles.getValue(id)}")
        }
    }
    if (session.discoveredQuests.isEmpty()) { say("No dungeon/sky-realm quests discovered yet -- find a portal and 'enter' it."); return }
    for (id in session.discoveredQuests) {
        val realm = session.world.subRealms.getValue(id)
        val status = if (id in session.completedQuests) AnsiText.green("[complete]") else AnsiText.yellow("[active]")
        say("  $status ${realm.quest.title}: ${realm.quest.objective}")
    }
}

/** Checked after every quest-completing action: full reunion + final battle unlock once the findable family member AND every sub-realm quest are done. */
private fun checkEndgameTrigger(session: GameSession) {
    if (session.finalBattleUnlocked) return
    if (MAIN_QUEST_ID !in session.completedQuests) return
    if (!session.world.subRealms.keys.all { it in session.completedQuests }) return

    session.finalBattleUnlocked = true
    say("\n" + AnsiText.bold("*".repeat(60)))
    say(AnsiText.bold(FamilyContentRegistry.grandReunionScene))
    say("")
    say(AnsiText.bold(FamilyContentRegistry.throneCallToAction))
    say(AnsiText.bold("*".repeat(60)) + "\n")
}

/** The scripted finale: three named nobles, fought in sequence, ending in an automatic (not dice-rolled) magic finishing strike on the third. */
private fun finalBattle(session: GameSession) {
    if (!session.finalBattleUnlocked) { say("There is nothing to confront yet -- finish every quest first."); return }
    if (session.finalBattleWon) { say(AnsiText.dim("The throne has already answered for its crimes. Your story is told.")); return }

    say(AnsiText.bold("You march on the capital. Three nobles bar your way to the throne."))
    val nobles = FamilyContentRegistry.nobles
    for ((i, noble) in nobles.withIndex()) {
        if (!session.player.isAlive) return
        say(AnsiText.red("\n${noble.name}, ${noble.title}, steps forward to meet you."))
        val stats = eldoria.core.world.StatGenerator.creatureStats(5, session.rng).let {
            it.copy(maxHealth = it.maxHealth + i * 15, attackBonus = it.attackBonus + i) // each noble a little tougher than the last
        }
        var hp = stats.maxHealth
        var round = 0
        while (hp > 0 && session.player.isAlive && round < 40) {
            round++
            val playerRoll = CombatMath.attackRoll(session.rng, session.player.attackBonus)
            if (CombatMath.isHit(playerRoll, stats.armorClass)) {
                val dmg = (session.player.equippedWeapon?.damage ?: session.player.unarmedDamage).roll(session.rng).coerceAtLeast(1)
                hp -= dmg
                say("  You strike ${noble.name} for $dmg damage.")
            } else {
                say(AnsiText.dim("  You attack ${noble.name} and miss."))
            }
            if (hp <= 0) break

            val foeRoll = CombatMath.attackRoll(session.rng, stats.attackBonus)
            if (CombatMath.isHit(foeRoll, session.player.armorClass)) {
                var dmg = stats.damage.roll(session.rng).coerceAtLeast(1)
                stats.magicDamage?.let { dmg += it.roll(session.rng) }
                dmg = (dmg - (dmg * session.player.race.magicResistancePercent / 100.0).toInt()).coerceAtLeast(1)
                session.player = session.player.copy(currentHealth = session.player.currentHealth - dmg)
                say(AnsiText.red("  ${noble.name} strikes you for $dmg damage."))
            } else {
                say(AnsiText.dim("  ${noble.name} attacks and misses."))
            }
            if (!session.player.isAlive) { handleDeath(session); return }
        }

        if (i < nobles.lastIndex) {
            say(AnsiText.bold(FamilyContentRegistry.nobleFallLines[i % FamilyContentRegistry.nobleFallLines.size].replace("{name}", noble.name)))
        } else {
            // The final blow is deliberately NOT another dice roll -- see FamilyContentRegistry's doc comment.
            say(AnsiText.bold(FamilyContentRegistry.finalStrikeLines.random(session.rng).replace("{name}", noble.name)))
        }
    }

    session.finalBattleWon = true
    session.player = session.player.copy(reputation = 100)
    say("\n" + AnsiText.bold(FamilyContentRegistry.victoryEpilogue))
}

private fun printCodex(session: GameSession) {
    if (session.bestiary.isEmpty()) { say("You haven't encountered anyone or anything yet."); return }
    say(AnsiText.bold("Bestiary/Codex (${session.bestiary.size} encountered):"))
    for (n in session.bestiary.sorted()) say("  - $n")
}

private val PIRATE_SHIP_NAMES = listOf("The Black Gull", "Crimson Tide Raider", "The Drowned Fang", "Widow's Wake")
private const val BIG_KAHOONA_NAME = "Big Kahoon-a"

private fun grantGillsFromBigKahoona(session: GameSession) {
    if (session.player.hasGills) return
    session.player = session.player.copy(hasGills = true, defeatedBigKahoona = true)
    say(AnsiText.bold("\nAs the $BIG_KAHOONA_NAME sinks back into the deep, something changes in you -- your neck stings, and when you touch it you feel slits there that weren't there before. Gills."))
    say(AnsiText.bold("You can breathe underwater now. Every river and every sea in the Kingdom is open to you, boat or no boat."))
}

private fun isSeaPort(session: GameSession): Boolean =
    session.currentLocation.biome == Biome.SEA && session.currentLocation.populationTier != PopulationTier.WILDERNESS

private fun buyBoat(session: GameSession) {
    if (!isSeaPort(session)) { say("You need to be at a coastal settlement to buy a boat."); return }
    if (session.player.ownedBoat != null) { say("You already own a boat. Sell it to the shipwright before buying another (not yet supported -- just keep it)."); return }
    val boat = BoatGenerator.buy(session.rng)
    if (session.player.gold < boat.value) { say("The shipwright offers you the ${boat.name} for ${boat.value}g -- you can't afford it yet."); return }
    session.player = session.player.copy(gold = session.player.gold - boat.value, ownedBoat = boat)
    say(AnsiText.bold("You buy the ${boat.name} for ${boat.value}g. She's yours now -- try not to sink her."))
}

private fun boatStatus(session: GameSession) {
    val boat = session.player.ownedBoat ?: run { say("You don't own a boat. Buy one at a coastal settlement ('buy boat')."); return }
    val cannonNote = if (boat.hasCannons) AnsiText.yellow(" [cannons fitted]") else ""
    say("${AnsiText.bold(boat.name)}$cannonNote: ${boat.currentDurability}/${boat.maxDurability} hull integrity${if (boat.isBroken) AnsiText.red(" -- WRECKED, needs repair") else ""}")
}

private const val CANNON_COST = 150

private fun buyCannons(session: GameSession) {
    val boat = session.player.ownedBoat ?: run { say("You need a boat before you can fit cannons to it."); return }
    if (!isSeaPort(session)) { say("You need to be at a coastal settlement to have cannons fitted."); return }
    if (boat.hasCannons) { say("The ${boat.name} already has cannons fitted."); return }
    if (session.player.gold < CANNON_COST) { say("The shipwright wants ${CANNON_COST}g to fit cannons -- you're short."); return }
    session.player = session.player.copy(gold = session.player.gold - CANNON_COST, ownedBoat = boat.copy(hasCannons = true))
    say(AnsiText.bold("A pair of iron cannons are bolted to the ${boat.name}'s hull. Sea monsters beware."))
}

private fun repairBoat(session: GameSession) {
    val boat = session.player.ownedBoat ?: run { say("You don't own a boat."); return }
    if (!isSeaPort(session)) { say("You need to be at a coastal settlement to find a shipwright."); return }
    if (boat.currentDurability >= boat.maxDurability) { say("Your boat is already in full repair."); return }
    val cost = BoatGenerator.repairCost(boat)
    if (session.player.gold < cost) { say("Repairs would cost ${cost}g -- you can't afford that yet."); return }
    session.player = session.player.copy(gold = session.player.gold - cost, ownedBoat = boat.repaired())
    say(AnsiText.yellow("The shipwright patches up the ${boat.name} for ${cost}g. Good as new."))
}

/** Sailing is its own fast-travel network, separate from walking-based discovery: any Sea settlement can be sailed to directly, discovered or not, but the open sea carries a real risk of pirates or worse. */
private fun sail(session: GameSession, arg: String) {
    if (!isSeaPort(session)) { say("You need to be at a coastal settlement to set sail."); return }
    val boat = session.player.ownedBoat ?: run { say("You don't own a boat. Buy one here first ('buy boat')."); return }
    if (boat.isBroken) { say("Your boat is wrecked and needs repairs before it can sail."); return }
    if (arg.isBlank()) { say("Sail where? Name a Sea settlement."); return }
    val dest = session.world.locations.values.firstOrNull {
        it.biome == Biome.SEA && it.populationTier != PopulationTier.WILDERNESS && it.name.lowercase().contains(arg.lowercase())
    }
    if (dest == null) { say("No such Sea settlement is known."); return }
    if (dest.id == session.locationId) { say("You're already there."); return }

    say(AnsiText.white("You cast off aboard the ${boat.name}, bound for ${dest.name}."))
    session.player = session.player.copy(ownedBoat = boat.worn((1..3).random(session.rng)))

    if (session.rng.nextInt(100) < 40) {
        val isBigKahoona = session.rng.nextInt(100) < 5
        val tier = if (isBigKahoona) 5 else (2..5).random(session.rng)
        val isPirate = !isBigKahoona && session.rng.nextBoolean()
        val foeName = when {
            isBigKahoona -> BIG_KAHOONA_NAME
            isPirate -> PIRATE_SHIP_NAMES.random(session.rng)
            else -> BiomeContentRegistry[Biome.SEA].creaturesFor(tier).filter { it.disposition == Disposition.HOSTILE }.random(session.rng).name
        }
        if (isBigKahoona) {
            say(AnsiText.bold("\nThe water churns and boils, and something impossibly vast rises from beneath -- the $BIG_KAHOONA_NAME, a squid the size of a ship, has found you!"))
        } else {
            say(AnsiText.red("A $foeName rises out of the waves ahead!"))
        }
        val stats = eldoria.core.world.StatGenerator.creatureStats(tier, session.rng).let {
            if (isBigKahoona) it.copy(maxHealth = it.maxHealth * 2, attackBonus = it.attackBonus + 2) else it
        }
        val outcome = shipEncounter(session, foeName, stats)
        if (outcome == ShipOutcome.BOAT_LOST) {
            say(AnsiText.red("The ${boat.name} breaks apart beneath you! You swim for it, washing up battered at ${dest.name}, your boat lost to the deep."))
            session.player = session.player.copy(ownedBoat = null, currentHealth = (session.player.maxHealth / 3).coerceAtLeast(1))
        } else if (outcome == ShipOutcome.PLAYER_DOWN) {
            return // handleDeath() runs in the main loop right after this call returns
        } else {
            say(AnsiText.bold("You drive off the $foeName and continue on to ${dest.name}."))
            if (isBigKahoona) grantGillsFromBigKahoona(session)
        }
    }

    if (session.player.isAlive) {
        session.locationId = dest.id
        session.discover(dest.id)
        say(AnsiText.white("You make port at ${dest.name}."))
        describeLocation(session)
    }
}

/** After a successful overworld move, a small chance a fisherman passes by near water and offers a lift -- only worth anything once the player actually owns a boat. */
private fun maybeFerryEncounter(session: GameSession, dest: GameLocation) {
    if (session.inSubRealm || session.player.ownedBoat == null || session.ferrymanAvailable) return
    val neighborTerrains = listOfNotNull(
        session.world.locationAt(dest.x, dest.y - 1)?.terrain,
        session.world.locationAt(dest.x, dest.y + 1)?.terrain,
        session.world.locationAt(dest.x - 1, dest.y)?.terrain,
        session.world.locationAt(dest.x + 1, dest.y)?.terrain,
    )
    val nearWater = dest.terrain != TerrainKind.LAND || neighborTerrains.any { it != TerrainKind.LAND }
    if (!nearWater) return
    if (session.rng.nextInt(100) >= 12) return

    session.ferrymanAvailable = true
    say(
        AnsiText.cyan(
            "\nA weathered fisherman poles a small skiff past, and slows when he spots you. " +
                "\"Rough way to travel, on foot. I can run you to port, for a coin or a favor.\" (type 'ferry' or 'ferry favor')"
        )
    )
}

private fun acceptFerry(session: GameSession, arg: String) {
    if (!session.ferrymanAvailable) { say("There's no ferryman here right now."); return }
    val dest = session.world.locations.values
        .filter { it.biome == Biome.SEA && it.populationTier != PopulationTier.WILDERNESS }
        .minByOrNull { kotlin.math.abs(it.x - session.currentLocation.x) + kotlin.math.abs(it.y - session.currentLocation.y) }
    if (dest == null) { say("The fisherman scratches his head. \"Truth told, I don't rightly know a port from here.\""); return }

    if (arg.equals("favor", ignoreCase = true)) {
        val material = session.player.materials.entries.firstOrNull { it.value > 0 }
        if (material == null) { say("\"A favor, you said? You've nothing on you worth my while.\""); return }
        session.player = session.player.copy(materials = session.player.materials + (material.key to material.value - 1))
        say(AnsiText.cyan("You hand over ${material.key} in trade. \"Fair enough. Climb aboard.\""))
    } else {
        val fee = (10..25).random(session.rng)
        if (session.player.gold < fee) { say("The fisherman wants ${fee}g -- you're short. Try 'ferry favor' instead if you've goods to trade."); return }
        session.player = session.player.copy(gold = session.player.gold - fee)
        say(AnsiText.cyan("You pay ${fee}g. \"Climb aboard, then.\""))
    }

    session.ferrymanAvailable = false
    session.subRealmPosition = null
    session.recordOverworldDeparture(session.locationId)
    session.locationId = dest.id
    session.discover(dest.id)
    say(AnsiText.white("The skiff cuts across the water and puts you ashore at ${dest.name}."))
    describeLocation(session)
}

/** A wandering aeronaut, found by luck in any village in any biome -- unlike 'travel', he'll take you anywhere, discovered or not. */
private fun maybeBalloonEncounter(session: GameSession, dest: GameLocation) {
    if (session.inSubRealm || dest.populationTier != PopulationTier.COUNTRYSIDE || session.balloonManAvailable) return
    if (session.rng.nextInt(100) >= 8) return

    session.balloonManAvailable = true
    say(
        AnsiText.cyan(
            "\nA patched, colorful hot air balloon drifts low and settles just outside the village. A weathered " +
                "aeronaut leans over the basket's edge. \"Fancy a ride? I've been everywhere in the Kingdom -- I can " +
                "set you down anywhere you like, whether you've laid eyes on it yet or not.\" (type 'ride <city name>')"
        )
    )
}

private fun rideBalloon(session: GameSession, arg: String) {
    if (!session.balloonManAvailable) { say("There's no balloon here right now."); return }
    if (arg.isBlank()) { say("Ride where? Name any city in the Kingdom."); return }
    val dest = session.world.locations.values.firstOrNull { it.populationTier == PopulationTier.CITY && it.name.lowercase().contains(arg.lowercase()) }
    if (dest == null) { say("\"Never heard of the place,\" the aeronaut says. \"Name a real city.\""); return }

    session.balloonManAvailable = false
    session.subRealmPosition = null
    session.recordOverworldDeparture(session.locationId)
    session.locationId = dest.id
    session.discover(dest.id)
    say(AnsiText.white("You climb into the basket. The village shrinks away below as the balloon sails across the Kingdom, and sets down gently in ${dest.name}."))
    describeLocation(session)
}

private enum class ShipOutcome { CONTINUE, BOAT_LOST, PLAYER_DOWN }

/** Combat at sea: each enemy hit has a chance to wound the boat instead of the sailor -- either can bring the voyage to an early end. */
private fun shipEncounter(session: GameSession, foeName: String, foeStats: StatBlock): ShipOutcome {
    var foeHp = foeStats.maxHealth
    var round = 0
    while (foeHp > 0 && session.player.isAlive && round < 30) {
        round++
        val playerRoll = CombatMath.attackRoll(session.rng, session.player.attackBonus)
        if (CombatMath.isHit(playerRoll, foeStats.armorClass)) {
            val dmg = (session.player.equippedWeapon?.damage ?: session.player.unarmedDamage).roll(session.rng).coerceAtLeast(1)
            foeHp -= dmg
            say("  You strike the $foeName for $dmg damage.")
        } else {
            say(AnsiText.dim("  You attack the $foeName and miss."))
        }
        if (foeHp <= 0) break

        if (session.player.ownedBoat?.hasCannons == true) {
            val cannonDmg = DiceFormula(2, DieType.D10, 0).roll(session.rng)
            foeHp -= cannonDmg
            say(AnsiText.yellow("  Your cannons roar! $cannonDmg damage to the $foeName."))
            if (foeHp <= 0) break
        }

        val foeRoll = CombatMath.attackRoll(session.rng, foeStats.attackBonus)
        val hitsBoat = session.player.ownedBoat != null && session.rng.nextBoolean()
        if (hitsBoat) {
            val dmg = foeStats.damage.roll(session.rng).coerceAtLeast(1)
            val boat = session.player.ownedBoat!!.worn(dmg)
            session.player = session.player.copy(ownedBoat = boat)
            say(AnsiText.red("  The $foeName slams into your hull for $dmg damage! (${boat.currentDurability}/${boat.maxDurability} hull left)"))
            if (boat.isBroken) return ShipOutcome.BOAT_LOST
        } else if (CombatMath.isHit(foeRoll, session.player.armorClass)) {
            var dmg = foeStats.damage.roll(session.rng).coerceAtLeast(1)
            val resisted = (dmg * session.player.race.magicResistancePercent / 100.0).toInt()
            dmg = (dmg - resisted).coerceAtLeast(1)
            session.player = session.player.copy(currentHealth = session.player.currentHealth - dmg)
            say(AnsiText.red("  The $foeName strikes you for $dmg damage."))
        } else {
            say(AnsiText.dim("  The $foeName attacks and misses."))
        }
    }
    if (!session.player.isAlive) {
        handleDeath(session)
        return ShipOutcome.PLAYER_DOWN
    }
    if (foeHp <= 0) {
        session.recordSeen(foeName)
        val xp = LevelProgression.xpForDefeating(4, session.rng)
        session.player = LevelProgression.applyExperience(session.player, xp, session.rng)
        say("You gain $xp experience.")
    }
    return ShipOutcome.CONTINUE
}
