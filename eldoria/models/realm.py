"""Shared small enums used by both game_location.py and sub_realm.py (split out to avoid an import cycle)."""
from __future__ import annotations

from enum import Enum


class RealmKind(Enum):
    """Underground dungeon (tunnels/caves) or the sky realm reached by beanstalk."""

    DUNGEON = "DUNGEON"
    SKY_REALM = "SKY_REALM"


class QuestType(Enum):
    RETRIEVE_ARTIFACT = "RETRIEVE_ARTIFACT"
    DEFEAT_GUARDIAN = "DEFEAT_GUARDIAN"
    RESCUE_CAPTIVE = "RESCUE_CAPTIVE"
