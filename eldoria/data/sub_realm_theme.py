"""All hardcoded flavor content for one dungeon (per-biome) or sky-realm variant."""
from __future__ import annotations

from dataclasses import dataclass

from eldoria.data.templates import CreatureTemplate
from eldoria.models import Biome, Disposition

HOSTILE = Disposition.HOSTILE
PASSIVE = Disposition.PASSIVE


@dataclass(frozen=True)
class SubRealmTheme:
    label: str
    realm_names: tuple[str, ...]
    room_adjectives: tuple[str, ...]
    room_features: tuple[str, ...]
    creatures: tuple[CreatureTemplate, ...]
    boss_creatures: tuple[str, ...]
    weapon_bases: tuple[str, ...]
    armor_bases: tuple[str, ...]
    item_prefixes: tuple[str, ...]
    quest_item_names: tuple[str, ...]
    captive_names: tuple[str, ...]

    def creatures_for(self, tier: int) -> list[CreatureTemplate]:
        return [c for c in self.creatures if c.min_tier <= tier <= c.max_tier]


# --- DungeonContentRegistry ---------------------------------------------

_DUNGEON_MOUNTAINS = SubRealmTheme(
    label="Deep Mines",
    realm_names=("Ironvein Depths", "Skyreach Undermines", "The Hollow Shaft"),
    room_adjectives=("Dust-choked", "Echoing", "Torch-lit", "Collapsed", "Gem-veined", "Cold", "Rubble-strewn"),
    room_features=("Tunnel", "Mineshaft", "Cavern", "Forge Ruin", "Crystal Chamber", "Collapsed Gallery", "Underground Lake", "Ore Vein Hall"),
    creatures=(
        CreatureTemplate("Bat Swarm", PASSIVE, 1, 2),
        CreatureTemplate("Lost Prospector", PASSIVE, 1, 2),
        CreatureTemplate("Kobold Miner", HOSTILE, 1, 3, pack_size=range(2, 4)),
        CreatureTemplate("Cave Troll", HOSTILE, 2, 4),
        CreatureTemplate("Rock Wight", HOSTILE, 2, 4),
        CreatureTemplate("Deep Spider", HOSTILE, 2, 4),
        CreatureTemplate("Gem Golem", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Ironvein Colossus", "Grask, Warden of the Deep", "The Sunken Forge-Wraith"),
    weapon_bases=("Warhammer", "War Pick", "Greataxe", "Maul"),
    armor_bases=("Plate Mail", "Gauntlets", "Chestguard"),
    item_prefixes=("Ironvein", "Deepforged", "Runic", "Molten", "Stonebound"),
    quest_item_names=("Shard of the Deep Forge", "Lost Miner's Compass", "Sealed Ore Chest", "The Prospector's Journal"),
    captive_names=("Trapped Miner Borin", "Lost Surveyor Elga"),
)

_DUNGEON_PLAINS = SubRealmTheme(
    label="Root Crypts",
    realm_names=("The Sunken Barrow", "Ancestral Catacomb", "The Hollow Cellar"),
    room_adjectives=("Musty", "Root-choked", "Dust-laden", "Crumbling", "Silent", "Cobwebbed"),
    room_features=("Burial Chamber", "Ossuary", "Collapsed Cellar", "Root Tunnel", "Forgotten Shrine", "Bone Hall", "Sealed Crypt"),
    creatures=(
        CreatureTemplate("Lost Pilgrim", PASSIVE, 1, 2),
        CreatureTemplate("Grave Rat Swarm", HOSTILE, 1, 2),
        CreatureTemplate("Skeleton Warrior", HOSTILE, 1, 3, pack_size=range(2, 4)),
        CreatureTemplate("Crypt Wight", HOSTILE, 2, 4),
        CreatureTemplate("Barrow Wraith", HOSTILE, 3, 5),
        CreatureTemplate("Bone Golem", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Barrow King", "Maldrec the Unburied", "The Root-Bound Horror"),
    weapon_bases=("Longsword", "Flail", "War Scythe", "Spear"),
    armor_bases=("Chainmail", "Cloak", "Breastplate"),
    item_prefixes=("Ancestral", "Hollowed", "Bonecarved", "Sunken", "Forgotten"),
    quest_item_names=("Seal of the First Harvest", "Ancestor's Signet Ring", "The Barrow Key", "Withered Family Ledger"),
    captive_names=("Trapped Grave Robber Finch", "Lost Acolyte Wren"),
)

_DUNGEON_DESERT = SubRealmTheme(
    label="Buried Tombs",
    realm_names=("The Sun-Idol Tomb", "Duskharrow Sepulcher", "The Scarab Vault"),
    room_adjectives=("Sand-choked", "Sun-bleached", "Trap-laden", "Gilded", "Airless", "Sealed"),
    room_features=("Sand-choked Hall", "Sarcophagus Chamber", "Trap Corridor", "Hidden Vault", "Sun Idol Room", "Collapsed Passage", "Embalming Hall"),
    creatures=(
        CreatureTemplate("Trapped Excavator", PASSIVE, 1, 2),
        CreatureTemplate("Scarab Swarm", HOSTILE, 1, 3),
        CreatureTemplate("Mummy", HOSTILE, 2, 4),
        CreatureTemplate("Sand Golem", HOSTILE, 2, 4),
        CreatureTemplate("Tomb Guardian", HOSTILE, 3, 5),
        CreatureTemplate("Cursed Priest", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Sun-Idol Pharaoh", "Ankhet, Eternal Guardian", "The Scarab Sovereign"),
    weapon_bases=("Khopesh", "War Scepter", "Ceremonial Spear", "Sun Blade"),
    armor_bases=("Golden Cuirass", "Sunplate Armor", "Sealed Vestments"),
    item_prefixes=("Sunforged", "Eternal", "Gilded", "Sandbound", "Pharaoh's"),
    quest_item_names=("The Sun Idol's Eye", "Sealed Canopic Jar", "Scarab Amulet", "Ancient Burial Scroll"),
    captive_names=("Trapped Excavator Rasha", "Lost Cartographer Idris"),
)

_DUNGEON_JUNGLE = SubRealmTheme(
    label="Overgrown Ruins",
    realm_names=("The Serpent Temple", "Rootwick Hollow", "The Sunken Idol Ruins"),
    room_adjectives=("Vine-choked", "Moss-covered", "Humid", "Overgrown", "Shadowed", "Flooded"),
    room_features=("Vine-choked Passage", "Temple Antechamber", "Flooded Tunnel", "Idol Chamber", "Root Cavern", "Collapsed Shrine", "Serpent Pit"),
    creatures=(
        CreatureTemplate("Lost Explorer", PASSIVE, 1, 2),
        CreatureTemplate("Dart Trap Golem", HOSTILE, 2, 4),
        CreatureTemplate("Serpent Guardian", HOSTILE, 2, 4),
        CreatureTemplate("Vine Horror", HOSTILE, 2, 4),
        CreatureTemplate("Jungle Wraith", HOSTILE, 3, 5),
        CreatureTemplate("Temple Jaguar", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Serpent God's Avatar", "Yaxil, Idol of Rot", "The Root-Throned Horror"),
    weapon_bases=("Serrated Blade", "War Club", "Dart Launcher", "Idol Spear"),
    armor_bases=("Bark Plate", "Vinewoven Cloak", "Scaled Hide Armor"),
    item_prefixes=("Verdant", "Sunken", "Idolbound", "Venomous", "Ancient"),
    quest_item_names=("The Serpent Idol's Eye", "Sealed Temple Scroll", "Jade Jaguar Talisman", "Root-Carved Totem"),
    captive_names=("Trapped Explorer Cass", "Lost Guide Tamsin"),
)

_DUNGEON_TUNDRA = SubRealmTheme(
    label="Frozen Caverns",
    realm_names=("The Rime Hollow", "Frosthaven Undercave", "The Glacial Sepulcher"),
    room_adjectives=("Frozen", "Ice-crusted", "Frostbitten", "Silent", "Glacial", "Numbing"),
    room_features=("Frozen Tunnel", "Ice Cavern", "Frost Shrine", "Glacial Crevasse Hall", "Buried Ice Temple", "Frostbound Gallery", "Rime Chamber"),
    creatures=(
        CreatureTemplate("Snowbound Trapper", PASSIVE, 1, 2),
        CreatureTemplate("Rime Spider", HOSTILE, 1, 3, pack_size=range(2, 4)),
        CreatureTemplate("Frost Wight", HOSTILE, 2, 4),
        CreatureTemplate("Ice Troll", HOSTILE, 2, 4),
        CreatureTemplate("Frozen Revenant", HOSTILE, 3, 5),
        CreatureTemplate("Glacial Guardian", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Rime Sovereign", "Skarn, the Frozen Wrath", "The Glacial Colossus"),
    weapon_bases=("Frost Greatsword", "Ice Warhammer", "Rime Spear", "Frozen Halberd"),
    armor_bases=("Frostplate Armor", "Rimewoven Cloak", "Glacial Chestguard"),
    item_prefixes=("Rimebound", "Frostforged", "Glacial", "Wintereach", "Frozen"),
    quest_item_names=("Shard of the Eternal Frost", "Sealed Ice Idol", "Crown Fragment of the Rime Sovereign", "Frozen Explorer's Log"),
    captive_names=("Trapped Trapper Yorik", "Lost Ranger Sela"),
)

_DUNGEON_SEA = SubRealmTheme(
    label="Sunken Grottos",
    realm_names=("The Drowned Hold", "Tideholm Grotto", "The Abyssal Shrine"),
    room_adjectives=("Flooded", "Coral-crusted", "Dark", "Brine-soaked", "Sunken", "Echoing"),
    room_features=("Flooded Passage", "Coral Cavern", "Sunken Hold", "Tide Chamber", "Drowned Shrine", "Barnacled Gallery", "Abyssal Rift"),
    creatures=(
        CreatureTemplate("Stranded Diver", PASSIVE, 1, 2),
        CreatureTemplate("Grotto Eel", HOSTILE, 1, 3, pack_size=range(2, 4)),
        CreatureTemplate("Drowned Sailor", HOSTILE, 2, 4),
        CreatureTemplate("Coral Golem", HOSTILE, 2, 4),
        CreatureTemplate("Deep One", HOSTILE, 3, 5),
        CreatureTemplate("Abyssal Guardian", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Abyssal Leviathan", "Maren, the Drowned Queen", "The Tideholm Kraken"),
    weapon_bases=("Trident", "Coral Blade", "Barbed Harpoon", "Tidecaller Spear"),
    armor_bases=("Coral Plate", "Drowned Cloak", "Barnacled Chestguard"),
    item_prefixes=("Tidebound", "Abyssal", "Drowned", "Coralforged", "Depthless"),
    quest_item_names=("The Drowned Queen's Pearl", "Sealed Captain's Log", "Sunken Idol Fragment", "Barnacled Chest Key"),
    captive_names=("Trapped Diver Mako", "Lost Navigator Wren"),
)

_DUNGEON_BY_BIOME: dict[Biome, SubRealmTheme] = {
    Biome.MOUNTAINS: _DUNGEON_MOUNTAINS,
    Biome.PLAINS: _DUNGEON_PLAINS,
    Biome.DESERT: _DUNGEON_DESERT,
    Biome.JUNGLE: _DUNGEON_JUNGLE,
    Biome.TUNDRA: _DUNGEON_TUNDRA,
    Biome.SEA: _DUNGEON_SEA,
}


def dungeon_theme_for(biome: Biome) -> SubRealmTheme:
    return _DUNGEON_BY_BIOME[biome]


def dungeon_themes_by_biome() -> dict[Biome, SubRealmTheme]:
    return _DUNGEON_BY_BIOME


# --- SkyContentRegistry --------------------------------------------------
# The sky realm is the deliberate aesthetic opposite of the dungeons: bright, airy, open.

_SKY_STORM_PEAKS = SubRealmTheme(
    label="Storm Peaks",
    realm_names=("The Storm Peaks", "Thunderhead Bastion", "The Tempest Spire"),
    room_adjectives=("Wind-swept", "Thundering", "Lightning-lit", "Storm-battered", "Roaring", "Electric"),
    room_features=("Cloud Bridge", "Storm Vault", "Wind Tunnel", "Thunder Roost", "Lightning Spire", "Gale Terrace", "Rolling Cloudbank"),
    creatures=(
        CreatureTemplate("Cloud Sprite", PASSIVE, 1, 2),
        CreatureTemplate("Sky Whale", PASSIVE, 1, 3),
        CreatureTemplate("Stranded Skysailor", PASSIVE, 1, 2),
        CreatureTemplate("Wind Elemental", HOSTILE, 2, 4),
        CreatureTemplate("Storm Hawk", HOSTILE, 2, 4, pack_size=range(2, 4)),
        CreatureTemplate("Thunderbird", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Thunderhead Roc", "Zephyrus, Lord of Storms", "The Tempest Wyrm"),
    weapon_bases=("Storm Lance", "Thunder Warblade", "Gale Bow", "Lightning Rapier"),
    armor_bases=("Stormplate Armor", "Windwoven Cloak", "Thunder Chestguard"),
    item_prefixes=("Stormforged", "Thundering", "Skybound", "Galebound", "Radiant"),
    quest_item_names=("The Storm Compass", "Sealed Cloud Vial", "Thunderbird Feather", "Skysailor's Lost Chart"),
    captive_names=("Stranded Skysailor Orin", "Lost Windrider Fael"),
)

_SKY_SUNLIT_GARDENS = SubRealmTheme(
    label="Sunlit Gardens",
    realm_names=("The Sunlit Gardens", "Aurora Plateau", "The Radiant Terrace"),
    room_adjectives=("Sunlit", "Blooming", "Golden", "Warm", "Radiant", "Fragrant"),
    room_features=("Floating Garden", "Sky Temple", "Petal-strewn Terrace", "Sunbeam Atrium", "Rainbow Shoal", "Starlight Chamber", "Golden Aviary"),
    creatures=(
        CreatureTemplate("Zephyr Wisp", PASSIVE, 1, 2),
        CreatureTemplate("Garden Phoenix", PASSIVE, 1, 3),
        CreatureTemplate("Lost Sky Pilgrim", PASSIVE, 1, 2),
        CreatureTemplate("Star Serpent", HOSTILE, 2, 4),
        CreatureTemplate("Griffin", HOSTILE, 2, 4),
        CreatureTemplate("Sun Spirit", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Radiant Griffin King", "Solara, Warden of Light", "The Aurora Sentinel"),
    weapon_bases=("Sunblade", "Radiant Bow", "Golden Halberd", "Star Rapier"),
    armor_bases=("Sunfeather Armor", "Radiant Vestments", "Golden Chestguard"),
    item_prefixes=("Sunforged", "Radiant", "Aurora-touched", "Starbound", "Golden"),
    quest_item_names=("The Sunpetal Idol", "Sealed Starlight Vial", "Phoenix Feather Charm", "Pilgrim's Sky Chart"),
    captive_names=("Lost Sky Pilgrim Wisteria", "Stranded Gardener Lume"),
)

_SKY_STARLIT_EXPANSE = SubRealmTheme(
    label="Starlit Expanse",
    realm_names=("The Starlit Expanse", "Celestial Atoll", "The Astral Reaches"),
    room_adjectives=("Starlit", "Silent", "Shimmering", "Weightless", "Astral", "Twinkling"),
    room_features=("Starlight Chamber", "Astral Bridge", "Void Terrace", "Celestial Vault", "Meteor Garden", "Comet Roost", "Nebula Hollow"),
    creatures=(
        CreatureTemplate("Void Wisp", PASSIVE, 1, 2),
        CreatureTemplate("Celestial Deer", PASSIVE, 1, 3),
        CreatureTemplate("Stranded Stargazer", PASSIVE, 1, 2),
        CreatureTemplate("Comet Hawk", HOSTILE, 2, 4, pack_size=range(2, 4)),
        CreatureTemplate("Star Serpent", HOSTILE, 2, 4),
        CreatureTemplate("Astral Guardian", HOSTILE, 3, 5),
    ),
    boss_creatures=("The Astral Sovereign", "Nyxara, Keeper of Stars", "The Meteor Colossus"),
    weapon_bases=("Astral Blade", "Comet Spear", "Void Bow", "Celestial Warhammer"),
    armor_bases=("Starplate Armor", "Astral Cloak", "Celestial Chestguard"),
    item_prefixes=("Astral", "Celestial", "Starforged", "Void-touched", "Meteoric"),
    quest_item_names=("The Celestial Compass", "Sealed Star Shard", "Crown Fragment of the Astral Sovereign", "Stargazer's Lost Atlas"),
    captive_names=("Stranded Stargazer Orien", "Lost Astral Monk Kess"),
)

_SKY_VARIANTS: tuple[SubRealmTheme, ...] = (_SKY_STORM_PEAKS, _SKY_SUNLIT_GARDENS, _SKY_STARLIT_EXPANSE)


def sky_theme_variants() -> tuple[SubRealmTheme, ...]:
    return _SKY_VARIANTS


def sky_theme_for(index: int) -> SubRealmTheme:
    return _SKY_VARIANTS[index % len(_SKY_VARIANTS)]
