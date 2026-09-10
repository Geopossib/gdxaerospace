"""missionpy — mission-level analysis (eclipse, delta-v budgets) for GDX Aerospace."""

from __future__ import annotations

from missionpy.delta_v_budget import DeltaVBudget
from missionpy.eclipse import eclipse_duration, eclipse_fraction
from missionpy.exceptions import InvalidMissionInputError

__all__ = [
    "DeltaVBudget",
    "InvalidMissionInputError",
    "eclipse_duration",
    "eclipse_fraction",
]

__version__ = "0.1.0"
