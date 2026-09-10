"""Fundamental stress, strain, and 2D failure-theory calculations.

Reference
---------
- Hibbeler, R.C., *Mechanics of Materials*, 10th ed., Ch. 1 (axial
  stress), Ch. 6 (bending stress), Ch. 7 (transverse shear), Ch. 5
  (torsion), Ch. 9 (plane stress transformation, principal stresses).
- Von Mises equivalent stress: the standard distortion-energy failure
  criterion for ductile materials (Hibbeler Ch. 10, or any mechanics of
  materials text).

Assumptions
-----------
- Linear-elastic material behavior (Hooke's law) throughout.
- Bending/shear/torsion formulas assume the standard beam-theory and
  circular-shaft-torsion assumptions (plane sections remain plane for
  bending; circular cross-section for the torsion formula as given --
  non-circular torsion requires different, shape-specific theory not
  covered here).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from stresspy.exceptions import InvalidStressInputError


def axial_stress(force: float, area: float) -> float:
    """Uniform axial (normal) stress: ``sigma = F / A``.

    Parameters
    ----------
    force:
        Axial force, N (positive = tension, negative = compression).
    area:
        Cross-sectional area, m^2, > 0.

    Example
    -------
    >>> round(axial_stress(force=50_000.0, area=0.001), 1)
    50000000.0

    """
    if area <= 0:
        raise InvalidStressInputError(f"area must be positive, got {area!r}")
    return force / area


def bending_stress(
    moment: float, distance_from_neutral_axis: float, moment_of_inertia: float
) -> float:
    """Bending (flexure) stress: ``sigma = M * c / I``.

    Parameters
    ----------
    moment:
        Bending moment, N*m.
    distance_from_neutral_axis:
        Distance from the neutral axis to the point of interest, m
        (positive on the side that goes into tension for positive
        moment, by the standard beam-theory sign convention).
    moment_of_inertia:
        Second moment of area about the bending axis, m^4, > 0 (see
        :mod:`aerostruct.sections` for section-property calculations).

    Example
    -------
    >>> round(bending_stress(5000.0, 0.05, 1.667e-6), -3)
    149970000.0

    """
    if moment_of_inertia <= 0:
        raise InvalidStressInputError(
            f"moment_of_inertia must be positive, got {moment_of_inertia!r}"
        )
    return moment * distance_from_neutral_axis / moment_of_inertia


def transverse_shear_stress(
    shear_force: float, first_moment_of_area: float, moment_of_inertia: float, thickness: float
) -> float:
    """Transverse shear stress in a beam: ``tau = V * Q / (I * t)``.

    Parameters
    ----------
    shear_force:
        Transverse shear force at the section, N.
    first_moment_of_area:
        First moment of the area beyond the point of interest about the
        neutral axis, m^3, >= 0.
    moment_of_inertia:
        Second moment of area of the full cross-section, m^4, > 0.
    thickness:
        Section thickness (width) at the point of interest, m, > 0.

    Example
    -------
    >>> round(transverse_shear_stress(1000.0, 2e-5, 1.667e-6, 0.02), 1)
    599880.0

    """
    if moment_of_inertia <= 0:
        raise InvalidStressInputError(
            f"moment_of_inertia must be positive, got {moment_of_inertia!r}"
        )
    if thickness <= 0:
        raise InvalidStressInputError(f"thickness must be positive, got {thickness!r}")
    return shear_force * first_moment_of_area / (moment_of_inertia * thickness)


def torsional_shear_stress(torque: float, radius: float, polar_moment_of_inertia: float) -> float:
    """Torsional shear stress in a circular shaft: ``tau = T * r / J``.

    Parameters
    ----------
    torque:
        Applied torque, N*m.
    radius:
        Radial distance from the shaft's center to the point of
        interest, m (maximum at the outer surface).
    polar_moment_of_inertia:
        Polar second moment of area, m^4, > 0 (see
        :func:`aerostruct.sections.circle_properties` for a solid
        circular shaft).

    Example
    -------
    >>> round(torsional_shear_stress(200.0, 0.02, 9.817e-6), 1)
    407456.5

    """
    if polar_moment_of_inertia <= 0:
        raise InvalidStressInputError(
            f"polar_moment_of_inertia must be positive, got {polar_moment_of_inertia!r}"
        )
    return torque * radius / polar_moment_of_inertia


def von_mises_stress(sigma_x: float, sigma_y: float, tau_xy: float) -> float:
    """Compute the von Mises equivalent stress for a 2D (plane) stress state.

    ``sigma_vm = sqrt(sigma_x^2 - sigma_x*sigma_y + sigma_y^2 + 3*tau_xy^2)``,
    the standard distortion-energy failure criterion for ductile materials.

    Parameters
    ----------
    sigma_x, sigma_y:
        Normal stresses in the x and y directions, Pa.
    tau_xy:
        Shear stress, Pa.

    Returns
    -------
    float
        Von Mises equivalent stress, Pa (always >= 0).

    Example
    -------
    >>> round(von_mises_stress(sigma_x=150e6, sigma_y=0.0, tau_xy=50e6), -3)
    173205000.0

    """
    return math.sqrt(sigma_x**2 - sigma_x * sigma_y + sigma_y**2 + 3 * tau_xy**2)


@dataclass(frozen=True)
class PrincipalStresses:
    """Principal stresses and maximum in-plane shear for a 2D stress state."""

    sigma_1: float
    sigma_2: float
    tau_max: float
    theta_p: float
    """Principal-plane angle, radians, from the +x axis to the sigma_1 direction."""


def principal_stresses(sigma_x: float, sigma_y: float, tau_xy: float) -> PrincipalStresses:
    """Compute principal stresses and max in-plane shear for a 2D stress state.

    Standard plane-stress transformation (Mohr's circle):
    ``sigma_avg = (sigma_x+sigma_y)/2``,
    ``R = sqrt(((sigma_x-sigma_y)/2)^2 + tau_xy^2)``,
    ``sigma_1 = sigma_avg + R``, ``sigma_2 = sigma_avg - R``, ``tau_max = R``.

    Parameters
    ----------
    sigma_x, sigma_y:
        Normal stresses in the x and y directions, Pa.
    tau_xy:
        Shear stress, Pa.

    Returns
    -------
    PrincipalStresses

    Example
    -------
    >>> result = principal_stresses(sigma_x=100e6, sigma_y=40e6, tau_xy=30e6)
    >>> round(result.sigma_1 / 1e6, 2)
    112.43
    >>> round(result.sigma_2 / 1e6, 2)
    27.57

    """
    sigma_avg = (sigma_x + sigma_y) / 2
    r = math.sqrt(((sigma_x - sigma_y) / 2) ** 2 + tau_xy**2)
    theta_p = 0.5 * math.atan2(2 * tau_xy, sigma_x - sigma_y)
    return PrincipalStresses(
        sigma_1=sigma_avg + r, sigma_2=sigma_avg - r, tau_max=r, theta_p=theta_p
    )
