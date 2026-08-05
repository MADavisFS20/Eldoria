package eldoria.core

import eldoria.core.model.Biome
import eldoria.core.model.CharacterClass
import eldoria.core.model.Disposition
import eldoria.core.model.PopulationTier
import eldoria.core.model.QuestType
import eldoria.core.model.Race
import eldoria.core.model.RealmKind
import eldoria.core.model.SkillType
import eldoria.core.model.TerrainKind
import eldoria.core.world.CombatMath
import eldoria.core.world.LevelProgression
import eldoria.core.world.PlayerCharacterFactory
import eldoria.core.world.SkillProgression
import eldoria.core.world.StatGenerator
import eldoria.core.world.WorldConfig
import eldoria.core.world.WorldGenerator
import kotlin.random.Random

fun main() {
    val world = WorldGenerator.generate(WorldConfig())
    val locations = world.locations.values

    println("=== ELDORIA WORLD GENERATION REPORT ===")
    println("Grid: ${world.width} x ${world.height} = ${world.width * world.height} tiles")
    println("Total locations generated: ${locations.size}")
    println()

    println("--- Per biome ---")
    for (biome in Biome.entries) {
        val inBiome = locations.filter { it.biome == biome }
        val cities = inBiome.count { it.populationTier == PopulationTier.CITY }
        val countryside = inBiome.count { it.populationTier == PopulationTier.COUNTRYSIDE }
        val wilderness = inBiome.count { it.populationTier == PopulationTier.WILDERNESS }
        val tiers = inBiome.map { it.difficultyTier }
        val ok = cities in 1..2 && countryside >= cities * 2
        println(
            "${biome.displayName.padEnd(10)} total=${inBiome.size.toString().padStart(5)}  " +
                "cities=$cities  countryside=$countryside  wilderness=$wilderness  " +
                "difficultyTiers=${tiers.min()}..${tiers.max()}  " +
                "[population rule ${if (ok) "OK" else "FAIL"}]"
        )
    }
    println()

    println("--- Wilderness emptiness (open, walkable country with nothing in it) ---")
    val wildernessLocs = locations.filter { it.populationTier == PopulationTier.WILDERNESS && it.portalId == null }
    val emptyWilderness = wildernessLocs.count { it.beings.isEmpty() }
    println(
        "wilderness tiles=${wildernessLocs.size}  empty=${emptyWilderness}  " +
            "(${"%.1f".format(100.0 * emptyWilderness / wildernessLocs.size)}% empty)"
    )
    println()

    println("--- Hostile vs passive beings (overworld) ---")
    val allBeings = locations.flatMap { it.beings }
    val hostile = allBeings.count { it.disposition == Disposition.HOSTILE }
    val passive = allBeings.count { it.disposition == Disposition.PASSIVE }
    println("Total beings placed: ${allBeings.size}  hostile=$hostile  passive=$passive")
    println()

    println("--- QA pass: description length (<=5 sentences) ---")
    fun sentenceCount(s: String): Int = s.count { it == '.' || it == '!' || it == '?' }.coerceAtLeast(1)
    val overworldViolations = locations.filter { sentenceCount(it.description) > 5 }
    val roomViolations = world.subRealms.values.flatMap { it.rooms.values }.filter { sentenceCount(it.description) > 5 }
    val questViolations = world.subRealms.values.map { it.quest }.filter { sentenceCount(it.objective) > 5 }
    val maxOverworld = locations.maxOf { sentenceCount(it.description) }
    val maxRoom = world.subRealms.values.flatMap { it.rooms.values }.maxOf { sentenceCount(it.description) }
    val maxQuest = world.subRealms.values.maxOf { sentenceCount(it.quest.objective) }
    println(
        "Longest overworld description: $maxOverworld sentence(s)   Longest sub-realm room: $maxRoom sentence(s)   " +
            "Longest quest objective: $maxQuest sentence(s)   " +
            "[${if (overworldViolations.isEmpty() && roomViolations.isEmpty() && questViolations.isEmpty()) "OK, all within limit" else "FAIL: ${overworldViolations.size + roomViolations.size + questViolations.size} over limit"}]"
    )
    println()

    println("--- QA pass: tile movement integrity ---")
    val danglingExits = locations.flatMap { loc -> loc.exits.entries.filter { it.value !in world.locations } }
    val reciprocalOpposite = mapOf("north" to "south", "south" to "north", "east" to "west", "west" to "east")
    var reciprocalBreaks = 0
    for (loc in locations) {
        for ((dir, destId) in loc.exits) {
            val opp = reciprocalOpposite[dir] ?: continue
            val dest = world.locations[destId] ?: continue
            if (dest.exits[opp] != loc.id) reciprocalBreaks++
        }
    }
    println("Dangling exits (pointing nowhere): ${danglingExits.size}   Non-reciprocal overworld exits: $reciprocalBreaks   [${if (danglingExits.isEmpty() && reciprocalBreaks == 0) "OK" else "FAIL"}]")

    fun reachableRoomCount(realm: eldoria.core.model.SubRealm): Int {
        val seen = mutableSetOf(realm.entryRoomId)
        val queue = ArrayDeque(listOf(realm.entryRoomId))
        while (queue.isNotEmpty()) {
            val cur = queue.removeFirst()
            for (dest in realm.rooms.getValue(cur).exits.values) if (seen.add(dest)) queue.addLast(dest)
        }
        return seen.size
    }
    val disconnectedRealms = world.subRealms.values.filter { reachableRoomCount(it) != it.rooms.size }
    val bossUnreachable = world.subRealms.values.filter { it.bossRoomId !in run { val s = mutableSetOf(it.entryRoomId); val q = ArrayDeque(listOf(it.entryRoomId)); while (q.isNotEmpty()) { val c = q.removeFirst(); for (d in it.rooms.getValue(c).exits.values) if (s.add(d)) q.addLast(d) }; s } }
    println("Sub-realms with unreachable rooms: ${disconnectedRealms.size}   Sub-realms with unreachable boss room: ${bossUnreachable.size}   [${if (disconnectedRealms.isEmpty() && bossUnreachable.isEmpty()) "OK" else "FAIL"}]")

    val questsMissingRewardsInBossRoom = world.subRealms.values.filter { realm ->
        val bossItems = realm.rooms.getValue(realm.bossRoomId).items
        realm.quest.legendaryItem !in bossItems || realm.quest.questItem !in bossItems
    }
    val rescueQuestsMissingCaptive = world.subRealms.values.filter { realm ->
        realm.quest.type == QuestType.RESCUE_CAPTIVE && realm.rooms.getValue(realm.bossRoomId).beings.none { it.kind == eldoria.core.model.SpawnKind.NPC }
    }
    println("Quests missing reward items in boss room: ${questsMissingRewardsInBossRoom.size}   Rescue quests missing their captive: ${rescueQuestsMissingCaptive.size}   [${if (questsMissingRewardsInBossRoom.isEmpty() && rescueQuestsMissingCaptive.isEmpty()) "OK" else "FAIL"}]")
    println()

    println("--- Sub-realms (dungeons + sky realms) ---")
    val dungeons = world.subRealms.values.filter { it.kind == RealmKind.DUNGEON }
    val skyRealms = world.subRealms.values.filter { it.kind == RealmKind.SKY_REALM }
    println("Dungeons: ${dungeons.size}   Sky realms: ${skyRealms.size}   Total rooms: ${world.subRealms.values.sumOf { it.rooms.size }}")
    val realmNames = world.subRealms.values.map { it.name }
    val legendaryNames = world.subRealms.values.map { it.quest.legendaryItem.name }
    println("All sub-realm names unique: ${realmNames.size == realmNames.toSet().size}   All legendary item names unique: ${legendaryNames.size == legendaryNames.toSet().size}")
    println()

    println("--- Sample dungeon ---")
    val sampleDungeon = dungeons.first()
    println("${sampleDungeon.name}  (biome=${sampleDungeon.biome.displayName}, rooms=${sampleDungeon.rooms.size})")
    println("Quest [${sampleDungeon.quest.type}]: ${sampleDungeon.quest.objective}")
    val li = sampleDungeon.quest.legendaryItem
    println("Reward: ${li.name} [${li.kind}] dmg=${li.damage} acBonus=${li.armorClassBonus} value=${li.value}g durability=${li.maxDurability} magic=${li.magicEffect}")
    val qi = sampleDungeon.quest.questItem
    println("Quest item: ${qi.name} value=${qi.value}g")
    val bossRoom = sampleDungeon.rooms.getValue(sampleDungeon.bossRoomId)
    println("Boss room: ${bossRoom.name} [tier ${bossRoom.difficultyTier}]")
    val boss = bossRoom.beings.first()
    val bs = boss.stats
    println(
        "  Boss ${boss.name}: STR=${bs.strength} AGI=${bs.agility} WIL=${bs.willpower} " +
            "HP=${bs.maxHealth} AC=${bs.armorClass} SPD=${bs.speed} atk=+${bs.attackBonus} dmg=${bs.damage} " +
            "magicDmg=${bs.magicDamage} magicEffect=${bs.magicEffect} worth=${bs.worth}g"
    )
    println()

    println("--- Sample sky realm ---")
    val sampleSky = skyRealms.first()
    println("${sampleSky.name}  (origin biome=${sampleSky.biome.displayName}, rooms=${sampleSky.rooms.size})")
    println("Quest [${sampleSky.quest.type}]: ${sampleSky.quest.objective}")
    val skyLi = sampleSky.quest.legendaryItem
    println("Reward: ${skyLi.name} [${skyLi.kind}] dmg=${skyLi.damage} acBonus=${skyLi.armorClassBonus} value=${skyLi.value}g durability=${skyLi.maxDurability} magic=${skyLi.magicEffect}")
    println()

    println("--- Quest type variety across all sub-realms ---")
    val questTypeCounts = world.subRealms.values.groupingBy { it.quest.type }.eachCount()
    for (t in QuestType.entries) println("  $t: ${questTypeCounts[t] ?: 0}")
    println()

    println("--- Dice-driven stat scaling sanity check (same creature slot, tier 1 vs tier 5) ---")
    val demoRng = Random(99)
    val tier1 = StatGenerator.creatureStats(1, demoRng)
    val tier5 = StatGenerator.creatureStats(5, demoRng)
    println("Tier 1: HP=${tier1.maxHealth} AC=${tier1.armorClass} dmg=${tier1.damage} (avg ${"%.1f".format(tier1.damage.average())}) worth=${tier1.worth}g magic=${tier1.magicDamage != null}")
    println("Tier 5: HP=${tier5.maxHealth} AC=${tier5.armorClass} dmg=${tier5.damage} (avg ${"%.1f".format(tier5.damage.average())}) worth=${tier5.worth}g magic=${tier5.magicDamage != null}")
    println()

    println("--- Core resolution mechanic demo: d20 + attackBonus vs target AC ---")
    repeat(5) {
        val roll = CombatMath.attackRoll(demoRng, tier1.attackBonus)
        println("  attacker (atk+${tier1.attackBonus}) rolls d20 -> $roll vs defender AC ${tier5.armorClass}: ${if (CombatMath.isHit(roll, tier5.armorClass)) "HIT" else "miss"}")
    }
    println()

    fun signed(n: Int): String = if (n >= 0) "+$n" else "$n"

    println("--- Character creation: one of each race/class pairing ---")
    val charRng = Random(2024)
    val nordWarrior = PlayerCharacterFactory.create("Bjorn", Race.NORD, CharacterClass.WARRIOR, charRng)
    val elfMage = PlayerCharacterFactory.create("Sylvaeril", Race.ELF, CharacterClass.MAGE, charRng)
    val orcRogue = PlayerCharacterFactory.create("Grosh", Race.ORC, CharacterClass.ROGUE, charRng)
    for (pc in listOf(nordWarrior, elfMage, orcRogue)) {
        println(
            "${pc.name} the ${pc.race.displayName} ${pc.characterClass.displayName} " +
                "(Lv${pc.level})  STR=${pc.strength} AGI=${pc.agility} WIL=${pc.willpower}  " +
                "HP=${pc.maxHealth} AC=${pc.armorClass} SPD=${pc.speed} atk=${signed(pc.attackBonus)}  gold=${pc.gold}g"
        )
        println("  Wielding ${pc.equippedWeapon?.name} (${pc.equippedWeapon?.damage})  Wearing ${pc.equippedArmor?.name} (+${pc.equippedArmor?.armorClassBonus} AC)")
        val topSkills = pc.skills.values.sortedByDescending { it.level }.take(4)
        println("  Starting skills: " + topSkills.joinToString(", ") { "${it.type.displayName} ${it.level}" })
    }
    println()

    println("--- Skill leveling from use (Skyrim-style, independent of character level) ---")
    var trainee = nordWarrior
    val trained = SkillType.ONE_HANDED
    println("${trainee.name}'s ${trained.displayName}: starts at ${trainee.skillLevel(trained)}")
    repeat(40) { trainee = SkillProgression.gainSkillUse(trainee, trained, charRng) }
    println("  after 40 uses -> ${trainee.skillLevel(trained)}")
    println()

    println("--- Learning a trainer-locked skill (magic/crafting can't be self-taught) ---")
    println("${elfMage.name} knows Restoration before training: ${elfMage.knowsSkill(SkillType.RESTORATION)}")
    val trainedMage = SkillProgression.learnSkillFromTrainer(elfMage, SkillType.RESTORATION)
    println("  after visiting Sister Wren -> knows it now, starting level ${trainedMage.skillLevel(SkillType.RESTORATION)}")
    println()

    println("--- Character-level progression from combat xp (separate track from skills) ---")
    var fighter = nordWarrior
    var totalXp = 0
    var kills = 0
    while (fighter.level < 10) {
        val tierFought = (1..3).random(charRng)
        val xp = LevelProgression.xpForDefeating(tierFought, charRng)
        totalXp += xp
        kills++
        fighter = LevelProgression.applyExperience(fighter, xp, charRng)
    }
    println(
        "${fighter.name} reached Lv${fighter.level} after $kills kills ($totalXp total xp).  " +
            "STR ${nordWarrior.strength}->${fighter.strength}  HP ${nordWarrior.maxHealth}->${fighter.maxHealth}  " +
            "AC ${nordWarrior.armorClass}->${fighter.armorClass}  atk ${signed(nordWarrior.attackBonus)}->${signed(fighter.attackBonus)}"
    )
    println("xp needed per level is escalating: L1->L2 needs ${LevelProgression.xpToNextLevel(1)}, L10->L11 needs ${LevelProgression.xpToNextLevel(10)}, L30->L31 needs ${LevelProgression.xpToNextLevel(30)}")
    println()

    println("--- QA pass: waterways (rivers/bridges/sea) ---")
    val waterway = locations.filter { it.terrain == TerrainKind.WATERWAY }
    val bridges = locations.filter { it.terrain == TerrainKind.BRIDGE }
    val riverWaterway = waterway.filter { it.biome != Biome.SEA }
    val riverBridges = bridges.filter { it.biome != Biome.SEA }
    val seaWaterway = waterway.filter { it.biome == Biome.SEA }
    println("River waterway tiles: ${riverWaterway.size}   River bridges: ${riverBridges.size}   Sea open-water tiles: ${seaWaterway.size}")
    val riverBiomesCrossed = riverWaterway.map { it.biome }.toSet()
    val bridgesPresent = riverBridges.isNotEmpty()
    println("River crosses biomes: ${riverBiomesCrossed.map { it.displayName }}   [${if (riverBiomesCrossed.size >= 3 && bridgesPresent) "OK" else "FAIL"}]")
    val treasureNames = setOf("Sunken Treasure Chest", "Barnacled Strongbox", "Corsair's Buried Hoard")
    val treasures = locations.filter { loc -> loc.items.any { it.name in treasureNames } }
    println("Sunken treasures placed: ${treasures.size}  (all on Sea open water: ${treasures.all { it.biome == Biome.SEA && it.terrain == TerrainKind.WATERWAY }})   [${if (treasures.size == 3) "OK" else "FAIL"}]")
    // Every settlement/portal must still be dry land -- otherwise the earlier
    // waterway pass would have swallowed a town or a dungeon mouth.
    val wetSettlements = locations.filter { it.populationTier != PopulationTier.WILDERNESS && it.terrain != TerrainKind.LAND }
    val wetPortals = locations.filter { it.portalId != null && it.terrain != TerrainKind.LAND }
    println("Settlements/portals accidentally underwater: ${wetSettlements.size + wetPortals.size}   [${if (wetSettlements.isEmpty() && wetPortals.isEmpty()) "OK" else "FAIL"}]")
    println()

    println("--- QA pass: per-biome environmental hazards ---")
    val hazardTiles = locations.filter { it.hazard != null }
    val hazardsByBiome = hazardTiles.groupBy { it.biome }
    val allBiomesHaveHazards = Biome.entries.all { hazardsByBiome[it].orEmpty().isNotEmpty() }
    val hazardsOnSettlementsOrPortals = hazardTiles.count { it.populationTier != PopulationTier.WILDERNESS || it.portalId != null }
    println(
        "Hazard tiles: ${hazardTiles.size} across ${hazardsByBiome.size}/6 biomes " +
            "[${if (allBiomesHaveHazards) "OK" else "FAIL"}]   On a settlement/portal: $hazardsOnSettlementsOrPortals [${if (hazardsOnSettlementsOrPortals == 0) "OK" else "FAIL"}]"
    )
    println()

    println("--- QA pass: side quests ---")
    val sideQuestGivers = locations.flatMap { loc -> loc.beings.filter { it.offersSideQuest != null }.map { loc to it } }
    val sideQuestsFound = sideQuestGivers.map { it.second.offersSideQuest }.toSet()
    val duplicates = sideQuestGivers.groupBy { it.second.offersSideQuest }.filter { it.value.size > 1 }
    println(
        "Side quest givers placed: ${sideQuestGivers.size}   Distinct quests: ${sideQuestsFound.size}/${eldoria.core.model.SideQuestKind.entries.size}   " +
            "Duplicated quests: ${duplicates.size}   [${if (sideQuestsFound.size == eldoria.core.model.SideQuestKind.entries.size && duplicates.isEmpty()) "OK" else "FAIL"}]"
    )
    val questsPerCity = sideQuestGivers.groupBy { it.first.name }.mapValues { it.value.size }
    println("Quests per city: " + questsPerCity.entries.joinToString(", ") { "${it.key}=${it.value}" })
    println()

    println("--- QA pass: hireable companions ---")
    val cities = locations.filter { it.populationTier == PopulationTier.CITY }
    val citiesWithCompanion = cities.count { it.beings.any { b -> b.offersCompanionship } }
    println("Cities: ${cities.size}   Cities with a hireable companion: $citiesWithCompanion   [${if (citiesWithCompanion == cities.size) "OK" else "FAIL"}]")
    println()

    println("--- QA pass: hidden sci-fi artifacts ---")
    val artifactTiles = locations.filter { loc -> loc.items.any { item -> eldoria.core.model.ArtifactKind.entries.any { it.itemName == item.name } } }
    val foundKinds = artifactTiles.flatMap { it.items }.mapNotNull { item -> eldoria.core.model.ArtifactKind.entries.find { it.itemName == item.name } }.toSet()
    for (loc in artifactTiles) println("  ${loc.items.first().name} hidden at ${loc.name} (${loc.biome.displayName}, ${loc.id})")
    println("Artifacts placed: ${artifactTiles.size}/3   All 3 kinds present: ${foundKinds.size == 3}   [${if (artifactTiles.size == 3 && foundKinds.size == 3) "OK" else "FAIL"}]")
    println()

    println("--- QA pass: subclass curse-givers + Mad Scientist ---")
    val subclassGivers = locations.flatMap { loc -> loc.beings.filter { it.offersSubclass != null }.map { loc to it } }
    val vampireGivers = subclassGivers.filter { it.second.offersSubclass == eldoria.core.model.Subclass.VAMPIRE }
    val werewolfGivers = subclassGivers.filter { it.second.offersSubclass == eldoria.core.model.Subclass.WEREWOLF }
    println("Vampire givers: ${vampireGivers.size} ${vampireGivers.firstOrNull()?.let { "(${it.second.name} at ${it.first.name})" } ?: ""}   [${if (vampireGivers.size == 1) "OK" else "FAIL"}]")
    println("Werewolf givers: ${werewolfGivers.size} ${werewolfGivers.firstOrNull()?.let { "(${it.second.name} at ${it.first.name})" } ?: ""}   [${if (werewolfGivers.size == 1) "OK" else "FAIL"}]")
    val scientists = locations.flatMap { loc -> loc.beings.filter { it.offersBionicUpgrade }.map { loc to it } }
    println("Mad Scientists: ${scientists.size} ${scientists.firstOrNull()?.let { "(${it.second.name} at ${it.first.name})" } ?: ""}   [${if (scientists.size == 1) "OK" else "FAIL"}]")
    println()

    println("--- QA pass: main-quest family member ---")
    val familyMembers = locations.flatMap { loc -> loc.beings.filter { it.isFamilyMember }.map { loc to it } }
    if (familyMembers.size == 1) {
        val (loc, being) = familyMembers.first()
        println("OK: exactly one family member placed -- ${being.name} at ${loc.name} (${loc.biome.displayName}, ${loc.id})")
    } else {
        println("FAIL: expected exactly 1 family member in the world, found ${familyMembers.size}")
    }
    println()

    println("--- Trainer NPC coverage: every trainer-locked skill must be reachable somewhere in the world ---")
    val trainerNpcs = locations.flatMap { it.beings }.filter { it.teachesSkill != null }
    val taughtSkills = trainerNpcs.map { it.teachesSkill }.toSet()
    val missing = SkillType.trainerLockedSkills.filterNot { it in taughtSkills }
    println("Trainer NPCs placed: ${trainerNpcs.size}   Distinct skills taught: ${taughtSkills.size}/${SkillType.trainerLockedSkills.size}   [${if (missing.isEmpty()) "OK, all reachable" else "FAIL missing $missing"}]")
    for (t in trainerNpcs) println("  ${t.name} teaches ${t.teachesSkill?.displayName}")
}
