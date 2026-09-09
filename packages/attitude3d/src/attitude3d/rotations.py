"""Attitude representation conversions: Euler angles, DCM, and quaternions.

Reference
---------
- Stevens, B.L., Lewis, F.L. & Johnson, E.N., *Aircraft Control and
  Simulation*, 3rd ed., Ch. 1 (Euler-angle/DCM/quaternion definitions and
  the 3-2-1 rotation sequence used throughout aircraft flight dynamics).
- Shepperd, S.W., "Quaternion from Rotation Matrix", *Journal of Guidance
  and Control*, 1978, for the numerically robust (gimbal-lock-safe)
  DCM-to-quaternion algorithm used in :func:`dcm_to_quaternion`.
- Markley, F.L. & Crassidis, J.L., *Fundamentals of Spacecraft Attitude
  Determination and Control*, Springer, 2014, Ch. 2, for the same
  algorithm in a spacecraft-attitude context.

Conventions
-----------
- Euler angles use the standard aerospace 3-2-1 (yaw-pitch-roll) sequence:
  ``(roll, pitch, yaw) = (phi, theta, psi)``, all in radians. The
  resulting DCM ``L`` transforms a vector from the inertial (or local
  reference) frame into the body frame: ``v_body = L @ v_inertial``.
- Quaternions are ``[q0, q1, q2, q3]`` with ``q0`` the scalar
  (real) part, representing the same inertial-to-body rotation as the
  DCM above, normalized to unit length.
- Gimbal lock occurs at ``theta = +/- 90 deg``, where ``dcm_to_euler``
  cannot uniquely recover roll and yaw separately (only their sum/
  difference is determined); this module does not special-case it beyond
  what the underlying ``atan2``/``asin`` calls do.
"""

from __future__ import annotations

import math

import numpy as np

from attitude3d.exceptions import InvalidAttitudeInputError


def euler_to_dcm(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """3-2-1 Euler angles to DCM (inertial-to-body direction cosine matrix).

    Parameters
    ----------
    roll, pitch, yaw:
        Euler angles (phi, theta, psi), radians.

    Returns
    -------
    numpy.ndarray
        3x3 DCM such that ``v_body = L @ v_inertial``.

    Example
    -------
    >>> import numpy as np
    >>> L = euler_to_dcm(0.0, 0.0, 0.0)
    >>> np.allclose(L, np.eye(3))
    True

    """
    cphi, sphi = math.cos(roll), math.sin(roll)
    cth, sth = math.cos(pitch), math.sin(pitch)
    cpsi, spsi = math.cos(yaw), math.sin(yaw)
    return np.array(
        [
            [cth * cpsi, cth * spsi, -sth],
            [sphi * sth * cpsi - cphi * spsi, sphi * sth * spsi + cphi * cpsi, sphi * cth],
            [cphi * sth * cpsi + sphi * spsi, cphi * sth * spsi - sphi * cpsi, cphi * cth],
        ]
    )


def dcm_to_euler(dcm: np.ndarray) -> tuple[float, float, float]:
    """Convert a DCM to 3-2-1 Euler angles.

    Parameters
    ----------
    dcm:
        3x3 inertial-to-body DCM.

    Returns
    -------
    (roll, pitch, yaw):
        Euler angles, radians. Near ``pitch = +/- 90 deg`` (gimbal lock),
        roll and yaw are not individually well-defined; this function
        still returns *a* consistent answer via ``atan2``, but only their
        combination is physically meaningful there.

    Example
    -------
    >>> import math
    >>> L = euler_to_dcm(math.radians(15), math.radians(-10), math.radians(30))
    >>> roll, pitch, yaw = dcm_to_euler(L)
    >>> [round(math.degrees(a), 3) for a in (roll, pitch, yaw)]
    [15.0, -10.0, 30.0]

    """
    dcm = np.asarray(dcm, dtype=float)
    if dcm.shape != (3, 3):
        raise InvalidAttitudeInputError(f"dcm must be a 3x3 matrix, got shape {dcm.shape}")
    pitch = -math.asin(np.clip(dcm[0, 2], -1.0, 1.0))
    yaw = math.atan2(dcm[0, 1], dcm[0, 0])
    roll = math.atan2(dcm[1, 2], dcm[2, 2])
    return roll, pitch, yaw


def euler_to_quaternion(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """3-2-1 Euler angles to a unit quaternion ``[q0, q1, q2, q3]``.

    Parameters
    ----------
    roll, pitch, yaw:
        Euler angles, radians.

    Returns
    -------
    numpy.ndarray
        Unit quaternion, scalar-first, representing the same
        inertial-to-body rotation as :func:`euler_to_dcm`.

    Example
    -------
    >>> import math
    >>> q = euler_to_quaternion(math.radians(15), math.radians(-10), math.radians(30))
    >>> round(float(np.linalg.norm(q)), 9)
    1.0

    """
    cphi2, sphi2 = math.cos(roll / 2), math.sin(roll / 2)
    cth2, sth2 = math.cos(pitch / 2), math.sin(pitch / 2)
    cpsi2, spsi2 = math.cos(yaw / 2), math.sin(yaw / 2)
    q0 = cphi2 * cth2 * cpsi2 + sphi2 * sth2 * spsi2
    q1 = sphi2 * cth2 * cpsi2 - cphi2 * sth2 * spsi2
    q2 = cphi2 * sth2 * cpsi2 + sphi2 * cth2 * spsi2
    q3 = cphi2 * cth2 * spsi2 - sphi2 * sth2 * cpsi2
    return np.array([q0, q1, q2, q3])


def quaternion_to_dcm(q: np.ndarray) -> np.ndarray:
    """Convert a unit quaternion to a DCM (inertial-to-body direction cosine matrix).

    Parameters
    ----------
    q:
        Unit quaternion ``[q0, q1, q2, q3]``, scalar-first.

    Returns
    -------
    numpy.ndarray
        3x3 DCM such that ``v_body = L @ v_inertial``.

    Example
    -------
    >>> import numpy as np
    >>> L = quaternion_to_dcm(np.array([1.0, 0.0, 0.0, 0.0]))
    >>> np.allclose(L, np.eye(3))
    True

    """
    q = np.asarray(q, dtype=float)
    if q.shape != (4,):
        raise InvalidAttitudeInputError(f"q must have shape (4,), got shape {q.shape}")
    q0, q1, q2, q3 = q
    return np.array(
        [
            [q0**2 + q1**2 - q2**2 - q3**2, 2 * (q1 * q2 + q0 * q3), 2 * (q1 * q3 - q0 * q2)],
            [2 * (q1 * q2 - q0 * q3), q0**2 - q1**2 + q2**2 - q3**2, 2 * (q2 * q3 + q0 * q1)],
            [2 * (q1 * q3 + q0 * q2), 2 * (q2 * q3 - q0 * q1), q0**2 - q1**2 - q2**2 + q3**2],
        ]
    )


def dcm_to_quaternion(dcm: np.ndarray) -> np.ndarray:
    """DCM to unit quaternion, via Shepperd's numerically robust algorithm.

    Selects the largest of ``{trace, L[0,0], L[1,1], L[2,2]}`` as the
    pivot for the square root, avoiding the numerical blow-up a naive
    trace-only formula suffers near gimbal lock / 180-degree rotations.

    Parameters
    ----------
    dcm:
        3x3 inertial-to-body DCM.

    Returns
    -------
    numpy.ndarray
        Unit quaternion ``[q0, q1, q2, q3]``, scalar-first.

    Example
    -------
    >>> import numpy as np
    >>> q = dcm_to_quaternion(np.eye(3))
    >>> np.allclose(q, [1.0, 0.0, 0.0, 0.0])
    True

    """
    dcm = np.asarray(dcm, dtype=float)
    if dcm.shape != (3, 3):
        raise InvalidAttitudeInputError(f"dcm must be a 3x3 matrix, got shape {dcm.shape}")

    trace = dcm[0, 0] + dcm[1, 1] + dcm[2, 2]
    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2
        q0 = 0.25 * s
        q1 = (dcm[1, 2] - dcm[2, 1]) / s
        q2 = (dcm[2, 0] - dcm[0, 2]) / s
        q3 = (dcm[0, 1] - dcm[1, 0]) / s
    elif dcm[0, 0] > dcm[1, 1] and dcm[0, 0] > dcm[2, 2]:
        s = math.sqrt(1.0 + dcm[0, 0] - dcm[1, 1] - dcm[2, 2]) * 2
        q0 = (dcm[1, 2] - dcm[2, 1]) / s
        q1 = 0.25 * s
        q2 = (dcm[0, 1] + dcm[1, 0]) / s
        q3 = (dcm[0, 2] + dcm[2, 0]) / s
    elif dcm[1, 1] > dcm[2, 2]:
        s = math.sqrt(1.0 + dcm[1, 1] - dcm[0, 0] - dcm[2, 2]) * 2
        q0 = (dcm[2, 0] - dcm[0, 2]) / s
        q1 = (dcm[0, 1] + dcm[1, 0]) / s
        q2 = 0.25 * s
        q3 = (dcm[1, 2] + dcm[2, 1]) / s
    else:
        s = math.sqrt(1.0 + dcm[2, 2] - dcm[0, 0] - dcm[1, 1]) * 2
        q0 = (dcm[0, 1] - dcm[1, 0]) / s
        q1 = (dcm[0, 2] + dcm[2, 0]) / s
        q2 = (dcm[1, 2] + dcm[2, 1]) / s
        q3 = 0.25 * s
    return np.array([q0, q1, q2, q3])


def quaternion_to_euler(q: np.ndarray) -> tuple[float, float, float]:
    """Convert a unit quaternion to 3-2-1 Euler angles.

    Parameters
    ----------
    q:
        Unit quaternion ``[q0, q1, q2, q3]``, scalar-first.

    Returns
    -------
    (roll, pitch, yaw):
        Euler angles, radians.

    Example
    -------
    >>> import math
    >>> q = euler_to_quaternion(math.radians(15), math.radians(-10), math.radians(30))
    >>> roll, pitch, yaw = quaternion_to_euler(q)
    >>> [round(math.degrees(a), 3) for a in (roll, pitch, yaw)]
    [15.0, -10.0, 30.0]

    """
    q = np.asarray(q, dtype=float)
    if q.shape != (4,):
        raise InvalidAttitudeInputError(f"q must have shape (4,), got shape {q.shape}")
    q0, q1, q2, q3 = q
    pitch = -math.asin(np.clip(2 * (q1 * q3 - q0 * q2), -1.0, 1.0))
    roll = math.atan2(2 * (q2 * q3 + q0 * q1), q0**2 - q1**2 - q2**2 + q3**2)
    yaw = math.atan2(2 * (q1 * q2 + q0 * q3), q0**2 + q1**2 - q2**2 - q3**2)
    return roll, pitch, yaw


def quaternion_multiply(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Hamilton quaternion product ``q (x) p``.

    Parameters
    ----------
    q, p:
        Quaternions ``[q0, q1, q2, q3]``, scalar-first.

    Returns
    -------
    numpy.ndarray
        The product quaternion.

    Example
    -------
    >>> import numpy as np
    >>> identity = np.array([1.0, 0.0, 0.0, 0.0])
    >>> q = np.array([0.9659258, 0.258819, 0.0, 0.0])
    >>> np.allclose(quaternion_multiply(identity, q), q)
    True

    """
    q0, q1, q2, q3 = q
    p0, p1, p2, p3 = p
    return np.array(
        [
            q0 * p0 - q1 * p1 - q2 * p2 - q3 * p3,
            q0 * p1 + q1 * p0 + q2 * p3 - q3 * p2,
            q0 * p2 - q1 * p3 + q2 * p0 + q3 * p1,
            q0 * p3 + q1 * p2 - q2 * p1 + q3 * p0,
        ]
    )


def quaternion_conjugate(q: np.ndarray) -> np.ndarray:
    """Quaternion conjugate ``[q0, -q1, -q2, -q3]`` (the inverse rotation, for a unit quaternion).

    Example:
    -------
    >>> import numpy as np
    >>> quaternion_conjugate(np.array([0.5, 0.5, 0.5, 0.5]))
    array([ 0.5, -0.5, -0.5, -0.5])

    """
    q = np.asarray(q, dtype=float)
    return np.array([q[0], -q[1], -q[2], -q[3]])


def quaternion_normalize(q: np.ndarray) -> np.ndarray:
    """Normalize a quaternion to unit length.

    Numerical integration of the quaternion kinematic equation
    (:func:`quaternion_derivative`) drifts away from unit norm over time;
    renormalizing periodically (e.g. once per integration step) keeps the
    quaternion a valid rotation representation.

    Raises:
    ------
    InvalidAttitudeInputError
        If ``q`` has near-zero norm (not a valid rotation quaternion).

    Example:
    -------
    >>> import numpy as np
    >>> round(float(np.linalg.norm(quaternion_normalize(np.array([2.0, 0.0, 0.0, 0.0])))), 9)
    1.0

    """
    q = np.asarray(q, dtype=float)
    norm = float(np.linalg.norm(q))
    if norm < 1e-12:
        raise InvalidAttitudeInputError(
            f"quaternion norm is too close to zero ({norm!r}) to normalize"
        )
    return q / norm


def quaternion_derivative(q: np.ndarray, angular_velocity: np.ndarray) -> np.ndarray:
    """Quaternion kinematic derivative: ``dq/dt`` from body angular rates.

    ``dq/dt = 1/2 * q (x) [0, p, q, r]`` where ``(p, q, r)`` are the body
    angular rates and ``(x)`` is the Hamilton product (Stevens & Lewis
    Eq. 1.8-15).

    Parameters
    ----------
    q:
        Current unit quaternion ``[q0, q1, q2, q3]``, scalar-first.
    angular_velocity:
        Body-frame angular rates ``[p, q, r]``, rad/s.

    Returns
    -------
    numpy.ndarray
        ``dq/dt``, same shape as ``q``.

    Example
    -------
    >>> import numpy as np
    >>> q0 = np.array([1.0, 0.0, 0.0, 0.0])
    >>> qdot = quaternion_derivative(q0, np.array([0.1, 0.0, 0.0]))
    >>> np.allclose(qdot, [0.0, 0.05, 0.0, 0.0])
    True

    """
    q = np.asarray(q, dtype=float)
    omega = np.asarray(angular_velocity, dtype=float)
    if q.shape != (4,):
        raise InvalidAttitudeInputError(f"q must have shape (4,), got shape {q.shape}")
    if omega.shape != (3,):
        raise InvalidAttitudeInputError(
            f"angular_velocity must have shape (3,), got shape {omega.shape}"
        )
    omega_quat = np.array([0.0, omega[0], omega[1], omega[2]])
    return 0.5 * quaternion_multiply(q, omega_quat)
