"""Fundamental constants for two-body orbital mechanics.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Appendix D (Earth physical constants, WGS84).
"""

from __future__ import annotations

#: Earth gravitational parameter (GM), m^3/s^2 (WGS84 value).
EARTH_MU = 3.986004418e14
#: Earth equatorial radius (WGS84), m.
EARTH_RADIUS = 6_378_137.0
#: Earth flattening (WGS84).
EARTH_FLATTENING = 1 / 298.257223563
#: Earth rotation rate, rad/s (sidereal).
EARTH_ROTATION_RATE = 7.292115e-5
