package eldoria.core.data

import eldoria.core.model.Biome

/** All hardcoded flavor content for one dungeon (per-biome) or sky-realm variant. */
data class SubRealmTheme(
    val label: String,
    val realmNames: List<String>,
    val roomAdjectives: List<String>,
    val roomFeatures: List<String>,
    val creatures: List<CreatureTemplate>,
    val bossCreatures: List<String>,
    val weaponBases: List<String>,
    val armorBases: List<String>,
    val itemPrefixes: List<String>,
    val questItemNames: List<String>,
    val captiveNames: List<String>,
) {
    fun creaturesFor(tier: Int) = creatures.filter { tier in it.minTier..it.maxTier }
}

object DungeonContentRegistry {
    private val MOUNTAINS = SubRealmTheme(
        label = "Deep Mines",
        realmNames = listOf("Ironvein Depths", "Skyreach Undermines", "The Hollow Shaft"),
        roomAdjectives = listOf("Dust-choked", "Echoing", "Torch-lit", "Collapsed", "Gem-veined", "Cold", "Rubble-strewn"),
        roomFeatures = listOf("Tunnel", "Mineshaft", "Cavern", "Forge Ruin", "Crystal Chamber", "Collapsed Gallery", "Underground Lake", "Ore Vein Hall"),
        creatures = listOf(
            CreatureTemplate("Bat Swarm", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Lost Prospector", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Kobold Miner", eldoria.core.model.Disposition.HOSTILE, 1, 3, packSize = 2..3),
            CreatureTemplate("Cave Troll", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Rock Wight", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Deep Spider", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Gem Golem", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Ironvein Colossus", "Grask, Warden of the Deep", "The Sunken Forge-Wraith"),
        weaponBases = listOf("Warhammer", "War Pick", "Greataxe", "Maul"),
        armorBases = listOf("Plate Mail", "Gauntlets", "Chestguard"),
        itemPrefixes = listOf("Ironvein", "Deepforged", "Runic", "Molten", "Stonebound"),
        questItemNames = listOf("Shard of the Deep Forge", "Lost Miner's Compass", "Sealed Ore Chest", "The Prospector's Journal"),
        captiveNames = listOf("Trapped Miner Borin", "Lost Surveyor Elga"),
    )

    private val PLAINS = SubRealmTheme(
        label = "Root Crypts",
        realmNames = listOf("The Sunken Barrow", "Ancestral Catacomb", "The Hollow Cellar"),
        roomAdjectives = listOf("Musty", "Root-choked", "Dust-laden", "Crumbling", "Silent", "Cobwebbed"),
        roomFeatures = listOf("Burial Chamber", "Ossuary", "Collapsed Cellar", "Root Tunnel", "Forgotten Shrine", "Bone Hall", "Sealed Crypt"),
        creatures = listOf(
            CreatureTemplate("Lost Pilgrim", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Grave Rat Swarm", eldoria.core.model.Disposition.HOSTILE, 1, 2),
            CreatureTemplate("Skeleton Warrior", eldoria.core.model.Disposition.HOSTILE, 1, 3, packSize = 2..3),
            CreatureTemplate("Crypt Wight", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Barrow Wraith", eldoria.core.model.Disposition.HOSTILE, 3, 5),
            CreatureTemplate("Bone Golem", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Barrow King", "Maldrec the Unburied", "The Root-Bound Horror"),
        weaponBases = listOf("Longsword", "Flail", "War Scythe", "Spear"),
        armorBases = listOf("Chainmail", "Cloak", "Breastplate"),
        itemPrefixes = listOf("Ancestral", "Hollowed", "Bonecarved", "Sunken", "Forgotten"),
        questItemNames = listOf("Seal of the First Harvest", "Ancestor's Signet Ring", "The Barrow Key", "Withered Family Ledger"),
        captiveNames = listOf("Trapped Grave Robber Finch", "Lost Acolyte Wren"),
    )

    private val DESERT = SubRealmTheme(
        label = "Buried Tombs",
        realmNames = listOf("The Sun-Idol Tomb", "Duskharrow Sepulcher", "The Scarab Vault"),
        roomAdjectives = listOf("Sand-choked", "Sun-bleached", "Trap-laden", "Gilded", "Airless", "Sealed"),
        roomFeatures = listOf("Sand-choked Hall", "Sarcophagus Chamber", "Trap Corridor", "Hidden Vault", "Sun Idol Room", "Collapsed Passage", "Embalming Hall"),
        creatures = listOf(
            CreatureTemplate("Trapped Excavator", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Scarab Swarm", eldoria.core.model.Disposition.HOSTILE, 1, 3),
            CreatureTemplate("Mummy", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Sand Golem", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Tomb Guardian", eldoria.core.model.Disposition.HOSTILE, 3, 5),
            CreatureTemplate("Cursed Priest", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Sun-Idol Pharaoh", "Ankhet, Eternal Guardian", "The Scarab Sovereign"),
        weaponBases = listOf("Khopesh", "War Scepter", "Ceremonial Spear", "Sun Blade"),
        armorBases = listOf("Golden Cuirass", "Sunplate Armor", "Sealed Vestments"),
        itemPrefixes = listOf("Sunforged", "Eternal", "Gilded", "Sandbound", "Pharaoh's"),
        questItemNames = listOf("The Sun Idol's Eye", "Sealed Canopic Jar", "Scarab Amulet", "Ancient Burial Scroll"),
        captiveNames = listOf("Trapped Excavator Rasha", "Lost Cartographer Idris"),
    )

    private val JUNGLE = SubRealmTheme(
        label = "Overgrown Ruins",
        realmNames = listOf("The Serpent Temple", "Rootwick Hollow", "The Sunken Idol Ruins"),
        roomAdjectives = listOf("Vine-choked", "Moss-covered", "Humid", "Overgrown", "Shadowed", "Flooded"),
        roomFeatures = listOf("Vine-choked Passage", "Temple Antechamber", "Flooded Tunnel", "Idol Chamber", "Root Cavern", "Collapsed Shrine", "Serpent Pit"),
        creatures = listOf(
            CreatureTemplate("Lost Explorer", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Dart Trap Golem", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Serpent Guardian", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Vine Horror", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Jungle Wraith", eldoria.core.model.Disposition.HOSTILE, 3, 5),
            CreatureTemplate("Temple Jaguar", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Serpent God's Avatar", "Yaxil, Idol of Rot", "The Root-Throned Horror"),
        weaponBases = listOf("Serrated Blade", "War Club", "Dart Launcher", "Idol Spear"),
        armorBases = listOf("Bark Plate", "Vinewoven Cloak", "Scaled Hide Armor"),
        itemPrefixes = listOf("Verdant", "Sunken", "Idolbound", "Venomous", "Ancient"),
        questItemNames = listOf("The Serpent Idol's Eye", "Sealed Temple Scroll", "Jade Jaguar Talisman", "Root-Carved Totem"),
        captiveNames = listOf("Trapped Explorer Cass", "Lost Guide Tamsin"),
    )

    private val TUNDRA = SubRealmTheme(
        label = "Frozen Caverns",
        realmNames = listOf("The Rime Hollow", "Frosthaven Undercave", "The Glacial Sepulcher"),
        roomAdjectives = listOf("Frozen", "Ice-crusted", "Frostbitten", "Silent", "Glacial", "Numbing"),
        roomFeatures = listOf("Frozen Tunnel", "Ice Cavern", "Frost Shrine", "Glacial Crevasse Hall", "Buried Ice Temple", "Frostbound Gallery", "Rime Chamber"),
        creatures = listOf(
            CreatureTemplate("Snowbound Trapper", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Rime Spider", eldoria.core.model.Disposition.HOSTILE, 1, 3, packSize = 2..3),
            CreatureTemplate("Frost Wight", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Ice Troll", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Frozen Revenant", eldoria.core.model.Disposition.HOSTILE, 3, 5),
            CreatureTemplate("Glacial Guardian", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Rime Sovereign", "Skarn, the Frozen Wrath", "The Glacial Colossus"),
        weaponBases = listOf("Frost Greatsword", "Ice Warhammer", "Rime Spear", "Frozen Halberd"),
        armorBases = listOf("Frostplate Armor", "Rimewoven Cloak", "Glacial Chestguard"),
        itemPrefixes = listOf("Rimebound", "Frostforged", "Glacial", "Wintereach", "Frozen"),
        questItemNames = listOf("Shard of the Eternal Frost", "Sealed Ice Idol", "Crown Fragment of the Rime Sovereign", "Frozen Explorer's Log"),
        captiveNames = listOf("Trapped Trapper Yorik", "Lost Ranger Sela"),
    )

    private val SEA = SubRealmTheme(
        label = "Sunken Grottos",
        realmNames = listOf("The Drowned Hold", "Tideholm Grotto", "The Abyssal Shrine"),
        roomAdjectives = listOf("Flooded", "Coral-crusted", "Dark", "Brine-soaked", "Sunken", "Echoing"),
        roomFeatures = listOf("Flooded Passage", "Coral Cavern", "Sunken Hold", "Tide Chamber", "Drowned Shrine", "Barnacled Gallery", "Abyssal Rift"),
        creatures = listOf(
            CreatureTemplate("Stranded Diver", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Grotto Eel", eldoria.core.model.Disposition.HOSTILE, 1, 3, packSize = 2..3),
            CreatureTemplate("Drowned Sailor", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Coral Golem", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Deep One", eldoria.core.model.Disposition.HOSTILE, 3, 5),
            CreatureTemplate("Abyssal Guardian", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Abyssal Leviathan", "Maren, the Drowned Queen", "The Tideholm Kraken"),
        weaponBases = listOf("Trident", "Coral Blade", "Barbed Harpoon", "Tidecaller Spear"),
        armorBases = listOf("Coral Plate", "Drowned Cloak", "Barnacled Chestguard"),
        itemPrefixes = listOf("Tidebound", "Abyssal", "Drowned", "Coralforged", "Depthless"),
        questItemNames = listOf("The Drowned Queen's Pearl", "Sealed Captain's Log", "Sunken Idol Fragment", "Barnacled Chest Key"),
        captiveNames = listOf("Trapped Diver Mako", "Lost Navigator Wren"),
    )

    val byBiome: Map<Biome, SubRealmTheme> = mapOf(
        Biome.MOUNTAINS to MOUNTAINS,
        Biome.PLAINS to PLAINS,
        Biome.DESERT to DESERT,
        Biome.JUNGLE to JUNGLE,
        Biome.TUNDRA to TUNDRA,
        Biome.SEA to SEA,
    )

    operator fun get(biome: Biome): SubRealmTheme = byBiome.getValue(biome)
}

/** The sky realm is the deliberate aesthetic opposite of the dungeons: bright, airy, open. */
object SkyContentRegistry {
    private val STORM_PEAKS = SubRealmTheme(
        label = "Storm Peaks",
        realmNames = listOf("The Storm Peaks", "Thunderhead Bastion", "The Tempest Spire"),
        roomAdjectives = listOf("Wind-swept", "Thundering", "Lightning-lit", "Storm-battered", "Roaring", "Electric"),
        roomFeatures = listOf("Cloud Bridge", "Storm Vault", "Wind Tunnel", "Thunder Roost", "Lightning Spire", "Gale Terrace", "Rolling Cloudbank"),
        creatures = listOf(
            CreatureTemplate("Cloud Sprite", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Sky Whale", eldoria.core.model.Disposition.PASSIVE, 1, 3),
            CreatureTemplate("Stranded Skysailor", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Wind Elemental", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Storm Hawk", eldoria.core.model.Disposition.HOSTILE, 2, 4, packSize = 2..3),
            CreatureTemplate("Thunderbird", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Thunderhead Roc", "Zephyrus, Lord of Storms", "The Tempest Wyrm"),
        weaponBases = listOf("Storm Lance", "Thunder Warblade", "Gale Bow", "Lightning Rapier"),
        armorBases = listOf("Stormplate Armor", "Windwoven Cloak", "Thunder Chestguard"),
        itemPrefixes = listOf("Stormforged", "Thundering", "Skybound", "Galebound", "Radiant"),
        questItemNames = listOf("The Storm Compass", "Sealed Cloud Vial", "Thunderbird Feather", "Skysailor's Lost Chart"),
        captiveNames = listOf("Stranded Skysailor Orin", "Lost Windrider Fael"),
    )

    private val SUNLIT_GARDENS = SubRealmTheme(
        label = "Sunlit Gardens",
        realmNames = listOf("The Sunlit Gardens", "Aurora Plateau", "The Radiant Terrace"),
        roomAdjectives = listOf("Sunlit", "Blooming", "Golden", "Warm", "Radiant", "Fragrant"),
        roomFeatures = listOf("Floating Garden", "Sky Temple", "Petal-strewn Terrace", "Sunbeam Atrium", "Rainbow Shoal", "Starlight Chamber", "Golden Aviary"),
        creatures = listOf(
            CreatureTemplate("Zephyr Wisp", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Garden Phoenix", eldoria.core.model.Disposition.PASSIVE, 1, 3),
            CreatureTemplate("Lost Sky Pilgrim", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Star Serpent", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Griffin", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Sun Spirit", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Radiant Griffin King", "Solara, Warden of Light", "The Aurora Sentinel"),
        weaponBases = listOf("Sunblade", "Radiant Bow", "Golden Halberd", "Star Rapier"),
        armorBases = listOf("Sunfeather Armor", "Radiant Vestments", "Golden Chestguard"),
        itemPrefixes = listOf("Sunforged", "Radiant", "Aurora-touched", "Starbound", "Golden"),
        questItemNames = listOf("The Sunpetal Idol", "Sealed Starlight Vial", "Phoenix Feather Charm", "Pilgrim's Sky Chart"),
        captiveNames = listOf("Lost Sky Pilgrim Wisteria", "Stranded Gardener Lume"),
    )

    private val STARLIT_EXPANSE = SubRealmTheme(
        label = "Starlit Expanse",
        realmNames = listOf("The Starlit Expanse", "Celestial Atoll", "The Astral Reaches"),
        roomAdjectives = listOf("Starlit", "Silent", "Shimmering", "Weightless", "Astral", "Twinkling"),
        roomFeatures = listOf("Starlight Chamber", "Astral Bridge", "Void Terrace", "Celestial Vault", "Meteor Garden", "Comet Roost", "Nebula Hollow"),
        creatures = listOf(
            CreatureTemplate("Void Wisp", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Celestial Deer", eldoria.core.model.Disposition.PASSIVE, 1, 3),
            CreatureTemplate("Stranded Stargazer", eldoria.core.model.Disposition.PASSIVE, 1, 2),
            CreatureTemplate("Comet Hawk", eldoria.core.model.Disposition.HOSTILE, 2, 4, packSize = 2..3),
            CreatureTemplate("Star Serpent", eldoria.core.model.Disposition.HOSTILE, 2, 4),
            CreatureTemplate("Astral Guardian", eldoria.core.model.Disposition.HOSTILE, 3, 5),
        ),
        bossCreatures = listOf("The Astral Sovereign", "Nyxara, Keeper of Stars", "The Meteor Colossus"),
        weaponBases = listOf("Astral Blade", "Comet Spear", "Void Bow", "Celestial Warhammer"),
        armorBases = listOf("Starplate Armor", "Astral Cloak", "Celestial Chestguard"),
        itemPrefixes = listOf("Astral", "Celestial", "Starforged", "Void-touched", "Meteoric"),
        questItemNames = listOf("The Celestial Compass", "Sealed Star Shard", "Crown Fragment of the Astral Sovereign", "Stargazer's Lost Atlas"),
        captiveNames = listOf("Stranded Stargazer Orien", "Lost Astral Monk Kess"),
    )

    val variants: List<SubRealmTheme> = listOf(STORM_PEAKS, SUNLIT_GARDENS, STARLIT_EXPANSE)
}
