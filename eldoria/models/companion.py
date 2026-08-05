"""A hired companion: deliberately lightweight since this rides along on PlayerCharacter and gets saved to disk."""
from __future__ import annotations

from dataclasses import dataclass

from eldoria.models.dice import DiceFormula

EMPLOYMENT_DURATION_MILLIS: int = 3 * 60 * 60 * 1000


@dataclass(frozen=True)
class HiredCompanion:
    name: str
    attack_bonus: int
    armor_class: int
    damage: DiceFormula
    origin_location_id: str
    hired_at_millis: int
    revive_used: bool = False
