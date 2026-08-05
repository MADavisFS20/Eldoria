"""A business the player has a stake in -- either a passive minority stake, or full ownership requiring a manager.

Pure data; the event simulation (profit, loss, manager performance, scandal,
business failure) lives in world/business.py, same split as every other model.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Business:
    id: str
    location_id: str
    location_name: str
    name: str
    business_type: str
    investment: int
    ownership_percent: int
    manager_name: str | None = None
    manager_quality: str | None = None  # "good" | "average" | "corrupt" | "incompetent" -- hidden until revealed
    manager_revealed: bool = False
    manager_cycles_observed: int = 0
    last_event_tick: int = 0
    lifetime_profit_collected: int = 0
    lifetime_losses: int = 0
    is_failed: bool = False

    @property
    def is_fully_owned(self) -> bool:
        return self.ownership_percent >= 100

    @property
    def has_manager(self) -> bool:
        return self.manager_name is not None
