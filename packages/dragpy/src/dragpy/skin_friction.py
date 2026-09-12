"""Flat-plate skin-friction drag coefficients.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 17-18.
- Schlichting, H., *Boundary-Layer Theory*, 7th ed., for the turbulent
  correlation.

Assumptions
-----------
- Laminar: exact Blasius flat-plate solution, valid for Re_x up to
  transition (typically Re ~ 5e5, flow-dependent).
- Turbulent: two alternative correlations are exposed explicitly via
  ``model=`` — the simple 1/5-power-law (Prandtl) and the more accurate
  Schlichting logarithmic correlation, both for a smooth flat plate.
- Both correlations assume incompressible flow; no compressibility
  correction is applied here (see ``dragpy.compressibility`` in a future
  phase for that).
"""

from __future__ import annotations

import math

from dragpy.exceptions import InvalidDragModelError


def skin_friction_coefficient_laminar(reynolds: float) -> float:
    """Average skin-friction coefficient over a flat plate, laminar flow.

    ``Cf = 1.328 / sqrt(Re)`` (exact Blasius solution).

    Parameters
    ----------
    reynolds:
        Reynolds number based on plate length, > 0.

    Example
    -------
    >>> round(skin_friction_coefficient_laminar(1e6), 5)
    0.00133

    """
    if reynolds <= 0:
        raise ValueError(f"reynolds must be positive, got {reynolds!r}")
    return 1.328 / math.sqrt(reynolds)


def skin_friction_coefficient_turbulent(reynolds: float, *, model: str = "schlichting") -> float:
    """Average skin-friction coefficient over a flat plate, turbulent flow.

    Parameters
    ----------
    reynolds:
        Reynolds number based on plate length, > 0.
    model:
        ``"prandtl"``: ``Cf = 0.074 / Re^0.2`` (1/7-power-law, valid
        Re < ~1e7).
        ``"schlichting"`` (default): ``Cf = 0.455 / (log10(Re))^2.58``,
        valid over a much wider range (up to Re ~ 1e9).

    Raises
    ------
    InvalidDragModelError
        If ``model`` is not one of the supported names.

    Example
    -------
    >>> round(skin_friction_coefficient_turbulent(1e7, model="schlichting"), 5)
    0.003

    """
    if reynolds <= 0:
        raise ValueError(f"reynolds must be positive, got {reynolds!r}")
    if model == "prandtl":
        return float(0.074 / reynolds**0.2)
    if model == "schlichting":
        return float(0.455 / (math.log10(reynolds)) ** 2.58)
    raise InvalidDragModelError(model, valid_models=("prandtl", "schlichting"))
