"""Cantilever beam deflection and shear-flow formulas for wing spar analysis.

Reference
---------
- Hibbeler, R.C., *Mechanics of Materials*, 10th ed., Appendix C
  (standard beam deflection tables, double-integration method).
- Megson, T.H.G., *Aircraft Structures for Engineering Students*, 6th
  ed., Ch. 16, for shear flow in thin-walled beam sections -- the
  standard idealization for wing spar webs.

Assumptions
-----------
- Linear-elastic, small-deflection (Euler-Bernoulli) beam theory
  throughout.
- The cantilever (fixed-free) boundary condition models a wing spar
  fixed at the root and free at the tip, the standard first-order
  idealization for a wing under aerodynamic load; a real wing box has
  additional support/redundancy this simplified model does not capture.
"""

from __future__ import annotations

from sparcalc.exceptions import InvalidSparInputError


def _check_beam_properties(
    length: float, youngs_modulus: float, moment_of_inertia: float
) -> None:
    if length <= 0:
        raise InvalidSparInputError(f"length must be positive, got {length!r}")
    if youngs_modulus <= 0:
        raise InvalidSparInputError(f"youngs_modulus must be positive, got {youngs_modulus!r}")
    if moment_of_inertia <= 0:
        raise InvalidSparInputError(
            f"moment_of_inertia must be positive, got {moment_of_inertia!r}"
        )


def cantilever_tip_deflection_point_load(
    load: float, length: float, youngs_modulus: float, moment_of_inertia: float
) -> float:
    """Compute the tip deflection of a cantilever beam under a point load at the free end.

    ``delta = P*L^3 / (3*E*I)``.

    Parameters
    ----------
    load:
        Point load at the free end, N.
    length:
        Beam length, m, > 0.
    youngs_modulus:
        Young's modulus, Pa, > 0.
    moment_of_inertia:
        Second moment of area about the bending axis, m^4, > 0.

    Example
    -------
    >>> round(cantilever_tip_deflection_point_load(1000.0, 2.0, 71.7e9, 1e-6), 6)
    0.037192

    """
    _check_beam_properties(length, youngs_modulus, moment_of_inertia)
    return load * length**3 / (3 * youngs_modulus * moment_of_inertia)


def cantilever_tip_deflection_distributed_load(
    load_per_length: float, length: float, youngs_modulus: float, moment_of_inertia: float
) -> float:
    """Compute the tip deflection of a cantilever beam under a uniformly distributed load.

    ``delta = w*L^4 / (8*E*I)``.

    Parameters
    ----------
    load_per_length:
        Distributed load, N/m (e.g. an idealized uniform aerodynamic
        lift distribution along the span).
    length:
        Beam length, m, > 0.
    youngs_modulus:
        Young's modulus, Pa, > 0.
    moment_of_inertia:
        Second moment of area, m^4, > 0.

    Example
    -------
    >>> round(cantilever_tip_deflection_distributed_load(500.0, 2.0, 71.7e9, 1e-6), 6)
    0.013947

    """
    _check_beam_properties(length, youngs_modulus, moment_of_inertia)
    return load_per_length * length**4 / (8 * youngs_modulus * moment_of_inertia)


def cantilever_tip_slope_point_load(
    load: float, length: float, youngs_modulus: float, moment_of_inertia: float
) -> float:
    """Compute the tip slope (rotation) of a cantilever beam under a point load.

    ``theta = P*L^2 / (2*E*I)``.

    Parameters
    ----------
    load:
        Point load at the free end, N.
    length:
        Beam length, m, > 0.
    youngs_modulus:
        Young's modulus, Pa, > 0.
    moment_of_inertia:
        Second moment of area, m^4, > 0.

    Example
    -------
    >>> round(cantilever_tip_slope_point_load(1000.0, 2.0, 71.7e9, 1e-6), 6)
    0.027894

    """
    _check_beam_properties(length, youngs_modulus, moment_of_inertia)
    return load * length**2 / (2 * youngs_modulus * moment_of_inertia)


def shear_flow(
    shear_force: float, first_moment_of_area: float, moment_of_inertia: float
) -> float:
    """Compute shear flow at a point in a thin-walled beam section: ``q = V*Q / I``.

    Shear flow (force per unit length along the section's midline) is
    the standard quantity used to size thin-walled spar webs and skin
    panels, since it's directly usable as a running load regardless of
    local wall thickness.

    Parameters
    ----------
    shear_force:
        Transverse shear force at the section, N.
    first_moment_of_area:
        First moment of the area beyond the point of interest about the
        neutral axis, m^3.
    moment_of_inertia:
        Second moment of area of the full cross-section, m^4, > 0.

    Returns
    -------
    float
        Shear flow, N/m.

    Example
    -------
    >>> round(
    ...     shear_flow(shear_force=5000.0, first_moment_of_area=1.5e-4, moment_of_inertia=8.55e-7),
    ...     1,
    ... )
    877193.0

    """
    if moment_of_inertia <= 0:
        raise InvalidSparInputError(
            f"moment_of_inertia must be positive, got {moment_of_inertia!r}"
        )
    return shear_force * first_moment_of_area / moment_of_inertia
