"""A rental property the player owns -- an ongoing real-estate side-mechanic, not a one-shot purchase.

Pure data; the event simulation (tenants moving in/out, rent, damage,
vacancy) lives in world/real_estate.py, same split as every other model.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RentalProperty:
    location_id: str
    location_name: str
    purchase_price: int
    condition: int = 100
    tenant_name: str | None = None
    tenant_quality: str | None = None  # "good" | "average" | "bad", None while vacant
    last_event_tick: int = 0
    lifetime_rent_collected: int = 0
    lifetime_repair_spent: int = 0
    cycles_vacant_streak: int = 0

    @property
    def is_occupied(self) -> bool:
        return self.tenant_name is not None

    @property
    def is_condemned(self) -> bool:
        return self.condition <= 0
