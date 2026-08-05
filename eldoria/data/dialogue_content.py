"""Hand-written dialogue banks so every NPC says something that fits who they are.

Passive NPCs are classified into a small archetype by keyword match on their
template name, then given a varied, biome/location-aware line. Hostile
beings get a threat/taunt line instead of a chat line.
"""
from __future__ import annotations

import random
from enum import Enum

from eldoria.models import Biome, QuestType


class NpcArchetype(Enum):
    TRADER = "TRADER"
    GUIDE = "GUIDE"
    LABORER = "LABORER"
    HEALER = "HEALER"
    MYSTIC = "MYSTIC"
    ENTERTAINER = "ENTERTAINER"
    GENERIC = "GENERIC"


def archetype_for(npc_name: str) -> NpcArchetype:
    n = npc_name.lower()
    if any(k in n for k in ("trader", "merchant", "keeper", "vendor")):
        return NpcArchetype.TRADER
    if any(k in n for k in ("guide", "sled driver", "pilgrim")):
        return NpcArchetype.GUIDE
    if any(k in n for k in ("miner", "farmer", "shepherd", "miller", "fisher", "trapper", "sailor", "crier")):
        return NpcArchetype.LABORER
    if any(k in n for k in ("healer", "herbalist", "priestess", "medic")):
        return NpcArchetype.HEALER
    if any(k in n for k in ("elder", "shaman", "mystic", "seer", "fortune teller", "cultist")):
        return NpcArchetype.MYSTIC
    if any(k in n for k in ("bard", "crier")):
        return NpcArchetype.ENTERTAINER
    return NpcArchetype.GENERIC


_TRADER_LINES = [
    "\"Best prices this side of {location}, I promise you that.\"",
    "\"Buying or selling? Either way, step out of the sun and let's talk.\"",
    "\"Careful on the roads out of {location} -- I lost a whole cart to bandits last month.\"",
]
_GUIDE_LINES = [
    "\"Lost? Half the travelers through {location} are, first time. I can point you right.\"",
    "\"I know every safe path out of {location} and a few of the unsafe ones too.\"",
    "\"Stick to the marked trails past {location} -- the wild parts of this {biome} don't forgive mistakes.\"",
]
_LABORER_LINES = [
    "\"Long day's work, but {location}'s got to eat same as anywhere.\"",
    "\"Not much news out here -- just the same work, day after day.\"",
    "\"You get used to the {biome}, after enough years. Mostly.\"",
]
_HEALER_LINES = [
    "\"You look a little worse for wear. Sit a moment, let me look you over.\"",
    "\"Plenty of folk come through {location} needing patching up. You're not the first.\"",
    "\"Rest when you can. This road doesn't forgive the reckless.\"",
]
_MYSTIC_LINES = [
    "\"The {biome} speaks, if you know how to listen. Most don't.\"",
    "\"I've seen a great many travelers pass through {location}. You've an odd look about you.\"",
    "\"Fate is a strange thread. Yours seems tangled with something big.\"",
    "\"I sense a family torn apart, long ago, by cowards in fine clothes. Perhaps that means something to you.\"",
]
_ENTERTAINER_LINES = [
    "\"Care to hear a tale of {location}? I've a few worth the telling.\"",
    "\"Every town's got a story. This one's got three, if you buy the next round.\"",
    "\"You've the look of someone about to become a story themselves.\"",
]
_GENERIC_LINES = [
    "\"Welcome to {location}, stranger. Mind yourself out there.\"",
    "\"Don't see many new faces around {location}.\"",
    "\"Quiet day here in the {biome}. Suits me fine.\"",
    "\"The King's law forbids what the nobles do to peasant families, but out here, who's left to enforce it?\"",
]
_HOSTILE_LINES = [
    "\"{name} snarls and levels a weapon at you -- there'll be no talking your way out of this.\"",
    "\"{name} bars your path with a cold, hungry look.\"",
    "\"{name} doesn't wait for words before closing the distance.\"",
]
_TELEPATHY_LINES = [
    "they think you're hiding something, and they're not wrong to wonder.",
    "they're far more afraid of the road ahead than they're letting on.",
    "they resent someone in this town, though they'd never say who out loud.",
    "they don't trust you as far as they could throw you -- smart of them.",
    "there's a debt owed to them that's gone unpaid far too long.",
    "they're quietly grateful you didn't ask about the scar.",
    "they know something about the nobles they'd never risk saying aloud.",
]
_CAPTIVE_RESCUE_LINES = [
    "\"{name}! You... you actually came. I'd nearly given up hope of seeing the sky again. Thank you.\"",
    "\"{name} sags with relief. \\\"I owe you my life. Get me out of here, please.\\\"\"",
    "\"{name} wipes their eyes and manages a shaky laugh. \\\"Every hero in the old stories showed up exactly this late. Let's go.\\\"\"",
]
_BOSS_TAUNT_LINES = [
    "\"{name} lets out a bone-deep roar. \\\"None who enter here leave again!\\\"\"",
    "\"{name} sizes you up and grins. \\\"Another fool come to die in my domain.\\\"\"",
    "\"{name} doesn't waste breath on words -- only on the attack that follows.\"",
]

_ARCHETYPE_BANKS = {
    NpcArchetype.TRADER: _TRADER_LINES,
    NpcArchetype.GUIDE: _GUIDE_LINES,
    NpcArchetype.LABORER: _LABORER_LINES,
    NpcArchetype.HEALER: _HEALER_LINES,
    NpcArchetype.MYSTIC: _MYSTIC_LINES,
    NpcArchetype.ENTERTAINER: _ENTERTAINER_LINES,
    NpcArchetype.GENERIC: _GENERIC_LINES,
}


def _fill(template: str, location: str, biome: Biome, name: str = "") -> str:
    return template.replace("{location}", location).replace("{biome}", biome.display_name.lower()).replace("{name}", name)


def civilian_line(npc_name: str, location: str, biome: Biome, rng: random.Random) -> str:
    bank = _ARCHETYPE_BANKS[archetype_for(npc_name)]
    return _fill(rng.choice(bank), location, biome)


def hostile_line(being_name: str, rng: random.Random) -> str:
    return _fill(rng.choice(_HOSTILE_LINES), "", Biome.PLAINS, being_name)


def telepathy_line(rng: random.Random) -> str:
    return rng.choice(_TELEPATHY_LINES)


def captive_rescue_line(captive_name: str, rng: random.Random) -> str:
    return rng.choice(_CAPTIVE_RESCUE_LINES).replace("{name}", captive_name)


def boss_taunt_line(boss_name: str, rng: random.Random) -> str:
    return rng.choice(_BOSS_TAUNT_LINES).replace("{name}", boss_name)


_QUEST_FLAVOR = {
    QuestType.RETRIEVE_ARTIFACT: [
        "Faint runes along the wall warn that only the worthy may claim what lies ahead.",
        "Old bloodstains on the floor suggest you're not the first to come looking for it.",
    ],
    QuestType.DEFEAT_GUARDIAN: [
        "The air grows heavier the deeper you go, thick with something ancient and territorial.",
        "Claw marks score the walls, each one deep enough to fit a finger.",
    ],
    QuestType.RESCUE_CAPTIVE: [
        "A faint, ragged voice calls for help somewhere deeper in.",
        "Scraps of torn cloth mark a trail further into the dark.",
    ],
}


def quest_flavor_line(type_: QuestType, rng: random.Random) -> str:
    return rng.choice(_QUEST_FLAVOR[type_])
