"""kalmanflight — discrete linear Kalman filtering for GDX Aerospace."""

from __future__ import annotations

from kalmanflight.exceptions import InvalidKalmanFilterInputError
from kalmanflight.filter import KalmanFilter

__all__ = [
    "InvalidKalmanFilterInputError",
    "KalmanFilter",
]

__version__ = "0.1.0"
