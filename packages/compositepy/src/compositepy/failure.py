"""Lamina-level failure criteria: maximum stress and Tsai-Hill.

Reference
---------
- Jones, R.M., *Mechanics of Composite Materials*, 2nd ed., Ch. 2
  (maximum stress criterion) and Ch. 2.3 (Tsai-Hill criterion, Eq. 2.128).

Assumptions
-----------
- Both criteria evaluate a single lamina's stress state in its own
  material (1-2) axes -- transform laminate-axis stresses to material
  axes first if starting from laminate-level results.
- Tsai-Hill uses the same strength value for tension and compression in
  each direction (a simplification some analyses replace with the
  Tsai-Wu criterion to allow different tension/compression strengths).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from compositepy.exceptions import InvalidLaminaError


@dataclass(frozen=True)
class LaminaStrengths:
    """A lamina's strength allowables, in material (1-2) axes.

    Parameters
    ----------
    x_tension, x_compression:
        Longitudinal (fiber-direction) tensile and compressive
        strength, Pa, both > 0 (compressive value given as a positive
        magnitude).
    y_tension, y_compression:
        Transverse tensile and compressive strength, Pa, both > 0.
    s:
        In-plane shear strength, Pa, > 0.

    """

    x_tension: float
    x_compression: float
    y_tension: float
    y_compression: float
    s: float

    def __post_init__(self) -> None:
        values = (self.x_tension, self.x_compression, self.y_tension, self.y_compression, self.s)
        if any(v <= 0 for v in values):
            raise InvalidLaminaError("all lamina strength values must be positive")


def max_stress_margins(
    sigma_1: float, sigma_2: float, tau_12: float, strengths: LaminaStrengths
) -> dict[str, float]:
    """Compute margins of safety against the maximum-stress failure criterion.

    Each mode's margin is ``strength/|stress| - 1``; failure in that mode
    is predicted when its margin is negative. The overall lamina margin
    is the minimum (most critical) across all modes.

    Parameters
    ----------
    sigma_1, sigma_2:
        Normal stresses in the fiber and transverse directions, Pa.
    tau_12:
        In-plane shear stress, Pa.
    strengths:
        Lamina strength allowables.

    Returns
    -------
    dict[str, float]
        Margin of safety for each of the three failure modes
        (``"fiber"``, ``"transverse"``, ``"shear"``) plus
        ``"governing"`` (the minimum, i.e. most critical, margin).

    Example
    -------
    T300/5208 (Jones Table 2-3 strength values), a lamina well within
    its allowables:

    >>> strengths = LaminaStrengths(
    ...     x_tension=1500e6, x_compression=1500e6,
    ...     y_tension=40e6, y_compression=246e6, s=68e6,
    ... )
    >>> margins = max_stress_margins(sigma_1=200e6, sigma_2=10e6, tau_12=20e6, strengths=strengths)
    >>> margins["governing"] > 0
    True

    """
    fiber_strength = strengths.x_tension if sigma_1 >= 0 else strengths.x_compression
    transverse_strength = strengths.y_tension if sigma_2 >= 0 else strengths.y_compression

    fiber_margin = fiber_strength / abs(sigma_1) - 1 if sigma_1 != 0 else math.inf
    transverse_margin = transverse_strength / abs(sigma_2) - 1 if sigma_2 != 0 else math.inf
    shear_margin = strengths.s / abs(tau_12) - 1 if tau_12 != 0 else math.inf

    return {
        "fiber": fiber_margin,
        "transverse": transverse_margin,
        "shear": shear_margin,
        "governing": min(fiber_margin, transverse_margin, shear_margin),
    }


def tsai_hill_failure_index(
    sigma_1: float, sigma_2: float, tau_12: float, strengths: LaminaStrengths
) -> float:
    """Compute the Tsai-Hill failure index for a lamina stress state.

    ``FI = (sigma_1/X)^2 - sigma_1*sigma_2/X^2 + (sigma_2/Y)^2 + (tau_12/S)^2``.

    Failure is predicted when ``FI >= 1``. Unlike the maximum-stress
    criterion, Tsai-Hill accounts for interaction between the stress
    components rather than checking each independently.

    Parameters
    ----------
    sigma_1, sigma_2:
        Normal stresses in the fiber and transverse directions, Pa.
    tau_12:
        In-plane shear stress, Pa.
    strengths:
        Lamina strength allowables. Uses the tension or compression
        strength in each direction according to the sign of the
        corresponding stress component.

    Returns
    -------
    float
        Tsai-Hill failure index. ``< 1``: predicted safe; ``>= 1``:
        predicted failure.

    Example
    -------
    >>> strengths = LaminaStrengths(
    ...     x_tension=1500e6, x_compression=1500e6,
    ...     y_tension=40e6, y_compression=246e6, s=68e6,
    ... )
    >>> fi = tsai_hill_failure_index(sigma_1=200e6, sigma_2=10e6, tau_12=20e6, strengths=strengths)
    >>> fi < 1
    True

    """
    x = strengths.x_tension if sigma_1 >= 0 else strengths.x_compression
    y = strengths.y_tension if sigma_2 >= 0 else strengths.y_compression
    s = strengths.s
    return (sigma_1 / x) ** 2 - (sigma_1 * sigma_2) / x**2 + (sigma_2 / y) ** 2 + (tau_12 / s) ** 2
