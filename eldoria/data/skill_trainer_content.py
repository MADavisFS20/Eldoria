"""Where to find a teacher for every magic school and crafting skill.

Exactly WorldConfig.cities_per_biome (2) trainers per biome -- list order is
load-bearing, world_generator places trainer[i] in city[i] of that biome.
"""
from __future__ import annotations

from dataclasses import dataclass

from eldoria.models import Biome, SkillType


@dataclass(frozen=True)
class TrainerTemplate:
    name: str
    skill: SkillType
    greeting: str
    teach_offer: str


_TRAINERS_BY_BIOME: dict[Biome, list[TrainerTemplate]] = {
    Biome.MOUNTAINS: [
        TrainerTemplate(
            "Borin Ironfist, Dwarven Master Smith", SkillType.BLACKSMITHING,
            "Borin Ironfist wipes soot from his brow and eyes your gear with a critical squint.",
            "\"That blade's a disgrace. Stay a while and I'll teach you to swing a hammer proper -- Blacksmithing's no mystery, just fire, iron, and patience.\"",
        ),
        TrainerTemplate(
            "Old Thrun, Runic Mystic", SkillType.ENCHANTING,
            "Old Thrun traces a glowing rune in the air, watching it fade before it touches the ground.",
            "\"Every blade and ring can hold a whisper of magic, if you know how to bind it. I can show you the runes, if you've the patience for Enchanting.\"",
        ),
    ],
    Biome.PLAINS: [
        TrainerTemplate(
            "Sister Wren, Temple Healer", SkillType.RESTORATION,
            "Sister Wren looks up from bandaging a farmhand's arm and offers you a tired, kind smile.",
            "\"The light doesn't just heal wounds, child -- it mends what fear and steel break. Let me teach you Restoration, and you'll never stand helpless over a dying friend.\"",
        ),
        TrainerTemplate(
            "Mother Fallow, Herbwife", SkillType.ALCHEMY,
            "Mother Fallow is elbow-deep in a basket of roots and dried petals, muttering names of plants under her breath.",
            "\"Half of what grows in these fields will cure you, and the other half will kill you -- the trick is knowing which. Learn Alchemy from me and you'll never guess wrong again.\"",
        ),
    ],
    Biome.DESERT: [
        TrainerTemplate(
            "Zahra the Bright, Sunfire Mystic", SkillType.DESTRUCTION,
            "Zahra the Bright watches a small flame dance across her open palm without ever touching her skin.",
            "\"Fire, frost, lightning -- the desert taught me to command all three. Study Destruction under me, and your enemies will learn to fear your shadow.\"",
        ),
        TrainerTemplate(
            "Kesh Veyra, Mirage Seer", SkillType.ILLUSION,
            "Kesh Veyra's outline shimmers faintly in the heat, and you can't quite tell if that's the desert air or her doing.",
            "\"What the eye believes, the sword obeys. Let me teach you Illusion, and you'll win fights your enemy never even knew they were in.\"",
        ),
    ],
    Biome.JUNGLE: [
        TrainerTemplate(
            "Itzel the Bound, Spirit Caller", SkillType.CONJURATION,
            "Itzel the Bound murmurs to something unseen just past your shoulder, then turns to greet you properly.",
            "\"The spirits of this jungle will fight at your side, if you learn to ask them right. I can teach you Conjuration, if you're not afraid of what answers.\"",
        ),
        TrainerTemplate(
            "Old Kael, Bowyer", SkillType.WOODWORKING,
            "Old Kael turns a half-finished bow stave over in his hands, checking the grain against the light.",
            "\"Any fool can whittle a stick. Learn Woodworking from me and you'll be carving bows and arrows worth carrying into a real fight.\"",
        ),
    ],
    Biome.TUNDRA: [
        TrainerTemplate(
            "Vigdis Coldhand, Frostshaper", SkillType.ALTERATION,
            "Vigdis Coldhand rests a bare hand on the ice wall beside her, and frost creeps outward from her fingertips.",
            "\"Stone, ice, even flesh -- the shape of a thing is only ever a suggestion. Let me teach you Alteration, and you'll learn to bend the rules the world thinks are fixed.\"",
        ),
        TrainerTemplate(
            "Ragnar, Master Smith of the North", SkillType.BLACKSMITHING,
            "Ragnar's hammer rings against the anvil in a steady rhythm that doesn't break as he glances your way.",
            "\"Southern steel is soft. Learn Blacksmithing from a northerner and you'll forge gear that laughs at the cold.\"",
        ),
    ],
    Biome.SEA: [
        TrainerTemplate(
            "Old Barnabus, Sailmaker", SkillType.LEATHERWORKING,
            "Old Barnabus sits cross-legged on the dock, a needle flashing through a stretch of tanned hide.",
            "\"Sailcloth, boots, a good jerkin -- it's all the same skill, just different leather. Let me teach you Leatherworking and you'll never buy shoddy gear again.\"",
        ),
        TrainerTemplate(
            "Priestess Marin of the Tide", SkillType.RESTORATION,
            "Priestess Marin stands at the tideline with her eyes closed, murmuring a prayer timed to the waves.",
            "\"The sea gives and the sea takes, but a healer's hands can hold the balance. Let me teach you Restoration, in the old tidewater way.\"",
        ),
    ],
}


def trainer_for(biome: Biome, city_index: int) -> TrainerTemplate | None:
    """The trainer placed in the city_index-th city of biome (0-based, matches world_generator's city ordering)."""
    trainers = _TRAINERS_BY_BIOME.get(biome, [])
    return trainers[city_index] if 0 <= city_index < len(trainers) else None


def all_trainers() -> list[TrainerTemplate]:
    return [t for group in _TRAINERS_BY_BIOME.values() for t in group]
