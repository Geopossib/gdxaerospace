"""fatiguepy — S-N fatigue life and Miner's-rule cumulative damage for GDX Aerospace."""

from __future__ import annotations

from fatiguepy.exceptions import InvalidFatigueInputError
from fatiguepy.sn_curve import basquin_life, basquin_stress_amplitude, miners_rule_damage

__all__ = [
    "InvalidFatigueInputError",
    "basquin_life",
    "basquin_stress_amplitude",
    "miners_rule_damage",
]

__version__ = "0.1.0"
