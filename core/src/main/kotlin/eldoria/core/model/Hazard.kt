package eldoria.core.model

/** A natural environmental danger tied to a biome -- not a monster, just the land itself trying to kill you. */
enum class HazardKind(val displayName: String, val encounterLine: String, val avoidLine: String, val failLine: String, val hitsGear: Boolean) {
    CLIFF_EDGE(
        "Crumbling Cliff Edge",
        "The path narrows along a crumbling cliff edge, loose stone underfoot.",
        "You pick your footing carefully and cross without incident.",
        "The ground gives way! You slide and catch yourself hard against the rock.",
        hitsGear = false,
    ),
    ROCKSLIDE(
        "Loose Rockslide",
        "Loose scree shifts ominously on the slope above you.",
        "You dart across before the slope lets go.",
        "The slope lets go behind you, and stone rains down before you clear it.",
        hitsGear = true,
    ),
    LIGHTNING_STORM(
        "Lightning Storm",
        "Dark clouds roll in fast, and the hair on your arms stands up.",
        "The storm rolls past, close but harmless.",
        "Lightning cracks down far too close, the shock rattling straight through you.",
        hitsGear = false,
    ),
    WILDFIRE(
        "Sudden Wildfire",
        "Smoke stings your eyes -- a wildfire is ripping through the dry grass nearby.",
        "You skirt the flames and keep moving.",
        "The wind shifts and the fire catches you before you can get clear.",
        hitsGear = true,
    ),
    QUICKSAND(
        "Quicksand",
        "The sand ahead looks wrong -- too smooth, too still.",
        "You test the ground first and step wide of the quicksand.",
        "The sand swallows your leg to the knee before you claw free.",
        hitsGear = false,
    ),
    SANDSTORM(
        "Blinding Sandstorm",
        "A wall of sand rises on the horizon and is on you within moments.",
        "You wrap your face and push through the worst of it.",
        "The sandstorm scours exposed skin and grit works into everything you own.",
        hitsGear = true,
    ),
    BOG(
        "Sucking Bog",
        "The ground turns soft and foul-smelling underfoot.",
        "You find solid roots to step on and cross the bog safely.",
        "You sink to the waist in stinking mud before hauling yourself out.",
        hitsGear = false,
    ),
    POISON_THORNS(
        "Poison Thicket",
        "A thicket of vivid, oily-looking thorns blocks the easy path.",
        "You find a way around the worst of the thorns.",
        "A thorn bites deep and your skin goes hot and tight around the wound.",
        hitsGear = false,
    ),
    THIN_ICE(
        "Thin Ice",
        "The ice here looks thin, faint cracks spidering under the frost.",
        "You spread your weight and cross without the ice giving.",
        "The ice cracks and you plunge into freezing water up to your waist.",
        hitsGear = true,
    ),
    AVALANCHE(
        "Avalanche Slope",
        "A hush falls over the snowfield -- exactly the kind of quiet that precedes an avalanche.",
        "You cross quickly and quietly, and the slope holds.",
        "The slope lets go and a wall of snow catches you before you can outrun it.",
        hitsGear = false,
    ),
    RIPTIDE(
        "Riptide",
        "The water here pulls strangely, a current dragging hard against the surface calm.",
        "You read the current and work with it instead of against it.",
        "The riptide seizes you and drags you under before releasing you, battered.",
        hitsGear = false,
    ),
    WHIRLPOOL(
        "Whirlpool",
        "The sea churns into a slow, deliberate spiral ahead.",
        "You steer wide and the whirlpool passes harmlessly.",
        "The whirlpool catches your hull and spins you hard before spitting you out.",
        hitsGear = true,
    ),
    ;

    companion object {
        fun forBiome(biome: Biome): List<HazardKind> = when (biome) {
            Biome.MOUNTAINS -> listOf(CLIFF_EDGE, ROCKSLIDE)
            Biome.PLAINS -> listOf(LIGHTNING_STORM, WILDFIRE)
            Biome.DESERT -> listOf(QUICKSAND, SANDSTORM)
            Biome.JUNGLE -> listOf(BOG, POISON_THORNS)
            Biome.TUNDRA -> listOf(THIN_ICE, AVALANCHE)
            Biome.SEA -> listOf(RIPTIDE, WHIRLPOOL)
        }
    }
}
