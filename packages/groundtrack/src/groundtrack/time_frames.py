"""Julian date, Greenwich Mean Sidereal Time, and ECI/ECEF rotation.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Ch. 3 (Julian date, Eq. 3-14 GMST formula, Eq. 3-63 ECI-ECEF
  rotation).
- Meeus, J., *Astronomical Algorithms*, 2nd ed., Ch. 7 (Julian day
  number calculation).

Convention
----------
- ECI here means any Earth-centered inertial frame consistent with the
  GMST convention used (e.g. TEME, as output by SGP4 in ``satprop`` --
  strictly TEME and true-of-date GCRF differ by nutation/precession
  terms this module does not model, which is a small-angle
  approximation adequate for ground-track/visibility work but not for
  precision geodesy).
"""

from __future__ import annotations

import datetime as dt
import math

import numpy as np

from groundtrack.exceptions import InvalidCoordinateError


def julian_date(epoch_utc: dt.datetime) -> float:
    """Compute the Julian Date for a UTC datetime.

    Parameters
    ----------
    epoch_utc:
        UTC datetime.

    Returns
    -------
    float
        Julian Date.

    Example
    -------
    J2000.0, the reference epoch, is by definition JD 2451545.0:

    >>> import datetime as dt
    >>> julian_date(dt.datetime(2000, 1, 1, 12, 0, 0))
    2451545.0

    """
    year, month = epoch_utc.year, epoch_utc.month
    day_fraction = (
        epoch_utc.day
        + epoch_utc.hour / 24
        + epoch_utc.minute / 1440
        + (epoch_utc.second + epoch_utc.microsecond / 1e6) / 86400
    )
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jd = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day_fraction
        + b
        - 1524.5
    )
    return jd


def gmst(epoch_utc: dt.datetime) -> float:
    """Compute the Greenwich Mean Sidereal Time for a UTC datetime.

    Parameters
    ----------
    epoch_utc:
        UTC datetime.

    Returns
    -------
    float
        GMST, radians, in ``[0, 2*pi)``.

    Example
    -------
    >>> import datetime as dt
    >>> import math
    >>> round(math.degrees(gmst(dt.datetime(2000, 1, 1, 12, 0, 0))), 5)
    280.46062

    """
    jd = julian_date(epoch_utc)
    t = (jd - 2451545.0) / 36525.0
    gmst_deg = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t**2
        - t**3 / 38710000.0
    )
    return math.radians(gmst_deg % 360.0)


def eci_to_ecef(position_eci: np.ndarray, gmst_rad: float) -> np.ndarray:
    """Rotate a position vector from an Earth-centered inertial frame to ECEF.

    ``r_ecef = R3(GMST) @ r_eci``, where ``R3`` is a right-handed rotation
    about the Z axis by GMST.

    Parameters
    ----------
    position_eci:
        Position in the ECI frame, shape ``(3,)`` (any consistent units).
    gmst_rad:
        Greenwich Mean Sidereal Time, radians (see :func:`gmst`).

    Returns
    -------
    numpy.ndarray
        Position in the ECEF frame, same units and shape as input.

    Example
    -------
    >>> import numpy as np
    >>> import math
    >>> r_eci = np.array([7_000_000.0, 0.0, 0.0])
    >>> r_ecef = eci_to_ecef(r_eci, math.radians(90.0))
    >>> [round(float(x), 1) for x in r_ecef]
    [0.0, -7000000.0, 0.0]

    """
    r = np.asarray(position_eci, dtype=float)
    if r.shape != (3,):
        raise InvalidCoordinateError(f"position_eci must have shape (3,), got {r.shape}")
    c, s = math.cos(gmst_rad), math.sin(gmst_rad)
    rotation = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])
    return np.asarray(rotation @ r)


def ecef_to_eci(position_ecef: np.ndarray, gmst_rad: float) -> np.ndarray:
    """Rotate a position vector from ECEF back to an Earth-centered inertial frame.

    Inverse of :func:`eci_to_ecef`.

    Example:
    -------
    >>> import numpy as np
    >>> import math
    >>> r_eci = np.array([7_000_000.0, 1_000_000.0, 500_000.0])
    >>> theta = math.radians(37.0)
    >>> np.allclose(ecef_to_eci(eci_to_ecef(r_eci, theta), theta), r_eci)
    True

    """
    r = np.asarray(position_ecef, dtype=float)
    if r.shape != (3,):
        raise InvalidCoordinateError(f"position_ecef must have shape (3,), got {r.shape}")
    c, s = math.cos(gmst_rad), math.sin(gmst_rad)
    rotation = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    return np.asarray(rotation @ r)
