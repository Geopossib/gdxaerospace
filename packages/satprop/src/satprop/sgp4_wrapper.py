"""A thin wrapper around the MIT-licensed ``sgp4`` library for TLE-based propagation.

Reference
---------
- Vallado, D.A., Crawford, P., Hujsak, R. & Kelso, T.S., "Revisiting
  Spacetrack Report #3", AIAA 2006-6753 (the SGP4/SDP4 algorithm this
  wraps).
- ``sgp4`` (PyPI, MIT license): https://pypi.org/project/sgp4/ -- the
  actual propagation engine. GDX Aerospace does not reimplement SGP4;
  it wraps a validated, permissively-licensed implementation of an
  established, empirically-calibrated algorithm rather than
  reimplementing it from scratch.

Convention
----------
- SGP4 returns position/velocity in the TEME (True Equator, Mean
  Equinox) frame, km and km/s -- a specific non-inertial-in-the-usual-
  sense frame tied to the SGP4/SDP4 theory itself. This module returns
  those TEME vectors in SI units (m, m/s) without further frame
  conversion; use ``groundtrack`` for TEME-to-ECEF-to-geodetic
  conversion.
- SGP4 propagation is only valid near the TLE's epoch -- accuracy
  degrades over days to weeks depending on the object and how
  recently the TLE was generated, since it does not know about drag,
  maneuvers, or solar activity after the epoch. Always use a current
  TLE for the time of interest.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
from sgp4.api import Satrec, jday

from satprop.exceptions import PropagationError

#: SGP4 error codes and their meanings (sgp4 library / Vallado report).
_SGP4_ERROR_MESSAGES = {
    1: "mean eccentricity is outside the range [0, 1)",
    2: "mean motion has become negative",
    3: "perturbed eccentricity is outside the range [0, 1)",
    4: "semi-latus rectum became negative",
    5: "epoch elements are unphysical (satellite has decayed)",
    6: "satellite has decayed (orbit has effectively decayed into the atmosphere)",
}


def propagate_tle(
    line1: str, line2: str, epoch_utc: dt.datetime
) -> tuple[np.ndarray, np.ndarray]:
    """Propagate a TLE to a given UTC time using SGP4.

    Parameters
    ----------
    line1, line2:
        The two TLE lines (see :mod:`tletools` to parse their contents
        into structured data, if needed separately from propagation).
    epoch_utc:
        UTC time to propagate to.

    Returns
    -------
    (position, velocity):
        TEME-frame position (m) and velocity (m/s), each shape ``(3,)``.

    Raises
    ------
    PropagationError
        If SGP4 reports an error (e.g. the object has decayed, or the
        TLE is unphysical).

    Example
    -------
    Propagating the classic Vallado/ISS validation TLE to its own epoch
    should give a position vector with a magnitude consistent with the
    ISS's known orbital altitude (~6700-6800 km from Earth's center):

    >>> line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    >>> line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
    >>> import datetime as dt
    >>> position, velocity = propagate_tle(line1, line2, dt.datetime(2008, 9, 20, 12, 25, 40))
    >>> 6_600_000 < float((position @ position) ** 0.5) < 6_900_000
    True

    """
    satellite = Satrec.twoline2rv(line1, line2)
    jd, fr = jday(
        epoch_utc.year,
        epoch_utc.month,
        epoch_utc.day,
        epoch_utc.hour,
        epoch_utc.minute,
        epoch_utc.second + epoch_utc.microsecond / 1e6,
    )
    error_code, position_km, velocity_km_s = satellite.sgp4(jd, fr)
    if error_code != 0:
        message = _SGP4_ERROR_MESSAGES.get(error_code, "unknown SGP4 error")
        raise PropagationError(f"SGP4 propagation failed (code {error_code}): {message}")

    position = np.array(position_km) * 1000.0
    velocity = np.array(velocity_km_s) * 1000.0
    return position, velocity
