"""Workspace-level smoke test: verifies packages interoperate correctly.

This lives outside packages/ because it tests cross-package integration
(aerocalc consuming aerounits quantities), not a single package in isolation.
"""

from __future__ import annotations

import math

from aerocalc import Atmosphere, mach_number
from aerounits import Q_


def test_atmosphere_accepts_aerounits_quantity_magnitude() -> None:
    altitude = Q_(35_000, "ft").to("m")
    atm = Atmosphere(altitude=altitude.magnitude)
    assert 200.0 < atm.temperature < 290.0  # sanity range for troposphere/stratosphere


def test_mach_number_end_to_end_cruise_scenario() -> None:
    """A 450 knot cruise at 35,000 ft should be transonic (M ~ 0.75-0.85)."""
    altitude = Q_(35_000, "ft").to("m")
    speed = Q_(450, "knot").to("m/s")

    atm = Atmosphere(altitude=altitude.magnitude)
    mach = mach_number(velocity=speed.magnitude, speed_of_sound=atm.speed_of_sound)

    assert math.isclose(mach, 0.783, rel_tol=0.05)
