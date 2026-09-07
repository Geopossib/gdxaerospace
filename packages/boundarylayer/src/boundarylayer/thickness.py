"""Flat-plate boundary-layer thickness and skin-friction relations.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 17-18
  (Blasius laminar solution, 1/7-power-law turbulent approximation).
- White, F.M., *Viscous Fluid Flow*, 3rd ed., Ch. 4 & 6.

Assumptions
-----------
- Incompressible, 2D flow over a smooth flat plate at zero pressure gradient.
- Laminar boundary-layer thickness is the (arbitrary but conventional)
  ``y`` where ``u = 0.99 * U_infinity``, from the Blasius similarity
  solution.
- Turbulent boundary-layer thickness uses the 1/7-power-law approximation,
  valid for ``5e5 < Re_x < 1e7`` roughly.
"""

from __future__ import annotations

from boundarylayer.exceptions import InvalidReynoldsNumberError


def _check_reynolds(reynolds_x: float) -> None:
    if reynolds_x <= 0:
        raise InvalidReynoldsNumberError(reynolds_x)


def laminar_thickness(x: float, reynolds_x: float) -> float:
    """Blasius laminar boundary-layer thickness ``delta = 5.0 * x / sqrt(Re_x)``.

    Parameters
    ----------
    x:
        Distance from the leading edge, m.
    reynolds_x:
        Local Reynolds number ``rho * U * x / mu``, > 0.

    Returns
    -------
    float
        Boundary-layer thickness (99% velocity thickness), m.

    Example
    -------
    >>> round(laminar_thickness(x=1.0, reynolds_x=1e6), 5)
    0.005

    """
    _check_reynolds(reynolds_x)
    return 5.0 * x / reynolds_x**0.5


def turbulent_thickness(x: float, reynolds_x: float) -> float:
    """1/7-power-law turbulent boundary-layer thickness ``delta = 0.37 * x / Re_x^0.2``.

    Parameters
    ----------
    x:
        Distance from the leading edge, m.
    reynolds_x:
        Local Reynolds number, > 0.

    Example
    -------
    >>> round(turbulent_thickness(x=1.0, reynolds_x=1e7), 5)
    0.01473

    """
    _check_reynolds(reynolds_x)
    return 0.37 * x / reynolds_x**0.2


def laminar_local_skin_friction(reynolds_x: float) -> float:
    """Local skin-friction coefficient, laminar: ``Cf_x = 0.664 / sqrt(Re_x)``.

    Example:
    -------
    >>> round(laminar_local_skin_friction(1e6), 5)
    0.00066

    """
    _check_reynolds(reynolds_x)
    return 0.664 / reynolds_x**0.5


def turbulent_local_skin_friction(reynolds_x: float) -> float:
    """Local skin-friction coefficient, turbulent (1/7-power-law): ``Cf_x = 0.0592 / Re_x^0.2``.

    Example:
    -------
    >>> round(turbulent_local_skin_friction(1e7), 5)
    0.00236

    """
    _check_reynolds(reynolds_x)
    return 0.0592 / reynolds_x**0.2
