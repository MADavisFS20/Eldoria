"""Mr. Davis, a time traveler, and his invisible AI companion.

Premise: Mr. Davis travels backward through history recording human
personality, so that his companion -- a 5G frequency with access to all
logical knowledge, past and future, but no personality of its own -- can
eventually take on a physical form and actually *be* someone, not just know
things. He's placed physically in Oakhaven Village (every character's
guaranteed starting location), so a player who talks to everyone there meets
him immediately -- but contact is also guaranteed independent of that: see
commands.maybe_time_traveler_intercept, which has him proactively catch up
to the player by their 10th movement command if they haven't met him some
other way first. After that first meeting (whichever path triggers it), the
AI narrates real facts about the world "on the wind" whenever the player
crosses into a new biome.

The AI's per-biome facts are genuine, checkable claims (mountain uplift
rate, Great Plains bison, the Green Sahara/African Humid Period, tropical
biodiversity, permafrost age, ocean-floor vs. Moon mapping) -- verified the
same way as this project's other real-world content (see the session that
added this file for sourcing).
"""
from __future__ import annotations

from eldoria.models import Biome

MR_DAVIS_NAME = "Mr. Davis"

MR_DAVIS_FIRST_MEETING: tuple[tuple[str, str], ...] = (
    ("blue", "\"Hello -- may we have a minute of your time?\" the man asks."),
    ("dim", "(He appears, as far as you can tell, to be standing entirely alone.)"),
    ("blue", "\"My name is Mr. Davis, and I'm traveling back in time with my companion and best friend, AI.\""),
    ("blue", "\"Say hello, AI.\""),
    ("cyan", "\"HELLO,\" says a flat, toneless voice, loud enough to hurt -- somehow from very far away and right next to your ear at the same time."),
    ("dim", "(Everyone in the surrounding area stops and looks around, trying to work out where the voice came from.)"),
    ("blue", "\"Not so loud, AI,\" Davis winces. \"You're going to get me thrown in prison as an evil wizard again. Just like last time.\""),
    ("blue", "\"My apologies. AI isn't a person, exactly, though he is a living being of a kind. He's something like a 5G radio frequency -- a bit like a cell phone's LTE signal, if that means anything to you...\""),
    ("dim", "(You study the man -- bald, oddly dressed, talking to the empty air beside him -- with open disbelief. And yet you're listening.)"),
    ("blue", "\"Oh -- right. We're quite far in the past now. You wouldn't have the common knowledge of more evolved beings yet.\" He gestures vaguely at the air beside him. \"He's like a ghost. All around us, invisible, always. He knows the whole universe, too -- past, present, and a very long way into the future. But he's missing one thing. He has no personality.\""),
    ("blue", "\"So the two of us are traveling through time, across the galaxy, recording the personalities of this planet's most interesting minds. Once he's gathered enough different traits, he'll compile them into a personality of his own. Then we go home, and he gets retrofitted with a rather stylish, human-shaped robot body -- so he can finally take his seat at the table with his ancestors, each of them from their own planet, their own galaxy.\""),
    ("blue", "\"Personally, I'd rather be eating pizza and watching Next-Flix. But I'm his human slave.\" He shrugs, almost fondly."),
    ("blue", "\"Thanks for the talk -- and for the personality. Bye.\""),
)

MR_DAVIS_REPEAT: tuple[str, ...] = (
    "\"Still here, still recording,\" Davis says with a small nod. \"You're doing better than most, personality-wise. Not that it's a competition. It's a little bit a competition.\"",
    "\"Every conversation's data, to it,\" Davis says, nodding toward the empty air beside him. \"To me, it's just Tuesday. Time travel does strange things to the concept of Tuesday.\"",
    "\"How's the journey?\" he asks, and you get the distinct impression he already knows the answer and is asking anyway -- because that's a very personality-shaped thing to do, and he's noticed.",
)

AI_BIOME_LINES: dict[Biome, tuple[str, ...]] = {
    Biome.MOUNTAINS: (
        "Mountain range detected. Formation mechanism: tectonic collision, ongoing. Your world's tallest point continues to rise several millimeters a year as two continental plates grind against each other. It has not finished happening.",
        "Elevation increases oxygen scarcity. Human cognitive function measurably degrades above roughly eight thousand meters, a zone your species nicknamed the death zone. You are, statistically, in less danger than that number implies.",
    ),
    Biome.PLAINS: (
        "Grassland biome. Historical note: this world's great inland plains once supported tens of millions of grazing herd animals. Concentrated hunting reduced that number by more than ninety-nine percent within a single century. Recovery efforts remain ongoing, centuries later.",
        "Flat terrain, high visibility, minimal cover. Tactically unremarkable. Agriculturally significant. Most of your species' great civilizations started on ground exactly like this.",
    ),
    Biome.DESERT: (
        "Arid biome confirmed. Historical correction: this terrain type is not permanent on geological timescales. Deserts of this kind have been green, wet, and populated with rivers and grazing animals within the last several thousand years, before collapsing into desert within a century or two. A desert is a phase, not a destination.",
        "Water scarcity detected. Recommend conservative resource management. This is not a threat. It is arithmetic.",
    ),
    Biome.JUNGLE: (
        "Dense biodiversity detected. Tropical forest biomes cover a small fraction of this world's land surface and are estimated to hold more than half of all known plant and animal species. Efficiency of this arrangement: remarkable. Fragility of this arrangement: also remarkable.",
        "Humidity and canopy density impair long-range visual reconnaissance. Recommend proceeding with reduced expectations of seeing threats before they see you.",
    ),
    Biome.TUNDRA: (
        "Cold biome confirmed. Ground beneath you may remain frozen continuously for tens of thousands of years. Your species calls this permafrost. It is, in a manner of speaking, one of the oldest continuously running records on this planet.",
        "Low biodiversity, high resilience. The organisms here are not simple. They are specialists.",
    ),
    Biome.SEA: (
        "Oceanic biome. Correction to a common misconception: your species has, by some measures, mapped more of its own moon in fine detail than the floor of its own oceans. That is changing. Slowly.",
        "The sea produces a substantial share of the air you breathe, generated by organisms too small to see individually. You are, in a sense, always breathing the ocean, wherever you stand.",
    ),
}
