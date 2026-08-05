"""All world content is hardcoded here: no runtime generation of text via AI,
just fixed word banks and stat tables that world_generator combines
deterministically. Tiers run 1 (easiest) .. 5 (hardest).
"""
from __future__ import annotations

from eldoria.data.templates import BiomeContent, CreatureTemplate, NpcTemplate
from eldoria.models import Biome, Disposition

HOSTILE = Disposition.HOSTILE
PASSIVE = Disposition.PASSIVE

_MOUNTAINS = BiomeContent(
    biome=Biome.MOUNTAINS,
    adjectives=(
        "Jagged", "Windswept", "Snow-capped", "Craggy", "Frost-bitten",
        "Treacherous", "Granite", "Echoing", "Cloud-piercing", "Avalanche-prone",
        "Wind-scoured", "Shale-strewn",
    ),
    features=(
        "Ridge", "Pass", "Cliff", "Cavern", "Peak", "Scree Slope",
        "Ravine", "Outcrop", "Mineshaft", "Summit", "Crevasse", "Rockfall",
    ),
    qualifiers=("Upper", "Lower", "Northern", "Southern", "Outer", "Inner", "Far", "High"),
    city_names=("Ironstone Citadel", "Skyreach Hold"),
    village_names=(
        "Stonefall Hamlet", "Grayridge", "Cragwatch", "Millstone Vale",
        "Windhollow", "Thornpeak Rest", "Copperveil", "Highforge",
    ),
    creatures=(
        CreatureTemplate("Mountain Goat", PASSIVE, 1, 2),
        CreatureTemplate("Snow Hare", PASSIVE, 1, 2),
        CreatureTemplate("Wild Ram", PASSIVE, 1, 3),
        CreatureTemplate("Cave Bat Swarm", PASSIVE, 1, 3),
        CreatureTemplate("Circling Eagle", PASSIVE, 1, 4),
        CreatureTemplate("Frost Wolf", HOSTILE, 1, 3, pack_size=range(2, 5)),
        CreatureTemplate("Cave Bandit", HOSTILE, 1, 3, pack_size=range(2, 4)),
        CreatureTemplate("Rockslide Troll", HOSTILE, 2, 4),
        CreatureTemplate("Giant Cave Spider", HOSTILE, 2, 4),
        CreatureTemplate("Stone Golem", HOSTILE, 3, 5),
        CreatureTemplate("Yeti", HOSTILE, 4, 5),
        CreatureTemplate("Wyvern", HOSTILE, 4, 5),
        CreatureTemplate("Ancient Dragon", HOSTILE, 5, 5),
    ),
    npcs=(
        NpcTemplate("Miner", PASSIVE, 1, 3),
        NpcTemplate("Mountain Guide", PASSIVE, 1, 3),
        NpcTemplate("Herbalist", PASSIVE, 1, 2),
        NpcTemplate("Traveling Trader", PASSIVE, 1, 3),
        NpcTemplate("Blacksmith", PASSIVE, 1, 2),
        NpcTemplate("Mountain Pilgrim", PASSIVE, 1, 4),
        NpcTemplate("Highway Bandit", HOSTILE, 2, 4),
        NpcTemplate("Rogue Cultist", HOSTILE, 3, 5),
    ),
)

_PLAINS = BiomeContent(
    biome=Biome.PLAINS,
    adjectives=(
        "Rolling", "Golden", "Windswept", "Sunlit", "Fertile", "Sprawling",
        "Tranquil", "Wildflower-strewn", "Sunbaked", "Breezy",
    ),
    features=(
        "Field", "Meadow", "Hill", "Grove", "Farmland", "Crossroads",
        "Windmill Flat", "Streamside", "Pasture", "Knoll", "Wagon Trail",
    ),
    qualifiers=("Upper", "Lower", "Northern", "Southern", "Outer", "Inner", "Far", "Old"),
    city_names=("Everfield City", "Sunspire"),
    village_names=(
        "Wheatridge", "Millbrook", "Larkspur Hollow", "Oxbend",
        "Clover Hearth", "Fallowmead", "Brightfurrow", "Hearthstead",
    ),
    creatures=(
        CreatureTemplate("Grazing Deer", PASSIVE, 1, 2),
        CreatureTemplate("Wild Horse Herd", PASSIVE, 1, 2),
        CreatureTemplate("Sheep Flock", PASSIVE, 1, 1),
        CreatureTemplate("Songbird Flock", PASSIVE, 1, 2),
        CreatureTemplate("Field Fox", PASSIVE, 1, 3),
        CreatureTemplate("Plains Wolf", HOSTILE, 1, 3, pack_size=range(2, 5)),
        CreatureTemplate("Locust Swarm", HOSTILE, 1, 2),
        CreatureTemplate("Giant Boar", HOSTILE, 2, 4),
        CreatureTemplate("Bandit Raider", HOSTILE, 2, 4, pack_size=range(2, 4)),
        CreatureTemplate("Rogue Knight", HOSTILE, 3, 5),
        CreatureTemplate("Ogre", HOSTILE, 4, 5),
    ),
    npcs=(
        NpcTemplate("Farmer", PASSIVE, 1, 2),
        NpcTemplate("Shepherd", PASSIVE, 1, 2),
        NpcTemplate("Traveling Merchant", PASSIVE, 1, 3),
        NpcTemplate("Town Crier", PASSIVE, 1, 2),
        NpcTemplate("Miller", PASSIVE, 1, 2),
        NpcTemplate("Wandering Bard", PASSIVE, 1, 4),
        NpcTemplate("Highwayman", HOSTILE, 2, 4),
        NpcTemplate("Marauder", HOSTILE, 3, 5),
    ),
)

_DESERT = BiomeContent(
    biome=Biome.DESERT,
    adjectives=(
        "Scorching", "Sun-bleached", "Wind-carved", "Arid", "Shimmering",
        "Dust-choked", "Sunburnt", "Endless", "Cracked", "Blistering",
    ),
    features=(
        "Dune", "Oasis", "Mesa", "Canyon", "Sandstorm Flat", "Buried Ruin",
        "Salt Flat", "Wadi", "Rock Spire", "Buried Temple", "Sinkhole",
    ),
    qualifiers=("Upper", "Lower", "Northern", "Southern", "Outer", "Inner", "Far", "Deep"),
    city_names=("Sandspire Bazaar", "Duskharrow"),
    village_names=(
        "Palmshade Rest", "Amberwell", "Sunveil Camp", "Cactusbrook",
        "Glassdune", "Mirage Hollow", "Scarabend", "Dryrun Oasis",
    ),
    creatures=(
        CreatureTemplate("Desert Fox", PASSIVE, 1, 2),
        CreatureTemplate("Camel Herd", PASSIVE, 1, 1),
        CreatureTemplate("Basking Lizard", PASSIVE, 1, 2),
        CreatureTemplate("Circling Vulture", PASSIVE, 1, 3),
        CreatureTemplate("Sand Hare", PASSIVE, 1, 2),
        CreatureTemplate("Giant Scorpion", HOSTILE, 1, 3),
        CreatureTemplate("Rock Viper", HOSTILE, 1, 3),
        CreatureTemplate("Jackal Pack", HOSTILE, 1, 3),
        CreatureTemplate("Desert Raider", HOSTILE, 2, 4, pack_size=range(2, 4)),
        CreatureTemplate("Sand Wraith", HOSTILE, 3, 5),
        CreatureTemplate("Dust Elemental", HOSTILE, 3, 5),
        CreatureTemplate("Ancient Sphinx Guardian", HOSTILE, 5, 5),
    ),
    npcs=(
        NpcTemplate("Caravan Trader", PASSIVE, 1, 3),
        NpcTemplate("Oasis Keeper", PASSIVE, 1, 2),
        NpcTemplate("Nomad Guide", PASSIVE, 1, 3),
        NpcTemplate("Fortune Teller", PASSIVE, 1, 3),
        NpcTemplate("Water Merchant", PASSIVE, 1, 2),
        NpcTemplate("Dune Raider", HOSTILE, 2, 4),
        NpcTemplate("Cultist of the Sun", HOSTILE, 4, 5),
    ),
)

_JUNGLE = BiomeContent(
    biome=Biome.JUNGLE,
    adjectives=(
        "Dense", "Humid", "Vine-choked", "Sweltering", "Teeming",
        "Moss-covered", "Shadowed", "Overgrown", "Sodden", "Buzzing",
    ),
    features=(
        "Canopy", "Thicket", "Riverbank", "Temple Ruin", "Swamp",
        "Waterfall", "Vine Bridge", "Mangrove", "Hidden Grove", "Sinkhole",
    ),
    qualifiers=("Upper", "Lower", "Northern", "Southern", "Outer", "Inner", "Far", "Deep"),
    city_names=("Verdant Spire", "Emerald Bastion"),
    village_names=(
        "Fernhollow", "Mossvale", "Rootwick", "Canopy Rest",
        "Serpent's Bend", "Vinehearth", "Junglemere", "Palmshade Landing",
    ),
    creatures=(
        CreatureTemplate("Tropical Bird Flock", PASSIVE, 1, 2),
        CreatureTemplate("Monkey Troop", PASSIVE, 1, 2),
        CreatureTemplate("River Otter", PASSIVE, 1, 2),
        CreatureTemplate("Butterfly Swarm", PASSIVE, 1, 1),
        CreatureTemplate("Wandering Tapir", PASSIVE, 1, 3),
        CreatureTemplate("Poison Dart Frog Swarm", HOSTILE, 1, 2),
        CreatureTemplate("Venomous Spider Nest", HOSTILE, 1, 3),
        CreatureTemplate("Jungle Panther", HOSTILE, 2, 4),
        CreatureTemplate("Giant Anaconda", HOSTILE, 2, 4),
        CreatureTemplate("Headhunter Tribe", HOSTILE, 2, 4),
        CreatureTemplate("Jaguar Spirit", HOSTILE, 4, 5),
        CreatureTemplate("Ancient Tree Guardian", HOSTILE, 4, 5),
    ),
    npcs=(
        NpcTemplate("Tribal Elder", PASSIVE, 1, 3),
        NpcTemplate("Herbalist", PASSIVE, 1, 2),
        NpcTemplate("River Guide", PASSIVE, 1, 3),
        NpcTemplate("Ruin Explorer", PASSIVE, 1, 4),
        NpcTemplate("Jungle Trader", PASSIVE, 1, 2),
        NpcTemplate("Poacher", HOSTILE, 2, 4),
        NpcTemplate("Cultist of the Vine", HOSTILE, 4, 5),
    ),
)

_TUNDRA = BiomeContent(
    biome=Biome.TUNDRA,
    adjectives=(
        "Frozen", "Ice-crusted", "Howling", "Desolate", "Glacial",
        "Snowbound", "Bone-chilling", "Endless-white", "Wind-scoured", "Numbing",
    ),
    features=(
        "Ice Field", "Glacier", "Frozen Lake", "Snowdrift", "Permafrost Plain",
        "Blizzard Pass", "Frost Cave", "Iceberg Shore", "Tundra Plain", "Frost Ruin",
    ),
    qualifiers=("Upper", "Lower", "Northern", "Southern", "Outer", "Inner", "Far", "High"),
    city_names=("Frosthaven", "Icewatch Keep"),
    village_names=(
        "Snowmere", "Coldbrook", "Palefrost Camp", "Whitewind Hearth",
        "Icemoor", "Rimehollow", "Glacierun", "Frostfall Rest",
    ),
    creatures=(
        CreatureTemplate("Snow Fox", PASSIVE, 1, 2),
        CreatureTemplate("Reindeer Herd", PASSIVE, 1, 2),
        CreatureTemplate("Arctic Hare", PASSIVE, 1, 2),
        CreatureTemplate("Snow Owl", PASSIVE, 1, 3),
        CreatureTemplate("Seal Colony", PASSIVE, 1, 1),
        CreatureTemplate("Ice Wolf", HOSTILE, 1, 3, pack_size=range(2, 5)),
        CreatureTemplate("Ice Bandit", HOSTILE, 2, 4, pack_size=range(2, 4)),
        CreatureTemplate("Polar Bear", HOSTILE, 2, 4),
        CreatureTemplate("Frost Wraith", HOSTILE, 3, 5),
        CreatureTemplate("Frozen Revenant", HOSTILE, 3, 5),
        CreatureTemplate("Frost Giant", HOSTILE, 4, 5),
    ),
    npcs=(
        NpcTemplate("Fur Trapper", PASSIVE, 1, 3),
        NpcTemplate("Ice Fisher", PASSIVE, 1, 2),
        NpcTemplate("Sled Driver", PASSIVE, 1, 3),
        NpcTemplate("Tundra Shaman", PASSIVE, 1, 4),
        NpcTemplate("Trading Post Keeper", PASSIVE, 1, 2),
        NpcTemplate("Frost Raider", HOSTILE, 2, 4),
        NpcTemplate("Cultist of Winter", HOSTILE, 4, 5),
    ),
)

_SEA = BiomeContent(
    biome=Biome.SEA,
    adjectives=(
        "Salt-sprayed", "Windswept", "Sunlit", "Storm-tossed", "Coral-fringed",
        "Foggy", "Tide-swept", "Endless-blue", "Briny", "Gull-loud",
    ),
    features=(
        "Reef", "Cove", "Harbor", "Tidepool", "Shipwreck", "Sandbar",
        "Lighthouse Point", "Sea Cave", "Island Shoal", "Deep Trench",
    ),
    qualifiers=("Upper", "Lower", "Northern", "Southern", "Outer", "Inner", "Far", "Old"),
    city_names=("Port Eldoria", "Tideholm"),
    village_names=(
        "Saltmere", "Driftwood Cove", "Herring Bay", "Foghaven",
        "Pearlshore", "Tidewatch", "Anchorstead", "Gullcry Landing",
    ),
    creatures=(
        CreatureTemplate("Dolphin Pod", PASSIVE, 1, 2),
        CreatureTemplate("Seagull Flock", PASSIVE, 1, 1),
        CreatureTemplate("Sea Turtle", PASSIVE, 1, 2),
        CreatureTemplate("School of Fish", PASSIVE, 1, 1),
        CreatureTemplate("Otter Raft", PASSIVE, 1, 2),
        CreatureTemplate("Giant Crab", HOSTILE, 1, 3),
        CreatureTemplate("Reef Shark", HOSTILE, 2, 4, pack_size=range(2, 4)),
        CreatureTemplate("Pirate Crew", HOSTILE, 2, 4),
        CreatureTemplate("Sea Serpent", HOSTILE, 3, 5),
        CreatureTemplate("Cursed Sailor", HOSTILE, 3, 5),
        CreatureTemplate("Siren", HOSTILE, 3, 5),
        CreatureTemplate("Kraken Spawn", HOSTILE, 4, 5),
    ),
    npcs=(
        NpcTemplate("Fisherman", PASSIVE, 1, 2),
        NpcTemplate("Harbor Master", PASSIVE, 1, 2),
        NpcTemplate("Ship Merchant", PASSIVE, 1, 3),
        NpcTemplate("Lighthouse Keeper", PASSIVE, 1, 2),
        NpcTemplate("Sailor", PASSIVE, 1, 3),
        NpcTemplate("Pirate Raider", HOSTILE, 2, 4),
        NpcTemplate("Smuggler", HOSTILE, 2, 4),
    ),
)

_ALL: dict[Biome, BiomeContent] = {
    content.biome: content for content in (_MOUNTAINS, _PLAINS, _DESERT, _JUNGLE, _TUNDRA, _SEA)
}


def get(biome: Biome) -> BiomeContent:
    return _ALL[biome]


def all_content() -> dict[Biome, BiomeContent]:
    return _ALL
