"""Plain-dict (JSON-ready) encoding for the model types that need to survive a save/load round trip.

Hand-written rather than a generic dataclass/enum walker, mirroring what the
old Kotlin engine got for free from kotlinx.serialization -- only the shapes
actually reachable from PlayerCharacter/Snapshot need a case here.
"""
from __future__ import annotations

from eldoria.models import (
    ArtifactKind,
    Business,
    CharacterClass,
    DiceFormula,
    DieType,
    HiredCompanion,
    Item,
    ItemKind,
    MagicEffect,
    Perk,
    PlayerCharacter,
    Race,
    RentalProperty,
    Skill,
    SkillType,
    StatusEffect,
    Subclass,
)


def dice_to_dict(d: DiceFormula) -> dict:
    return {"count": d.count, "die": d.die.name, "modifier": d.modifier}


def dice_from_dict(d: dict) -> DiceFormula:
    return DiceFormula(d["count"], DieType[d["die"]], d["modifier"])


def magic_effect_to_dict(m: MagicEffect | None) -> dict | None:
    if m is None:
        return None
    return {"name": m.name, "affected_trait": m.affected_trait, "magnitude": m.magnitude, "beneficial": m.beneficial}


def magic_effect_from_dict(d: dict | None) -> MagicEffect | None:
    if d is None:
        return None
    return MagicEffect(d["name"], d["affected_trait"], d["magnitude"], d["beneficial"])


def item_to_dict(i: Item | None) -> dict | None:
    if i is None:
        return None
    return {
        "name": i.name,
        "kind": i.kind.name,
        "tier": i.tier,
        "value": i.value,
        "max_durability": i.max_durability,
        "damage": dice_to_dict(i.damage) if i.damage else None,
        "armor_class_bonus": i.armor_class_bonus,
        "magic_effect": magic_effect_to_dict(i.magic_effect),
        "current_durability": i.current_durability,
        "is_legendary": i.is_legendary,
        "has_cannons": i.has_cannons,
        "inflicts_status": i.inflicts_status.name if i.inflicts_status else None,
        "is_compounding": i.is_compounding,
    }


def item_from_dict(d: dict | None) -> Item | None:
    if d is None:
        return None
    return Item(
        name=d["name"],
        kind=ItemKind[d["kind"]],
        tier=d["tier"],
        value=d["value"],
        max_durability=d["max_durability"],
        damage=dice_from_dict(d["damage"]) if d.get("damage") else None,
        armor_class_bonus=d.get("armor_class_bonus"),
        magic_effect=magic_effect_from_dict(d.get("magic_effect")),
        current_durability=d.get("current_durability"),
        is_legendary=d.get("is_legendary", False),
        has_cannons=d.get("has_cannons", False),
        inflicts_status=StatusEffect[d["inflicts_status"]] if d.get("inflicts_status") else None,
        is_compounding=d.get("is_compounding", False),
    )


def companion_to_dict(c: HiredCompanion | None) -> dict | None:
    if c is None:
        return None
    return {
        "name": c.name,
        "attack_bonus": c.attack_bonus,
        "armor_class": c.armor_class,
        "damage": dice_to_dict(c.damage),
        "origin_location_id": c.origin_location_id,
        "hired_at_millis": c.hired_at_millis,
        "revive_used": c.revive_used,
    }


def companion_from_dict(d: dict | None) -> HiredCompanion | None:
    if d is None:
        return None
    return HiredCompanion(
        name=d["name"],
        attack_bonus=d["attack_bonus"],
        armor_class=d["armor_class"],
        damage=dice_from_dict(d["damage"]),
        origin_location_id=d["origin_location_id"],
        hired_at_millis=d["hired_at_millis"],
        revive_used=d.get("revive_used", False),
    )


def property_to_dict(prop: RentalProperty) -> dict:
    return {
        "location_id": prop.location_id,
        "location_name": prop.location_name,
        "purchase_price": prop.purchase_price,
        "condition": prop.condition,
        "tenant_name": prop.tenant_name,
        "tenant_quality": prop.tenant_quality,
        "last_event_tick": prop.last_event_tick,
        "lifetime_rent_collected": prop.lifetime_rent_collected,
        "lifetime_repair_spent": prop.lifetime_repair_spent,
        "cycles_vacant_streak": prop.cycles_vacant_streak,
    }


def property_from_dict(d: dict) -> RentalProperty:
    return RentalProperty(
        location_id=d["location_id"],
        location_name=d["location_name"],
        purchase_price=d["purchase_price"],
        condition=d.get("condition", 100),
        tenant_name=d.get("tenant_name"),
        tenant_quality=d.get("tenant_quality"),
        last_event_tick=d.get("last_event_tick", 0),
        lifetime_rent_collected=d.get("lifetime_rent_collected", 0),
        lifetime_repair_spent=d.get("lifetime_repair_spent", 0),
        cycles_vacant_streak=d.get("cycles_vacant_streak", 0),
    )


def business_to_dict(biz: Business) -> dict:
    return {
        "id": biz.id,
        "location_id": biz.location_id,
        "location_name": biz.location_name,
        "name": biz.name,
        "business_type": biz.business_type,
        "investment": biz.investment,
        "ownership_percent": biz.ownership_percent,
        "manager_name": biz.manager_name,
        "manager_quality": biz.manager_quality,
        "manager_revealed": biz.manager_revealed,
        "manager_cycles_observed": biz.manager_cycles_observed,
        "last_event_tick": biz.last_event_tick,
        "lifetime_profit_collected": biz.lifetime_profit_collected,
        "lifetime_losses": biz.lifetime_losses,
        "is_failed": biz.is_failed,
    }


def business_from_dict(d: dict) -> Business:
    return Business(
        id=d["id"],
        location_id=d["location_id"],
        location_name=d["location_name"],
        name=d["name"],
        business_type=d["business_type"],
        investment=d["investment"],
        ownership_percent=d["ownership_percent"],
        manager_name=d.get("manager_name"),
        manager_quality=d.get("manager_quality"),
        manager_revealed=d.get("manager_revealed", False),
        manager_cycles_observed=d.get("manager_cycles_observed", 0),
        last_event_tick=d.get("last_event_tick", 0),
        lifetime_profit_collected=d.get("lifetime_profit_collected", 0),
        lifetime_losses=d.get("lifetime_losses", 0),
        is_failed=d.get("is_failed", False),
    )


def player_to_dict(p: PlayerCharacter) -> dict:
    return {
        "name": p.name,
        "race": p.race.name,
        "character_class": p.character_class.name,
        "level": p.level,
        "experience": p.experience,
        "strength": p.strength,
        "agility": p.agility,
        "willpower": p.willpower,
        "max_health": p.max_health,
        "current_health": p.current_health,
        "max_stamina": p.max_stamina,
        "current_stamina": p.current_stamina,
        "armor_class": p.armor_class,
        "speed": p.speed,
        "attack_bonus": p.attack_bonus,
        "unarmed_damage": dice_to_dict(p.unarmed_damage),
        "skills": {s.type.name: {"level": s.level, "xp": s.xp} for s in p.skills.values()},
        "gold": p.gold,
        "inventory": [item_to_dict(i) for i in p.inventory],
        "equipped_weapon": item_to_dict(p.equipped_weapon),
        "equipped_armor": item_to_dict(p.equipped_armor),
        "equipped_offhand": item_to_dict(p.equipped_offhand),
        "equipped_head": item_to_dict(p.equipped_head),
        "equipped_ring": item_to_dict(p.equipped_ring),
        "equipped_amulet": item_to_dict(p.equipped_amulet),
        "owned_boat": item_to_dict(p.owned_boat),
        "materials": dict(p.materials),
        "reputation": p.reputation,
        "perks": {perk.name: count for perk, count in p.perks.items()},
        "pending_perk_choices": p.pending_perk_choices,
        "second_wind_ready": p.second_wind_ready,
        "subclass": p.subclass.name if p.subclass else None,
        "bionic_upgrade_used": p.bionic_upgrade_used,
        "artifacts": [a.name for a in p.artifacts],
        "companion": companion_to_dict(p.companion),
        "has_gills": p.has_gills,
        "defeated_big_kahoona": p.defeated_big_kahoona,
        "bank_gold": p.bank_gold,
        "bank_last_interest_tick": p.bank_last_interest_tick,
        "banker_reckoning_purchased": p.banker_reckoning_purchased,
        "owned_properties": [property_to_dict(prop) for prop in p.owned_properties],
        "owned_businesses": [business_to_dict(biz) for biz in p.owned_businesses],
    }


def player_from_dict(d: dict) -> PlayerCharacter:
    skills = {SkillType[k]: Skill(SkillType[k], v["level"], v["xp"]) for k, v in d["skills"].items()}
    return PlayerCharacter(
        name=d["name"],
        race=Race[d["race"]],
        character_class=CharacterClass[d["character_class"]],
        level=d["level"],
        experience=d["experience"],
        strength=d["strength"],
        agility=d["agility"],
        willpower=d["willpower"],
        max_health=d["max_health"],
        current_health=d["current_health"],
        max_stamina=d["max_stamina"],
        current_stamina=d["current_stamina"],
        armor_class=d["armor_class"],
        speed=d["speed"],
        attack_bonus=d["attack_bonus"],
        unarmed_damage=dice_from_dict(d["unarmed_damage"]),
        skills=skills,
        gold=d["gold"],
        inventory=tuple(item_from_dict(i) for i in d.get("inventory", [])),
        equipped_weapon=item_from_dict(d.get("equipped_weapon")),
        equipped_armor=item_from_dict(d.get("equipped_armor")),
        equipped_offhand=item_from_dict(d.get("equipped_offhand")),
        equipped_head=item_from_dict(d.get("equipped_head")),
        equipped_ring=item_from_dict(d.get("equipped_ring")),
        equipped_amulet=item_from_dict(d.get("equipped_amulet")),
        owned_boat=item_from_dict(d.get("owned_boat")),
        materials=dict(d.get("materials", {})),
        reputation=d.get("reputation", 0),
        perks={Perk[k]: v for k, v in d.get("perks", {}).items()},
        pending_perk_choices=d.get("pending_perk_choices", 0),
        second_wind_ready=d.get("second_wind_ready", False),
        subclass=Subclass[d["subclass"]] if d.get("subclass") else None,
        bionic_upgrade_used=d.get("bionic_upgrade_used", False),
        artifacts=frozenset(ArtifactKind[a] for a in d.get("artifacts", [])),
        companion=companion_from_dict(d.get("companion")),
        has_gills=d.get("has_gills", False),
        defeated_big_kahoona=d.get("defeated_big_kahoona", False),
        bank_gold=d.get("bank_gold", 0),
        bank_last_interest_tick=d.get("bank_last_interest_tick", 0),
        banker_reckoning_purchased=d.get("banker_reckoning_purchased", False),
        owned_properties=tuple(property_from_dict(pd) for pd in d.get("owned_properties", [])),
        owned_businesses=tuple(business_from_dict(bd) for bd in d.get("owned_businesses", [])),
    )
