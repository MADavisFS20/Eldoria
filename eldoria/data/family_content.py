"""The game's main-quest premise: the player was taken from their family as a child by the Kingdom's nobles.

One relation is picked deterministically per world seed and placed as a
single findable NPC in one countryside village. The other three are
revealed, already safe and waiting, in the endgame reunion scene.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FamilyRelation:
    relation: str
    name: str


@dataclass(frozen=True)
class Noble:
    title: str
    name: str


CANDIDATES: tuple[FamilyRelation, ...] = (
    FamilyRelation("mother", "Elara"),
    FamilyRelation("father", "Bran"),
    FamilyRelation("sister", "Wren"),
    FamilyRelation("brother", "Toma"),
)

REUNION_LINES: tuple[str, ...] = (
    "\"{name} freezes, then drops what they're holding. \\\"...it's you. After all these years, it's really you.\\\"\"",
    "\"{name}'s eyes fill with tears. \\\"I never stopped looking. I never stopped hoping. Come here.\\\"\"",
    "\"{name} pulls you into an embrace before you've said a single word. \\\"The nobles took you from us, but they couldn't take this.\\\"\"",
)

# The three nobles responsible for the theft, fought in order of ascending menace in the final battle.
NOBLES: tuple[Noble, ...] = (
    Noble("Mistress of Whispers", "Lady Seraphine Vex"),
    Noble("Warden of the Silent Decree", "Lord Malvorn Ashgrave"),
    Noble("the Iron Regent", "Duke Corvin Blackthorne"),
)

GRAND_REUNION_SCENE: str = (
    "Word reaches you before you've even had time to catch your breath from the last battle: a caravan,\n"
    "quiet and unannounced, has arrived. And there, stepping down from it, are the faces you gave up\n"
    "hoping to see -- your mother, your father, your sister, all of them, drawn by whispers that a child\n"
    "stolen long ago had returned to fight for a kingdom that once turned its back on them.\n"
    "\n"
    "You are not looking for your family anymore. For the first time since you were a child, your family\n"
    "is looking at you, and none of you can say a word."
)

THRONE_CALL_TO_ACTION: str = (
    "But reunion is not the end of it. The nobles who tore your family apart still sit comfortably above\n"
    "the law they broke -- Lady Seraphine Vex, Lord Malvorn Ashgrave, and Duke Corvin Blackthorne, the\n"
    "Iron Regent himself. Every quest you have completed, every monster you've put down, has been a\n"
    "step toward this. Your family did not come to say goodbye. They came to watch you finish it.\n"
    "\n"
    "Type 'confront' when you are ready to march on the throne room."
)

# Flavor for each noble going down in the sequential final fight -- normal combat, not the scripted finish.
NOBLE_FALL_LINES: tuple[str, ...] = (
    "\"{name} staggers, crown of authority slipping from a face that never once looked at a peasant with pity.\"",
    "\"{name} collapses, the last of their borrowed power draining out with the blood.\"",
    "\"{name} falls to their knees. \\\"This throne was never meant to answer to the likes of you--\\\" It's the last thing they say.\"",
)

# The scripted, automatic finishing blow on the third and final noble -- NOT a normal dice-rolled attack.
FINAL_STRIKE_LINES: tuple[str, ...] = (
    (
        "Something rises in you that no trainer ever taught and no dungeon ever tested -- not strength, not\n"
        "steel, not a spell drilled into memory, but something that was simply always there, waiting. It\n"
        "floods up through you like a held breath finally released, and without a single conscious thought\n"
        "you move, and light that answers to no school of magic you have ever learned pours out of you and\n"
        "through {name}, and the Iron Regent's reign ends between one heartbeat and the next."
    ),
    (
        "You don't decide to strike. Your body simply remembers something your mind never learned -- a warmth\n"
        "welling up from somewhere under the ribs, old as a mother's arms, old as a father's hands, old as a\n"
        "sister's laugh -- and it becomes light, and the light becomes a blow that {name} never sees coming\n"
        "and never survives."
    ),
)

VICTORY_EPILOGUE: str = (
    "The throne room falls silent. You stand over the last of the three nobles who broke the king's own\n"
    "law to steal children from their families, and you feel -- not triumph, not even relief, but\n"
    "something quieter. That strike didn't come from any skill you trained or any weapon you carried.\n"
    "It came from the same place your family had been all along: not lost, not waiting to be found in\n"
    "some far village, but carried with you the entire time, in your heart, in every step of this\n"
    "journey, whether you knew it or not.\n"
    "\n"
    "You had been searching the whole kingdom for something that never once left you.\n"
    "\n"
    "=== THE END ==="
)
