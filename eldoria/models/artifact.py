"""Three impossible pieces of technology, each hidden in a single far-flung spot in the world.

Deliberately anachronistic against the rest of the hardcoded medieval-fantasy
content. Picking one up auto-activates it permanently; it never sits in
inventory and can't be sold or lost.
"""
from __future__ import annotations

from enum import Enum


class ArtifactKind(Enum):
    TELEPATH_DEVICE = (
        "Neural Resonance Circlet",
        "A thin band of some impossible dark alloy, warm to the touch, humming faintly even in dead silence.",
        "The moment it touches your skin it dissolves into your temple in a flash of cold light. Suddenly the "
        "world is louder -- not with sound, but with something underneath it. You can hear what people are thinking.",
        True, 0, 0, 0,
    )
    COERCION_DEVICE = (
        "Neural Static Emitter",
        "A small device of matte black plating and blinking amber light, utterly unlike anything a blacksmith could forge.",
        "It fuses seamlessly into your palm, invisible beneath the skin. You flex your hand and feel something "
        "new there -- a needle of pain you can point at anyone you choose, and they will never know where it came from.",
        False, 20, 0, 0,
    )
    PRECOGNITION_DEVICE = (
        "Chronal Lattice Implant",
        "A lattice of impossibly thin wire folded into a shape that hurts to look at directly, as if it exists half a second before it should.",
        "It sinks into your chest without leaving a mark. For one instant you see everything about to happen -- "
        "then it's gone, but the feeling isn't. You'll always be just a heartbeat ahead of what comes next.",
        False, 0, 2, 2,
    )

    def __init__(
        self,
        item_name: str,
        lore: str,
        activation_line: str,
        telepathy: bool,
        trade_discount_percent: int,
        attack_bonus: int,
        armor_class_bonus: int,
    ):
        self.item_name = item_name
        self.lore = lore
        self.activation_line = activation_line
        self.telepathy = telepathy
        self.trade_discount_percent = trade_discount_percent
        self.attack_bonus = attack_bonus
        self.armor_class_bonus = armor_class_bonus
