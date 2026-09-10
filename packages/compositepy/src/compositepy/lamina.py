"""Orthotropic lamina reduced-stiffness matrix and axis transformation.

Reference
---------
- Jones, R.M., *Mechanics of Composite Materials*, 2nd ed., Ch. 2
  (reduced stiffness matrix, Eq. 2.66; transformed stiffness, Eq. 2.84).
  The T300/5208 graphite-epoxy properties used throughout this module's
  examples (E1=181 GPa, E2=10.3 GPa, nu12=0.28, G12=7.17 GPa) are Jones's
  own Table 2-2 example material, reproduced across most of the
  composite-mechanics literature as the standard worked example.

Convention
----------
- Material (1-2) axes: 1 = along the fibers, 2 = transverse to the fibers.
- ``theta`` is the ply angle, radians, measured from the laminate's
  reference x-axis to the fiber (1) direction, positive
  counterclockwise -- the standard CLT convention.
- The reciprocal relation ``nu21 = nu12 * E2 / E1`` is used internally
  so only the four independent elastic constants (E1, E2, nu12, G12)
  need to be supplied.

Assumptions
-----------
- Linear-elastic, orthotropic lamina behavior (no viscoelasticity,
  damage, or nonlinearity).
- Plane-stress assumption throughout, standard for thin-laminate CLT.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from compositepy.exceptions import InvalidLaminaError


@dataclass(frozen=True)
class ReducedStiffness:
    """A lamina's reduced stiffness matrix components, in material (1-2) axes."""

    q11: float
    q12: float
    q22: float
    q66: float


@dataclass(frozen=True)
class TransformedStiffness:
    """A lamina's transformed reduced stiffness matrix, in laminate (x-y) axes."""

    q11: float
    q12: float
    q16: float
    q22: float
    q26: float
    q66: float


def reduced_stiffness(e1: float, e2: float, nu12: float, g12: float) -> ReducedStiffness:
    """Compute a lamina's reduced stiffness matrix from its four elastic constants.

    ``Q11 = E1/(1-nu12*nu21)``, ``Q22 = E2/(1-nu12*nu21)``,
    ``Q12 = nu12*E2/(1-nu12*nu21)``, ``Q66 = G12``, using the reciprocal
    relation ``nu21 = nu12*E2/E1``.

    Parameters
    ----------
    e1:
        Longitudinal (fiber-direction) modulus, Pa, > 0.
    e2:
        Transverse modulus, Pa, > 0.
    nu12:
        Major Poisson's ratio, dimensionless, in ``[0, 1)``.
    g12:
        In-plane shear modulus, Pa, > 0.

    Returns
    -------
    ReducedStiffness

    Example
    -------
    T300/5208 graphite-epoxy (Jones, Table 2-2):

    >>> q = reduced_stiffness(e1=181e9, e2=10.3e9, nu12=0.28, g12=7.17e9)
    >>> round(q.q11 / 1e9, 2)
    181.81

    """
    if e1 <= 0 or e2 <= 0:
        raise InvalidLaminaError(f"e1 and e2 must both be positive, got e1={e1!r}, e2={e2!r}")
    if not (0 <= nu12 < 1):
        raise InvalidLaminaError(f"nu12 must be in [0, 1), got {nu12!r}")
    if g12 <= 0:
        raise InvalidLaminaError(f"g12 must be positive, got {g12!r}")

    nu21 = nu12 * e2 / e1
    denominator = 1 - nu12 * nu21
    if denominator <= 0:
        raise InvalidLaminaError(
            f"nu12*nu21 = {nu12 * nu21!r} >= 1; these elastic constants are not physically "
            "consistent for an orthotropic material"
        )
    q11 = e1 / denominator
    q22 = e2 / denominator
    q12 = nu12 * e2 / denominator
    return ReducedStiffness(q11=q11, q12=q12, q22=q22, q66=g12)


def transform_stiffness(q: ReducedStiffness, theta: float) -> TransformedStiffness:
    """Transform a lamina's reduced stiffness matrix to an arbitrary ply angle.

    Standard CLT axis-transformation equations (Jones Eq. 2.84).

    Parameters
    ----------
    q:
        Reduced stiffness matrix in material axes (see
        :func:`reduced_stiffness`).
    theta:
        Ply angle, radians, measured from the laminate x-axis to the
        fiber direction.

    Returns
    -------
    TransformedStiffness

    Example
    -------
    At theta=0, the transformed matrix equals the material-axes matrix
    (no shear coupling terms):

    >>> q = reduced_stiffness(e1=181e9, e2=10.3e9, nu12=0.28, g12=7.17e9)
    >>> q_bar = transform_stiffness(q, theta=0.0)
    >>> round(q_bar.q11 / 1e9, 2), round(q_bar.q16, 6)
    (181.81, 0.0)

    At theta=90 degrees, Q11_bar and Q22_bar swap (the fiber direction
    has rotated to what was the transverse direction):

    >>> import math
    >>> q_bar_90 = transform_stiffness(q, theta=math.radians(90.0))
    >>> round(q_bar_90.q11 / 1e9, 4) == round(q.q22 / 1e9, 4)
    True

    """
    c, s = math.cos(theta), math.sin(theta)
    c2, s2 = c**2, s**2
    c4, s4 = c**4, s**4

    q11_bar = q.q11 * c4 + 2 * (q.q12 + 2 * q.q66) * s2 * c2 + q.q22 * s4
    q22_bar = q.q11 * s4 + 2 * (q.q12 + 2 * q.q66) * s2 * c2 + q.q22 * c4
    q12_bar = (q.q11 + q.q22 - 4 * q.q66) * s2 * c2 + q.q12 * (s4 + c4)
    q66_bar = (q.q11 + q.q22 - 2 * q.q12 - 2 * q.q66) * s2 * c2 + q.q66 * (s4 + c4)
    q16_bar = (q.q11 - q.q12 - 2 * q.q66) * s * c**3 + (q.q12 - q.q22 + 2 * q.q66) * s**3 * c
    q26_bar = (q.q11 - q.q12 - 2 * q.q66) * s**3 * c + (q.q12 - q.q22 + 2 * q.q66) * s * c**3

    return TransformedStiffness(
        q11=q11_bar, q12=q12_bar, q16=q16_bar, q22=q22_bar, q26=q26_bar, q66=q66_bar
    )
