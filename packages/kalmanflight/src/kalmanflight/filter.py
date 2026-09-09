"""A discrete-time linear Kalman filter.

Reference
---------
- Kalman, R.E., "A New Approach to Linear Filtering and Prediction
  Problems", *Journal of Basic Engineering*, 1960 (the original filter).
- Zarchan, P. & Musoff, H., *Fundamentals of Kalman Filtering: A
  Practical Approach*, 4th ed., AIAA, Ch. 4 (the standard aerospace/GNC
  reference for this exact predict/update formulation, including the
  constant-velocity tracking example used to validate this module).
- Simon, D., *Optimal State Estimation*, Wiley, 2006, Ch. 5, for the
  numerically-stable Joseph-form covariance update used here.

Convention
----------
- Standard discrete linear-Gaussian model:
  ``x_k = F x_{k-1} + B u_{k-1} + w_{k-1}``, ``w ~ N(0, Q)``
  ``z_k = H x_k + v_k``, ``v ~ N(0, R)``
- ``predict()`` propagates the state and covariance forward one step;
  ``update()`` incorporates a measurement. Call them in that order per
  filter cycle (predict, then update), as is standard practice.

Assumptions
-----------
- Linear time-invariant (or externally time-varying, if you pass new
  matrices to each call) system -- for genuinely nonlinear dynamics or
  measurement models, an Extended or Unscented Kalman Filter is required;
  this module implements only the linear case.
- The covariance update uses the Joseph form,
  ``P = (I-KH) P (I-KH)^T + K R K^T``, which remains symmetric and
  positive semi-definite even under small numerical errors or a
  suboptimal gain -- more robust than the simpler ``P = (I-KH)P`` form.
"""

from __future__ import annotations

import numpy as np

from kalmanflight.exceptions import InvalidKalmanFilterInputError


class KalmanFilter:
    """A discrete-time linear Kalman filter with fixed matrices.

    Parameters
    ----------
    x0:
        Initial state estimate, shape ``(n,)``.
    p0:
        Initial state covariance, shape ``(n, n)``.
    f:
        State transition matrix, shape ``(n, n)``.
    h:
        Measurement matrix, shape ``(m, n)``.
    q:
        Process noise covariance, shape ``(n, n)``.
    r:
        Measurement noise covariance, shape ``(m, m)``.

    Example
    -------
    A scalar (1-state) filter tracking a static quantity, hand-verifiable:
    starting from ``x=0, P=1``, after one predict (``F=1, Q=0``, so ``x``
    and ``P`` are unchanged) and one update against a measurement of 1
    with ``R=1``, the Kalman gain is ``K = P/(P+R) = 0.5``, giving
    ``x = 0 + 0.5*(1-0) = 0.5`` and ``P = (1-0.5)*1 = 0.5``.

    >>> import numpy as np
    >>> kf = KalmanFilter(
    ...     x0=np.array([0.0]), p0=np.array([[1.0]]),
    ...     f=np.array([[1.0]]), h=np.array([[1.0]]),
    ...     q=np.array([[0.0]]), r=np.array([[1.0]]),
    ... )
    >>> kf.predict()
    >>> kf.update(np.array([1.0]))
    >>> kf.x
    array([0.5])
    >>> kf.p
    array([[0.5]])

    """

    def __init__(
        self,
        x0: np.ndarray,
        p0: np.ndarray,
        f: np.ndarray,
        h: np.ndarray,
        q: np.ndarray,
        r: np.ndarray,
    ) -> None:
        self.x = np.asarray(x0, dtype=float)
        self.p = np.asarray(p0, dtype=float)
        self.f = np.asarray(f, dtype=float)
        self.h = np.asarray(h, dtype=float)
        self.q = np.asarray(q, dtype=float)
        self.r = np.asarray(r, dtype=float)

        n = self.x.shape[0]
        if self.p.shape != (n, n):
            raise InvalidKalmanFilterInputError(
                f"p0 must have shape ({n}, {n}), got {self.p.shape}"
            )
        if self.f.shape != (n, n):
            raise InvalidKalmanFilterInputError(
                f"f must have shape ({n}, {n}), got {self.f.shape}"
            )
        if self.q.shape != (n, n):
            raise InvalidKalmanFilterInputError(
                f"q must have shape ({n}, {n}), got {self.q.shape}"
            )
        if self.h.shape[1] != n:
            raise InvalidKalmanFilterInputError(f"h must have shape (m, {n}), got {self.h.shape}")
        m = self.h.shape[0]
        if self.r.shape != (m, m):
            raise InvalidKalmanFilterInputError(
                f"r must have shape ({m}, {m}), got {self.r.shape}"
            )

    def predict(self, u: np.ndarray | None = None, b: np.ndarray | None = None) -> None:
        """Propagate the state and covariance forward one time step.

        ``x = F x (+ B u)``, ``P = F P F^T + Q``.

        Parameters
        ----------
        u:
            Optional control input, shape ``(p,)``.
        b:
            Optional control input matrix, shape ``(n, p)``. Required if
            ``u`` is given.

        """
        self.x = self.f @ self.x
        if u is not None:
            if b is None:
                raise InvalidKalmanFilterInputError("b must be given if u is provided")
            self.x = self.x + np.asarray(b, dtype=float) @ np.asarray(u, dtype=float)
        self.p = self.f @ self.p @ self.f.T + self.q

    def update(self, z: np.ndarray) -> None:
        """Incorporate a measurement, updating the state and covariance estimates.

        ``y = z - H x`` (innovation), ``S = H P H^T + R``,
        ``K = P H^T S^-1``, ``x = x + K y``,
        ``P = (I-KH) P (I-KH)^T + K R K^T`` (Joseph form).

        Parameters
        ----------
        z:
            Measurement vector, shape ``(m,)``.

        """
        z = np.asarray(z, dtype=float)
        innovation = z - self.h @ self.x
        innovation_covariance = self.h @ self.p @ self.h.T + self.r
        kalman_gain = self.p @ self.h.T @ np.linalg.inv(innovation_covariance)

        self.x = self.x + kalman_gain @ innovation
        identity = np.eye(self.p.shape[0])
        i_kh = identity - kalman_gain @ self.h
        self.p = i_kh @ self.p @ i_kh.T + kalman_gain @ self.r @ kalman_gain.T
