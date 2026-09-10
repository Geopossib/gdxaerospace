"""Euler column buckling and flat-plate buckling.

Reference
---------
- Timoshenko, S.P. & Gere, J.M., *Theory of Elastic Stability*, 2nd ed.,
  Ch. 2 (Euler column buckling, all four standard end conditions) and
  Ch. 9 (flat rectangular plate buckling under uniaxial compression).
- Hibbeler, R.C., *Mechanics of Materials*, 10th ed., Ch. 13, for the
  same column formulas in the "effective length factor K" convention
  used here.

Convention
----------
- Column buckling uses the effective-length-factor form,
  ``Pcr = pi^2 * E * I / (K*L)^2``, where ``K`` depends on the end
  conditions:

  - pinned-pinned: ``K = 1.0``
  - fixed-free (cantilever): ``K = 2.0``
  - fixed-fixed: ``K = 0.5``
  - fixed-pinned: ``K = 0.699`` (from the transcendental equation
    ``tan(pi/K) = pi/K``; 0.699 is the standard rounded value quoted in
    most references, e.g. Hibbeler)

Assumptions
-----------
- Ideal, initially perfectly straight columns with no eccentricity and
  purely elastic buckling (valid while the buckling stress stays below
  the material's proportional limit -- for short, stocky columns the
  actual failure mode is yielding, not elastic buckling, and this
  module's result is not meaningful there).
- The plate-buckling formula assumes a flat rectangular plate, simply
  supported on all four edges, under uniform uniaxial in-plane
  compression -- other support/loading conditions need a different
  buckling coefficient ``k``.
"""

from __future__ import annotations

import math

from bucklingpy.exceptions import InvalidBucklingInputError

#: Effective length factor K: pinned-pinned column.
K_PINNED_PINNED = 1.0
#: Effective length factor K: fixed-free (cantilever) column.
K_FIXED_FREE = 2.0
#: Effective length factor K: fixed-fixed column.
K_FIXED_FIXED = 0.5
#: Effective length factor K: fixed-pinned column.
K_FIXED_PINNED = 0.699

#: Buckling coefficient k for a flat rectangular plate, simply supported on all
#: four edges, under uniform uniaxial compression, long-plate limit.
PLATE_K_ALL_EDGES_SIMPLY_SUPPORTED = 4.0


def euler_buckling_load(
    youngs_modulus: float,
    moment_of_inertia: float,
    length: float,
    *,
    k_factor: float = K_PINNED_PINNED,
) -> float:
    """Compute the Euler critical buckling load: ``Pcr = pi^2 * E * I / (K*L)^2``.

    Parameters
    ----------
    youngs_modulus:
        Young's modulus, Pa, > 0.
    moment_of_inertia:
        Second moment of area about the weak (buckling) axis, m^4, > 0.
    length:
        Unsupported column length, m, > 0.
    k_factor:
        Effective length factor for the end conditions; see the module
        docstring for the four standard values. Defaults to 1.0
        (pinned-pinned).

    Returns
    -------
    float
        Critical buckling load, N.

    Example
    -------
    >>> round(euler_buckling_load(71.7e9, 1e-6, 2.0), 2)
    176912.66

    """
    if youngs_modulus <= 0:
        raise InvalidBucklingInputError(
            f"youngs_modulus must be positive, got {youngs_modulus!r}"
        )
    if moment_of_inertia <= 0:
        raise InvalidBucklingInputError(
            f"moment_of_inertia must be positive, got {moment_of_inertia!r}"
        )
    if length <= 0:
        raise InvalidBucklingInputError(f"length must be positive, got {length!r}")
    if k_factor <= 0:
        raise InvalidBucklingInputError(f"k_factor must be positive, got {k_factor!r}")
    return math.pi**2 * youngs_modulus * moment_of_inertia / (k_factor * length) ** 2


def euler_buckling_stress(
    youngs_modulus: float,
    radius_of_gyration: float,
    length: float,
    *,
    k_factor: float = K_PINNED_PINNED,
) -> float:
    """Compute the Euler critical buckling stress: ``sigma_cr = pi^2 * E / (K*L/r)^2``.

    Parameters
    ----------
    youngs_modulus:
        Young's modulus, Pa, > 0.
    radius_of_gyration:
        Radius of gyration about the weak axis, ``r = sqrt(I/A)``, m, > 0.
    length:
        Unsupported column length, m, > 0.
    k_factor:
        Effective length factor; see the module docstring.

    Returns
    -------
    float
        Critical buckling stress, Pa.

    Example
    -------
    >>> round(euler_buckling_stress(71.7e9, radius_of_gyration=0.01, length=2.0), 1)
    17691265.9

    """
    if youngs_modulus <= 0:
        raise InvalidBucklingInputError(
            f"youngs_modulus must be positive, got {youngs_modulus!r}"
        )
    if radius_of_gyration <= 0:
        raise InvalidBucklingInputError(
            f"radius_of_gyration must be positive, got {radius_of_gyration!r}"
        )
    if length <= 0:
        raise InvalidBucklingInputError(f"length must be positive, got {length!r}")
    if k_factor <= 0:
        raise InvalidBucklingInputError(f"k_factor must be positive, got {k_factor!r}")
    slenderness_ratio = (k_factor * length) / radius_of_gyration
    return math.pi**2 * youngs_modulus / slenderness_ratio**2


def plate_buckling_stress(
    youngs_modulus: float,
    poisson_ratio: float,
    thickness: float,
    width: float,
    *,
    k: float = PLATE_K_ALL_EDGES_SIMPLY_SUPPORTED,
) -> float:
    """Compute the critical buckling stress for a flat plate under uniaxial compression.

    ``sigma_cr = k * pi^2 * E / (12*(1-nu^2)) * (t/b)^2``.

    Parameters
    ----------
    youngs_modulus:
        Young's modulus, Pa, > 0.
    poisson_ratio:
        Poisson's ratio, in ``[0, 0.5)``.
    thickness:
        Plate thickness, m, > 0.
    width:
        Plate width (the loaded-edge-perpendicular dimension used to
        define the buckling coefficient), m, > 0.
    k:
        Buckling coefficient, depends on support and loading
        conditions. Defaults to 4.0 (all four edges simply supported,
        long-plate limit; see :data:`PLATE_K_ALL_EDGES_SIMPLY_SUPPORTED`).

    Returns
    -------
    float
        Critical buckling stress, Pa.

    Example
    -------
    >>> round(plate_buckling_stress(71.7e9, 0.33, thickness=0.002, width=0.1), 1)
    105884208.4

    """
    if youngs_modulus <= 0:
        raise InvalidBucklingInputError(
            f"youngs_modulus must be positive, got {youngs_modulus!r}"
        )
    if not (0 <= poisson_ratio < 0.5):
        raise InvalidBucklingInputError(
            f"poisson_ratio must be in [0, 0.5), got {poisson_ratio!r}"
        )
    if thickness <= 0:
        raise InvalidBucklingInputError(f"thickness must be positive, got {thickness!r}")
    if width <= 0:
        raise InvalidBucklingInputError(f"width must be positive, got {width!r}")
    if k <= 0:
        raise InvalidBucklingInputError(f"k must be positive, got {k!r}")
    return (
        k * math.pi**2 * youngs_modulus / (12 * (1 - poisson_ratio**2)) * (thickness / width) ** 2
    )
