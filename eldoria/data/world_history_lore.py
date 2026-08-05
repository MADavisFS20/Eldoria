"""Real-world history, woven into moments that already make thematic sense in Eldoria.

Every fact below is a genuine, checkable claim -- verified against Britannica,
the Smithsonian, HISTORY.com, the American Physical Society, and similar
sources (see the session that added this file for the actual research).
Each persona/topic maps onto an existing game moment rather than a new one:
 - Archimedes' buoyancy principle -> repairing a boat (world/real_estate-style
   flavor hook in commands.repair_boat).
 - The Library of Alexandria + Eratosthenes -> the Ancient Scholar NPC, who
   already lives among ruins in the home region.
 - Leif Erikson and the Vikings in North America -> a rare peaceful sighting
   while sailing.
 - Ada Lovelace and Charles Babbage's Analytical Engine -> enchanting an item
   (programming an engine to do something new is the closest real-world
   parallel to enchanting a mundane object).
 - The Antikythera mechanism -> the world's existing sunken-treasure finds.
Collected via `session.chronicle_discovered`; review with the `chronicle` command.
"""
from __future__ import annotations

ARCHIMEDES_KEY = "archimedes"
ARCHIMEDES_TITLE = "Archimedes of Syracuse"
ARCHIMEDES_FACTS: tuple[str, ...] = (
    "\"Funny thing about a hull settling into water,\" the shipwright mutters, running a hand along the repaired planks. \"An old Syracusan named Archimedes worked out why, stepping into his bath one day -- the water that spills over weighs exactly as much as the part of you that's underneath it. He's said to have gone running through the streets shouting 'Eureka!' -- 'I have found it!' -- not even dressed for the occasion.\"",
    "\"Archimedes used that same principle to catch a cheating goldsmith,\" the shipwright adds. \"The king's new crown was supposed to be pure gold, but gold and silver displace water differently for the same weight. Dunk both, compare the overflow -- no scale needed, no melting it down. The goldsmith had indeed cut it with silver.\"",
    "\"That same mind built a screw that could lift water uphill, coiled inside a tube -- they still call it the Archimedes screw, and it's still used today, near two thousand years on,\" the shipwright says. \"Died defending his home city of Syracuse from the Romans, they say, still scratching diagrams in the sand when the soldier found him.\"",
)

LIBRARY_KEY = "library_of_alexandria"
LIBRARY_TITLE = "The Great Library of Alexandria"
LIBRARY_FACTS: tuple[str, ...] = (
    "\"There was once a library, in a city called Alexandria, that tried to hold every scroll ever written,\" the scholar says, eyes distant. \"Founded in the third century before your reckoning. Perhaps four hundred thousand scrolls, at its height. Scholars came from every civilization that had ships to reach it.\"",
    "\"No single fire took it,\" the scholar continues. \"That's the story people like, but it isn't the true one. It faded over centuries -- neglect, funding cut, a war here, a riot there. Julius Caesar's own soldiers likely burned part of it by accident in 48 BC, setting fire to ships in the harbor that spread to the docks. The rest just... wasted away.\"",
    "\"Its chief librarian once was a man named Eratosthenes,\" the scholar says, brightening. \"He measured the entire girth of the world without ever leaving Egypt -- compared how a shadow fell at noon in two cities a known distance apart, and did the arithmetic. Off by less than a tenth from the true number, and this was over two thousand years before anyone circled the globe to check him.\"",
)

VIKING_KEY = "leif_erikson"
VIKING_TITLE = "Leif Erikson and Vinland"
VIKING_FACTS: tuple[str, ...] = (
    "Through the fog off the bow, for just a moment, you could swear you see it: a long, low ship with a single striped sail and a dragon's head at the prow, gone again before you can point it out to anyone.",
    "It puts you in mind of an old sailor's tale -- of a Norseman named Leif Erikson who sailed west from Greenland around the year 1000 and found a green, wild land he called Vinland, for the grapes growing there. Five hundred years before anyone thought to call it a New World.",
    "Centuries later, someone finally dug up the proof: a real Norse settlement at a place called L'Anse aux Meadows, on an island called Newfoundland, dated to right around the year 1021. It didn't last two winters -- but it was real, and it was first.",
)

LOVELACE_KEY = "ada_lovelace"
LOVELACE_TITLE = "Ada Lovelace and the Analytical Engine"
LOVELACE_FACTS: tuple[str, ...] = (
    "As the enchantment settles into the item, a thought strikes you, unbidden and oddly clear: the hardest part was never the magic. It was writing down, in order, precisely what the magic should do -- and in what sequence -- before it ever happened.",
    "It reminds you of a story about a woman named Ada Lovelace, a mathematician who, in the 1840s, wrote out a full set of instructions for a machine that was never even built -- Charles Babbage's Analytical Engine. Historians now call it the first computer program in the world, roughly a century before any machine existed that could actually run one.",
    "Lovelace saw further than the machine itself, too -- she wrote that such an engine could work on more than just numbers, on any symbols at all, if you told it how. That single idea is most of what a modern engine, magical or otherwise, actually is.",
)

ANTIKYTHERA_KEY = "antikythera_mechanism"
ANTIKYTHERA_TITLE = "The Antikythera Mechanism"
ANTIKYTHERA_FACTS: tuple[str, ...] = (
    "Wedged into the treasure, corroded almost past recognizing, is something that stops you cold: a fist-sized lump of bronze gearwork, dozens of interlocking teeth, clearly built to turn as one.",
    "It's the twin of something real: the Antikythera mechanism, pulled from a Greek shipwreck in 1901 by sponge divers who had no idea what they'd found. Built somewhere around 200 BC, over thirty precisely cut bronze gears inside a hand-sized case.",
    "No one built anything with that many interlocking gears again for over a thousand years. It tracked the sun, the moon, the planets, and could predict eclipses -- and even the dates of the Olympic Games -- decades ahead. People now just call it the world's first analog computer.",
)

ALL_CHRONICLE_ENTRIES: dict[str, tuple[str, tuple[str, ...]]] = {
    ARCHIMEDES_KEY: (ARCHIMEDES_TITLE, ARCHIMEDES_FACTS),
    LIBRARY_KEY: (LIBRARY_TITLE, LIBRARY_FACTS),
    VIKING_KEY: (VIKING_TITLE, VIKING_FACTS),
    LOVELACE_KEY: (LOVELACE_TITLE, LOVELACE_FACTS),
    ANTIKYTHERA_KEY: (ANTIKYTHERA_TITLE, ANTIKYTHERA_FACTS),
}
