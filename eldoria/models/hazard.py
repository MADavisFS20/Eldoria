"""A natural environmental danger tied to a biome -- not a monster, just the land itself trying to kill you."""
from __future__ import annotations

from enum import Enum

from eldoria.models.biome import Biome


class HazardKind(Enum):
    CLIFF_EDGE = (
        "Crumbling Cliff Edge",
        "The path narrows along a crumbling cliff edge, loose stone underfoot.",
        "You pick your footing carefully and cross without incident.",
        "The ground gives way! You slide and catch yourself hard against the rock.",
        False,
    )
    ROCKSLIDE = (
        "Loose Rockslide",
        "Loose scree shifts ominously on the slope above you.",
        "You dart across before the slope lets go.",
        "The slope lets go behind you, and stone rains down before you clear it.",
        True,
    )
    LIGHTNING_STORM = (
        "Lightning Storm",
        "Dark clouds roll in fast, and the hair on your arms stands up.",
        "The storm rolls past, close but harmless.",
        "Lightning cracks down far too close, the shock rattling straight through you.",
        False,
    )
    WILDFIRE = (
        "Sudden Wildfire",
        "Smoke stings your eyes -- a wildfire is ripping through the dry grass nearby.",
        "You skirt the flames and keep moving.",
        "The wind shifts and the fire catches you before you can get clear.",
        True,
    )
    QUICKSAND = (
        "Quicksand",
        "The sand ahead looks wrong -- too smooth, too still.",
        "You test the ground first and step wide of the quicksand.",
        "The sand swallows your leg to the knee before you claw free.",
        False,
    )
    SANDSTORM = (
        "Blinding Sandstorm",
        "A wall of sand rises on the horizon and is on you within moments.",
        "You wrap your face and push through the worst of it.",
        "The sandstorm scours exposed skin and grit works into everything you own.",
        True,
    )
    BOG = (
        "Sucking Bog",
        "The ground turns soft and foul-smelling underfoot.",
        "You find solid roots to step on and cross the bog safely.",
        "You sink to the waist in stinking mud before hauling yourself out.",
        False,
    )
    POISON_THORNS = (
        "Poison Thicket",
        "A thicket of vivid, oily-looking thorns blocks the easy path.",
        "You find a way around the worst of the thorns.",
        "A thorn bites deep and your skin goes hot and tight around the wound.",
        False,
    )
    THIN_ICE = (
        "Thin Ice",
        "The ice here looks thin, faint cracks spidering under the frost.",
        "You spread your weight and cross without the ice giving.",
        "The ice cracks and you plunge into freezing water up to your waist.",
        True,
    )
    AVALANCHE = (
        "Avalanche Slope",
        "A hush falls over the snowfield -- exactly the kind of quiet that precedes an avalanche.",
        "You cross quickly and quietly, and the slope holds.",
        "The slope lets go and a wall of snow catches you before you can outrun it.",
        False,
    )
    RIPTIDE = (
        "Riptide",
        "The water here pulls strangely, a current dragging hard against the surface calm.",
        "You read the current and work with it instead of against it.",
        "The riptide seizes you and drags you under before releasing you, battered.",
        False,
    )
    WHIRLPOOL = (
        "Whirlpool",
        "The sea churns into a slow, deliberate spiral ahead.",
        "You steer wide and the whirlpool passes harmlessly.",
        "The whirlpool catches your hull and spins you hard before spitting you out.",
        True,
    )

    def __init__(self, display_name: str, encounter_line: str, avoid_line: str, fail_line: str, hits_gear: bool):
        self.display_name = display_name
        self.encounter_line = encounter_line
        self.avoid_line = avoid_line
        self.fail_line = fail_line
        self.hits_gear = hits_gear

    @staticmethod
    def for_biome(biome: Biome) -> list["HazardKind"]:
        return {
            Biome.MOUNTAINS: [HazardKind.CLIFF_EDGE, HazardKind.ROCKSLIDE],
            Biome.PLAINS: [HazardKind.LIGHTNING_STORM, HazardKind.WILDFIRE],
            Biome.DESERT: [HazardKind.QUICKSAND, HazardKind.SANDSTORM],
            Biome.JUNGLE: [HazardKind.BOG, HazardKind.POISON_THORNS],
            Biome.TUNDRA: [HazardKind.THIN_ICE, HazardKind.AVALANCHE],
            Biome.SEA: [HazardKind.RIPTIDE, HazardKind.WHIRLPOOL],
        }[biome]
