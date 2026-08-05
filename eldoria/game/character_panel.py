"""The bordered "side window" character sheet, plus structured data for the web side panel."""
from __future__ import annotations

from eldoria.data import finance_lore
from eldoria.models import PlayerCharacter
from eldoria.world import level_progression

_WIDTH = 46


def _bar(current: int, maximum: int, width: int = 20) -> str:
    filled = 0 if maximum <= 0 else max(0, min(width, int((current / maximum) * width)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _line(s: str) -> str:
    pad = max(0, _WIDTH - len(s))
    return f"| {s}{' ' * pad} |"


def render(player: PlayerCharacter) -> str:
    border = "+" + "-" * (_WIDTH + 2) + "+"
    lines = [border]
    subclass_tag = f"  [{player.subclass.display_name}]" if player.subclass else ""
    gills_tag = "  [Gilled]" if player.has_gills else ""
    lines.append(_line(f"{player.name} the {player.race.display_name} {player.character_class.display_name}  (Lv{player.level}){subclass_tag}{gills_tag}"))
    lines.append(_line(f"Reputation: {player.reputation_title} ({player.reputation})"))
    lines.append(_line(f"HP {_bar(player.current_health, player.max_health)} {player.current_health}/{player.max_health}"))
    lines.append(_line(f"SP {_bar(player.current_stamina, player.max_stamina)} {player.current_stamina}/{player.max_stamina}"))
    xp_needed = level_progression.xp_to_next_level(player.level)
    lines.append(_line(f"XP {_bar(player.experience, xp_needed)} {player.experience}/{xp_needed}"))
    lines.append(_line(f"STR {player.strength}  AGI {player.agility}  WIL {player.willpower}"))
    atk_sign = "+" if player.attack_bonus >= 0 else ""
    lines.append(_line(f"AC {player.armor_class}   SPD {player.speed}   ATK {atk_sign}{player.attack_bonus}"))
    lines.append(_line(f"Gold: {player.gold}g"))
    lines.append(_line("-" * _WIDTH))
    lines.append(_line(f"Weapon:  {player.equipped_weapon.name if player.equipped_weapon else 'none'} " + (f"({player.equipped_weapon.damage})" if player.equipped_weapon and player.equipped_weapon.damage else "")))
    lines.append(_line(f"Chest:   {player.equipped_armor.name if player.equipped_armor else 'none'} " + (f"(+{player.equipped_armor.armor_class_bonus} AC)" if player.equipped_armor and player.equipped_armor.armor_class_bonus else "")))
    lines.append(_line(f"Offhand: {player.equipped_offhand.name if player.equipped_offhand else 'none'} " + (f"(+{player.equipped_offhand.armor_class_bonus} AC)" if player.equipped_offhand and player.equipped_offhand.armor_class_bonus else "")))
    lines.append(_line(f"Head:    {player.equipped_head.name if player.equipped_head else 'none'} " + (f"(+{player.equipped_head.armor_class_bonus} AC)" if player.equipped_head and player.equipped_head.armor_class_bonus else "")))
    lines.append(_line(f"Ring:    {player.equipped_ring.name if player.equipped_ring else 'none'} " + (f"({player.equipped_ring.magic_effect.name})" if player.equipped_ring and player.equipped_ring.magic_effect else "")))
    lines.append(_line(f"Amulet:  {player.equipped_amulet.name if player.equipped_amulet else 'none'} " + (f"({player.equipped_amulet.magic_effect.name})" if player.equipped_amulet and player.equipped_amulet.magic_effect else "")))
    lines.append(_line("-" * _WIDTH))
    top_skills = sorted(player.skills.values(), key=lambda s: s.level, reverse=True)[:6]
    lines.append(_line("Top skills:"))
    for s in top_skills:
        lines.append(_line(f"  {s.type.display_name}: {s.level}"))
    if player.perks:
        lines.append(_line("-" * _WIDTH))
        perks_str = ", ".join(f"{perk.display_name} x{rank}" if rank > 1 else perk.display_name for perk, rank in player.perks.items())
        lines.append(_line(f"Perks: {perks_str}"))
    if player.pending_perk_choices > 0:
        lines.append(_line(f"Perk choices available: {player.pending_perk_choices} (use 'perk')"))
    if player.artifacts:
        lines.append(_line("-" * _WIDTH))
        lines.append(_line("Artifacts: " + ", ".join(a.item_name for a in player.artifacts)))
    if player.companion is not None:
        lines.append(_line("-" * _WIDTH))
        revive_note = " (revive used)" if player.companion.revive_used else " (can revive you once)"
        lines.append(_line(f"Companion: {player.companion.name}{revive_note}"))
    lines.append(border)
    return "\n".join(lines)


def render_inventory(player: PlayerCharacter) -> str:
    border = "+" + "-" * (_WIDTH + 2) + "+"
    lines = [border, _line("Inventory"), _line("-" * _WIDTH)]
    if not player.inventory:
        lines.append(_line("(empty)"))
    else:
        equipped_items = {i for i in (player.equipped_weapon, player.equipped_armor, player.equipped_offhand, player.equipped_head, player.equipped_ring, player.equipped_amulet) if i is not None}
        for item in player.inventory:
            equipped = " [equipped]" if item in equipped_items else ""
            lines.append(_line(f"{item.name}{equipped} -- {item.value}g"))
    if player.materials:
        lines.append(_line("-" * _WIDTH))
        lines.append(_line("Materials:"))
        for name, count in player.materials.items():
            lines.append(_line(f"  {name} x{count}"))
    lines.append(border)
    return "\n".join(lines)


def sheet_data(player: PlayerCharacter) -> dict:
    """Structured character sheet for the web side panel."""
    xp_needed = level_progression.xp_to_next_level(player.level)

    def item_summary(item):
        if item is None:
            return None
        return {
            "name": item.name,
            "damage": str(item.damage) if item.damage else None,
            "armor_class_bonus": item.armor_class_bonus,
            "magic_effect": item.magic_effect.name if item.magic_effect else None,
            "magic_effect_note": finance_lore.MAGIC_EFFECT_NOTES.get(item.magic_effect.name) if item.magic_effect else None,
            "is_compounding": item.is_compounding,
        }

    return {
        "name": player.name,
        "race": player.race.display_name,
        "character_class": player.character_class.display_name,
        "level": player.level,
        "subclass": player.subclass.display_name if player.subclass else None,
        "has_gills": player.has_gills,
        "reputation": player.reputation,
        "reputation_title": player.reputation_title,
        "current_health": player.current_health,
        "max_health": player.max_health,
        "current_stamina": player.current_stamina,
        "max_stamina": player.max_stamina,
        "experience": player.experience,
        "xp_needed": xp_needed,
        "strength": player.strength,
        "agility": player.agility,
        "willpower": player.willpower,
        "armor_class": player.armor_class,
        "speed": player.speed,
        "attack_bonus": player.attack_bonus,
        "gold": player.gold,
        "equipped": {
            "weapon": item_summary(player.equipped_weapon),
            "armor": item_summary(player.equipped_armor),
            "offhand": item_summary(player.equipped_offhand),
            "head": item_summary(player.equipped_head),
            "ring": item_summary(player.equipped_ring),
            "amulet": item_summary(player.equipped_amulet),
        },
        "top_skills": [{"name": s.type.display_name, "level": s.level} for s in sorted(player.skills.values(), key=lambda s: s.level, reverse=True)[:6]],
        "perks": [{"name": perk.display_name, "rank": rank} for perk, rank in player.perks.items()],
        "pending_perk_choices": player.pending_perk_choices,
        "artifacts": [a.item_name for a in player.artifacts],
        "companion": {"name": player.companion.name, "revive_used": player.companion.revive_used} if player.companion else None,
        "owned_boat": item_summary(player.owned_boat) if player.owned_boat else None,
        "bank_gold": player.bank_gold,
        "properties": [
            {
                "location_name": p.location_name,
                "condition": p.condition,
                "status": "condemned" if p.is_condemned else (f"rented to {p.tenant_name}" if p.is_occupied else "vacant"),
                "lifetime_rent_collected": p.lifetime_rent_collected,
            }
            for p in player.owned_properties
        ],
        "businesses": [
            {
                "name": b.name,
                "location_name": b.location_name,
                "business_type": b.business_type,
                "ownership_percent": b.ownership_percent,
                "is_fully_owned": b.is_fully_owned,
                "is_failed": b.is_failed,
                "manager_name": b.manager_name,
                "manager_quality": b.manager_quality if b.manager_revealed else None,
                "lifetime_profit_collected": b.lifetime_profit_collected,
                "lifetime_losses": b.lifetime_losses,
            }
            for b in player.owned_businesses
        ],
    }


def inventory_data(player: PlayerCharacter) -> dict:
    equipped_items = {i for i in (player.equipped_weapon, player.equipped_armor, player.equipped_offhand, player.equipped_head, player.equipped_ring, player.equipped_amulet) if i is not None}
    return {
        "items": [
            {"name": i.name, "value": i.value, "equipped": i in equipped_items, "kind": i.kind.name}
            for i in player.inventory
        ],
        "materials": [{"name": name, "count": count} for name, count in player.materials.items()],
    }
