"""Classical Laminate Theory: ABD stiffness-matrix assembly and laminate response.

Reference
---------
- Jones, R.M., *Mechanics of Composite Materials*, 2nd ed., Ch. 4
  (Eq. 4.21-4.23: A, B, D matrix definitions as through-thickness
  integrals/sums of each ply's transformed stiffness).
- Gibson, R.F., *Principles of Composite Material Mechanics*, 3rd ed.,
  Ch. 7, for the same laminate constitutive equation,
  ``[N; M] = [[A, B], [B, D]] @ [eps0; kappa]``.

Convention
----------
- Plies are given in order from the bottom (most-negative-z) surface to
  the top. Ply z-coordinates are measured from the laminate mid-plane,
  so the stack is centered automatically from the given thicknesses.
- ``N`` is the in-plane force resultant (N/m, force per unit width) and
  ``M`` is the moment resultant (N, moment per unit width), each a
  3-vector ``[x, y, xy]`` component.
- A **symmetric** laminate (ply stack mirror-symmetric about the
  mid-plane) has ``B = 0`` exactly -- this is a standard CLT identity
  and is used here as a self-consistency check on the ABD assembly
  (see the test suite), not just an example property.

Assumptions
-----------
- Standard CLT assumptions: thin laminate, perfect bonding between
  plies, plane stress in each ply, Kirchhoff plate (straight normals
  remain straight and perpendicular to the mid-surface after
  deformation) -- no transverse shear deformation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from compositepy.lamina import ReducedStiffness, transform_stiffness

from laminatepy.exceptions import InvalidLaminateError


@dataclass(frozen=True)
class Ply:
    """One ply in a laminate stack.

    Parameters
    ----------
    thickness:
        Ply thickness, m, > 0.
    angle:
        Fiber angle, radians, measured from the laminate x-axis.
    stiffness:
        The ply material's reduced stiffness matrix in its own material
        axes (see :func:`compositepy.lamina.reduced_stiffness`) --
        shared across all plies of the same material.

    """

    thickness: float
    angle: float
    stiffness: ReducedStiffness

    def __post_init__(self) -> None:
        if self.thickness <= 0:
            raise InvalidLaminateError(f"ply thickness must be positive, got {self.thickness!r}")


@dataclass(frozen=True)
class ABDMatrix:
    """A laminate's extensional (A), coupling (B), and bending (D) stiffness matrices."""

    a: np.ndarray
    """Extensional stiffness, 3x3, N/m."""
    b: np.ndarray
    """Coupling stiffness, 3x3, N (couples in-plane loads to curvature and vice versa)."""
    d: np.ndarray
    """Bending stiffness, 3x3, N*m."""


def _q_bar_matrix(stiffness: ReducedStiffness, angle: float) -> np.ndarray:
    q_bar = transform_stiffness(stiffness, angle)
    return np.array(
        [
            [q_bar.q11, q_bar.q12, q_bar.q16],
            [q_bar.q12, q_bar.q22, q_bar.q26],
            [q_bar.q16, q_bar.q26, q_bar.q66],
        ]
    )


def compute_abd(plies: list[Ply]) -> ABDMatrix:
    """Assemble the ABD stiffness matrices for a laminate from its ply stack.

    ``A_ij = sum_k Q_bar_ij,k * (z_k - z_{k-1})``,
    ``B_ij = sum_k Q_bar_ij,k * (z_k^2 - z_{k-1}^2) / 2``,
    ``D_ij = sum_k Q_bar_ij,k * (z_k^3 - z_{k-1}^3) / 3``,
    where ``z_k`` are ply-interface coordinates measured from the
    laminate mid-plane.

    Parameters
    ----------
    plies:
        Ply stack, bottom to top, at least one ply.

    Returns
    -------
    ABDMatrix

    Raises
    ------
    InvalidLaminateError
        If ``plies`` is empty.

    Example
    -------
    A single 1 mm ply: A should equal Q_bar times the thickness, and B
    should be exactly zero (a single ply is trivially symmetric about
    its own mid-plane):

    >>> from compositepy.lamina import reduced_stiffness
    >>> q = reduced_stiffness(e1=181e9, e2=10.3e9, nu12=0.28, g12=7.17e9)
    >>> abd = compute_abd([Ply(thickness=0.001, angle=0.0, stiffness=q)])
    >>> round(float(abd.a[0, 0]) / 1e6, 3)
    181.811
    >>> float(abd.b[0, 0])
    0.0

    """
    if len(plies) == 0:
        raise InvalidLaminateError("plies must not be empty")

    total_thickness = sum(ply.thickness for ply in plies)
    z = -total_thickness / 2
    z_coords = [z]
    for ply in plies:
        z += ply.thickness
        z_coords.append(z)

    a = np.zeros((3, 3))
    b = np.zeros((3, 3))
    d = np.zeros((3, 3))
    for k, ply in enumerate(plies):
        q_bar = _q_bar_matrix(ply.stiffness, ply.angle)
        z_top, z_bottom = z_coords[k + 1], z_coords[k]
        a += q_bar * (z_top - z_bottom)
        b += q_bar * (z_top**2 - z_bottom**2) / 2
        d += q_bar * (z_top**3 - z_bottom**3) / 3

    return ABDMatrix(a=a, b=b, d=d)


def laminate_response(
    abd: ABDMatrix, force_resultant: np.ndarray, moment_resultant: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Solve for mid-plane strain and curvature given applied force/moment resultants.

    Solves ``[N; M] = [[A, B], [B, D]] @ [eps0; kappa]`` for
    ``[eps0; kappa]``.

    Parameters
    ----------
    abd:
        Laminate ABD matrices (see :func:`compute_abd`).
    force_resultant:
        In-plane force resultant ``[Nx, Ny, Nxy]``, N/m, shape ``(3,)``.
    moment_resultant:
        Moment resultant ``[Mx, My, Mxy]``, N, shape ``(3,)``.

    Returns
    -------
    (mid_plane_strain, curvature):
        Mid-plane strain ``[eps_x, eps_y, gamma_xy]`` (dimensionless)
        and curvature ``[kappa_x, kappa_y, kappa_xy]`` (1/m).

    Example
    -------
    >>> from compositepy.lamina import reduced_stiffness
    >>> import numpy as np
    >>> q = reduced_stiffness(e1=181e9, e2=10.3e9, nu12=0.28, g12=7.17e9)
    >>> abd = compute_abd([Ply(thickness=0.001, angle=0.0, stiffness=q)])
    >>> eps0, kappa = laminate_response(
    ...     abd, force_resultant=np.array([1e5, 0.0, 0.0]), moment_resultant=np.zeros(3)
    ... )
    >>> round(float(eps0[0]), 6)
    0.000552

    """
    force_resultant = np.asarray(force_resultant, dtype=float)
    moment_resultant = np.asarray(moment_resultant, dtype=float)
    if force_resultant.shape != (3,) or moment_resultant.shape != (3,):
        raise InvalidLaminateError(
            "force_resultant and moment_resultant must each have shape (3,)"
        )

    full_matrix = np.block([[abd.a, abd.b], [abd.b, abd.d]])
    loads = np.concatenate([force_resultant, moment_resultant])
    try:
        solution = np.linalg.solve(full_matrix, loads)
    except np.linalg.LinAlgError as exc:
        raise InvalidLaminateError(
            "the laminate's 6x6 ABD stiffness matrix is singular and cannot be solved "
            "(the ply stack may be degenerate, e.g. zero total thickness)"
        ) from exc

    return solution[:3], solution[3:]
