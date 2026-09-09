"""attitude3d — attitude representation and kinematics for GDX Aerospace."""

from __future__ import annotations

from attitude3d.exceptions import InvalidAttitudeInputError
from attitude3d.rotations import (
    dcm_to_euler,
    dcm_to_quaternion,
    euler_to_dcm,
    euler_to_quaternion,
    quaternion_conjugate,
    quaternion_derivative,
    quaternion_multiply,
    quaternion_normalize,
    quaternion_to_dcm,
    quaternion_to_euler,
)

__all__ = [
    "InvalidAttitudeInputError",
    "dcm_to_euler",
    "dcm_to_quaternion",
    "euler_to_dcm",
    "euler_to_quaternion",
    "quaternion_conjugate",
    "quaternion_derivative",
    "quaternion_multiply",
    "quaternion_normalize",
    "quaternion_to_dcm",
    "quaternion_to_euler",
]

__version__ = "0.1.0"
