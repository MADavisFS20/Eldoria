"""Trader NPCs sell a small, deterministic stock of tier-appropriate generic gear.

Generated on the fly from the same stat_generator dice formulas everything
else uses, seeded off the trader's name and location so the same merchant
always has the same stock in the same playthrough.
"""
from __future__ import annotations

from eldoria.models import Item, ItemKind
from eldoria.world import stat_generator as sg
from eldoria.world.deterministic_random import make_random, string_hash

_WEAPON_NAMES = ["Traveler's Sword", "Worn Hand Axe", "Hunting Bow", "Iron Mace", "Simple Dagger", "Oak Quarterstaff"]
_ARMOR_NAMES = ["Traveler's Vest", "Reinforced Buckler", "Padded Jerkin", "Riveted Cuirass", "Simple Hood", "Worn Chainmail"]
_OFFHAND_NAMES = ["Worn Buckler", "Iron Targe", "Reinforced Kite Shield"]
_HEAD_NAMES = ["Leather Cap", "Iron Skullcap", "Traveler's Hood"]
_RING_NAMES = ["Simple Band", "Engraved Signet Ring", "Weathered Ring"]
_AMULET_NAMES = ["Plain Pendant", "Carved Bone Amulet", "Silver Locket"]


def healing_draught(tier: int) -> Item:
    """A tier-scaled potion, restores heal_amount health on use (see commands.use_item)."""
    heal = 10 + tier * 8
    return Item(name="Healing Draught", kind=ItemKind.CONSUMABLE, tier=tier, value=10 + tier * 5, max_durability=1, heal_amount=heal)


def inventory_for(trader_name: str, location_id: str, tier: int, world_seed: int) -> list[Item]:
    rng = make_random(world_seed, string_hash(trader_name), string_hash(location_id), 555)
    count = rng.randint(3, 5)
    items: list[Item] = []
    for _ in range(count):
        roll = rng.randrange(7)
        if roll in (0, 1):
            items.append(sg.weapon_item(rng.choice(_WEAPON_NAMES), tier, rng))
        elif roll in (2, 3):
            items.append(sg.armor_item(rng.choice(_ARMOR_NAMES), tier, rng))
        elif roll == 4:
            if rng.choice([True, False]):
                items.append(sg.armor_item(rng.choice(_OFFHAND_NAMES), tier, rng, slot=ItemKind.OFFHAND))
            else:
                items.append(sg.armor_item(rng.choice(_HEAD_NAMES), tier, rng, slot=ItemKind.HEAD))
        elif roll == 5:
            if rng.choice([True, False]):
                items.append(sg.accessory_item(rng.choice(_RING_NAMES), tier, rng, slot=ItemKind.RING))
            else:
                items.append(sg.accessory_item(rng.choice(_AMULET_NAMES), tier, rng, slot=ItemKind.AMULET))
        else:
            items.append(healing_draught(tier))
    return items


def sell_back_price(item: Item, bonus_percent: int) -> int:
    """Price a merchant pays the player -- base 50% of value, plus bonus_percent (capped 95%)."""
    return max(1, int(item.value * min(50 + bonus_percent, 95) / 100.0))


def buy_price(item: Item, discount_percent: int) -> int:
    """Price the player pays to buy -- discount_percent stacks the same way, in the buyer's favor."""
    return max(1, int(item.value * max(100 - discount_percent, 5) / 100.0))
