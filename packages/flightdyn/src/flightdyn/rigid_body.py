"""Rigid-body 6-DOF equations of motion: translational and rotational dynamics.

Reference
---------
- Stevens, B.L., Lewis, F.L. & Johnson, E.N., *Aircraft Control and
  Simulation*, 3rd ed., Ch. 1 (Eq. 1.7-18 body-axes translational
  equations; Eq. 1.7-19 rotational/Euler equations).
- Etkin, B. & Reid, L.D., *Dynamics of Flight: Stability and Control*,
  3rd ed., Ch. 4, for the same equations in a slightly different notation.

Convention
----------
- All vector quantities are expressed in the body-fixed frame (x forward,
  y right, z down, right-handed) unless otherwise noted.
- Attitude is represented via a DCM ``L`` from :mod:`attitude3d` such that
  ``v_body = L @ v_inertial``.
- Gravity uses a flat, non-rotating Earth (NED inertial frame) --
  adequate for atmospheric flight dynamics, not for problems where
  Earth's curvature or rotation matters (e.g. long-range ballistic or
  orbital trajectories -- see the ``orbitpy`` package for those).
"""

from __future__ import annotations

import numpy as np

from flightdyn.exceptions import InvalidFlightDynamicsInputError

#: Standard gravitational acceleration, m/s^2.
G0 = 9.80665


def translational_acceleration(
    velocity_body: np.ndarray,
    angular_velocity_body: np.ndarray,
    force_body: np.ndarray,
    mass: float,
) -> np.ndarray:
    """Body-axes translational acceleration: ``dV/dt = F/m - omega x V``.

    The ``-omega x V`` (Coriolis-like) term accounts for the body frame
    itself rotating; it vanishes for a non-rotating body (pure Newton's
    second law) and must be included whenever ``angular_velocity_body``
    is nonzero.

    Parameters
    ----------
    velocity_body:
        Body-frame velocity ``[u, v, w]``, m/s, shape ``(3,)``.
    angular_velocity_body:
        Body-frame angular velocity ``[p, q, r]``, rad/s, shape ``(3,)``.
    force_body:
        Total body-frame force (aerodynamic + propulsive + gravity), N,
        shape ``(3,)``.
    mass:
        Vehicle mass, kg, > 0.

    Returns
    -------
    numpy.ndarray
        ``dV/dt``, shape ``(3,)``, m/s^2.

    Example
    -------
    >>> import numpy as np
    >>> dv = translational_acceleration(
    ...     velocity_body=np.zeros(3),
    ...     angular_velocity_body=np.zeros(3),
    ...     force_body=np.array([1000.0, 0.0, 0.0]),
    ...     mass=1000.0,
    ... )
    >>> dv
    array([1., 0., 0.])

    """
    if mass <= 0:
        raise InvalidFlightDynamicsInputError(f"mass must be positive, got {mass!r}")
    v = np.asarray(velocity_body, dtype=float)
    omega = np.asarray(angular_velocity_body, dtype=float)
    f = np.asarray(force_body, dtype=float)
    if v.shape != (3,) or omega.shape != (3,) or f.shape != (3,):
        raise InvalidFlightDynamicsInputError(
            "velocity_body, angular_velocity_body, and force_body must each have shape (3,)"
        )
    return f / mass - np.cross(omega, v)


def rotational_acceleration(
    angular_velocity_body: np.ndarray, moment_body: np.ndarray, inertia: np.ndarray
) -> np.ndarray:
    """Compute body-axes rotational acceleration (Euler's equations).

    ``I domega/dt = M - omega x (I omega)``

    Parameters
    ----------
    angular_velocity_body:
        Body-frame angular velocity ``[p, q, r]``, rad/s, shape ``(3,)``.
    moment_body:
        Total body-frame moment about the center of mass, N*m, shape ``(3,)``.
    inertia:
        3x3 inertia matrix (or a length-3 array of principal moments
        ``[Ixx, Iyy, Izz]`` for a body with no products of inertia, which
        is automatically expanded to a diagonal matrix).

    Returns
    -------
    numpy.ndarray
        ``domega/dt``, shape ``(3,)``, rad/s^2.

    Example
    -------
    >>> import numpy as np
    >>> domega = rotational_acceleration(
    ...     angular_velocity_body=np.zeros(3),
    ...     moment_body=np.array([0.0, 100.0, 0.0]),
    ...     inertia=np.array([1500.0, 2000.0, 3000.0]),
    ... )
    >>> np.round(domega, 4)
    array([0.  , 0.05, 0.  ])

    """
    omega = np.asarray(angular_velocity_body, dtype=float)
    m = np.asarray(moment_body, dtype=float)
    inertia = np.asarray(inertia, dtype=float)
    if omega.shape != (3,) or m.shape != (3,):
        raise InvalidFlightDynamicsInputError(
            "angular_velocity_body and moment_body must each have shape (3,)"
        )
    if inertia.shape == (3,):
        inertia_matrix = np.diag(inertia)
    elif inertia.shape == (3, 3):
        inertia_matrix = inertia
    else:
        raise InvalidFlightDynamicsInputError(
            f"inertia must have shape (3,) or (3, 3), got {inertia.shape}"
        )
    gyroscopic_term = np.cross(omega, inertia_matrix @ omega)
    return np.linalg.solve(inertia_matrix, m - gyroscopic_term)


def gravity_body_frame(dcm_inertial_to_body: np.ndarray, *, g0: float = G0) -> np.ndarray:
    """Gravitational force per unit mass, resolved into the body frame.

    Assumes a flat-Earth NED inertial frame, where gravity acts purely
    along the inertial +Z (down) axis.

    Parameters
    ----------
    dcm_inertial_to_body:
        3x3 DCM ``L`` such that ``v_body = L @ v_inertial`` (see
        :mod:`attitude3d`).
    g0:
        Gravitational acceleration, m/s^2.

    Returns
    -------
    numpy.ndarray
        Gravity vector in the body frame, m/s^2, shape ``(3,)``.

    Example
    -------
    >>> import numpy as np
    >>> g_body = gravity_body_frame(np.eye(3))
    >>> np.round(g_body, 5)
    array([0.     , 0.     , 9.80665])

    """
    dcm = np.asarray(dcm_inertial_to_body, dtype=float)
    if dcm.shape != (3, 3):
        raise InvalidFlightDynamicsInputError(f"dcm must have shape (3, 3), got {dcm.shape}")
    return dcm @ np.array([0.0, 0.0, g0])


def position_derivative(dcm_inertial_to_body: np.ndarray, velocity_body: np.ndarray) -> np.ndarray:
    """Inertial-frame position rate from body-frame velocity: ``dP/dt = L^T @ V_body``.

    Since the DCM is orthonormal, its transpose is its inverse, mapping
    body-frame quantities back to the inertial frame.

    Parameters
    ----------
    dcm_inertial_to_body:
        3x3 DCM ``L`` such that ``v_body = L @ v_inertial``.
    velocity_body:
        Body-frame velocity ``[u, v, w]``, m/s, shape ``(3,)``.

    Returns
    -------
    numpy.ndarray
        Inertial-frame position rate, m/s, shape ``(3,)``.

    Example
    -------
    >>> import numpy as np
    >>> position_derivative(np.eye(3), np.array([100.0, 0.0, 0.0]))
    array([100.,   0.,   0.])

    """
    dcm = np.asarray(dcm_inertial_to_body, dtype=float)
    v = np.asarray(velocity_body, dtype=float)
    if dcm.shape != (3, 3) or v.shape != (3,):
        raise InvalidFlightDynamicsInputError(
            "dcm_inertial_to_body must have shape (3, 3) and velocity_body must have shape (3,)"
        )
    return dcm.T @ v
