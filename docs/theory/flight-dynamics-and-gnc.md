# Flight dynamics, guidance, navigation, and control

`attitude3d`, `flightdyn`, `aircraftsim`, `guidancepy`, `navigationpy`,
`autopilotpy`, and `kalmanflight` together cover rigid-body flight
simulation and the classic GNC (guidance, navigation, control) stack
around it.

## Attitude representation (`attitude3d`)

Three equivalent representations of orientation — Euler angles (3-2-1
sequence), the direction cosine matrix (DCM), and quaternions — are kept
mutually consistent throughout the ecosystem. Quaternions avoid the
gimbal-lock singularity that Euler angles hit at ±90° pitch, which is why
`flightdyn`'s equations of motion integrate a quaternion internally even
though the API accepts and returns Euler angles at the boundary.

## Equations of motion (`flightdyn`)

Newton's second law in a *rotating* body frame picks up an extra term:

$$
\frac{dV}{dt} = \frac{F}{m} - \omega \times V, \qquad
I\dot{\omega} = M - \omega \times (I\omega)
$$

The second is Euler's equation for rigid-body rotation. Both are
implemented generically (accepting a full inertia matrix or a
no-products-of-inertia diagonal shortcut) rather than only in the
simplified scalar form many textbooks present first.

## Simulation (`aircraftsim`)

`Aircraft6DOF` composes `flightdyn`'s equations of motion with a generic
linear stability-derivative aerodynamic model and integrates the coupled
13-state system (position, body velocity, quaternion, body rates) with
fixed-step RK4. Its aerodynamic coefficients are explicitly **illustrative
defaults**, not validated flight data for any real aircraft — swap in real
derivatives for anything beyond demonstration.

## Guidance (`guidancepy`)

Proportional navigation commands lateral acceleration proportional to
closing velocity and line-of-sight rotation rate:

$$
a_{cmd} = N \, V_c \, \dot\lambda
$$

This is the guidance law behind most tactical missile systems — a
straight-line (zero-LOS-rate) collision course requires zero command,
and PN nulls out any LOS rotation that would otherwise develop.

## Navigation (`navigationpy`)

Great-circle distance and bearing use the haversine formula on a
spherical Earth (mean radius 6,371 km) — accurate to flight-planning
tolerances, not survey-grade. Dead reckoning solves the direct geodesic
problem: given a start point, bearing, and distance, where do you end up?

## Control (`autopilotpy`)

A standard PID controller with **conditional-integration anti-windup**:
when the output saturates and the integral term would push further into
saturation, the integral is frozen rather than allowed to keep growing
unboundedly — this is what prevents the large overshoot ("integrator
windup") that a naive PID exhibits after a big, sustained error.

## Estimation (`kalmanflight`)

The discrete linear Kalman filter fuses noisy measurements with a
dynamics model, weighting each by its uncertainty. The Joseph-form
covariance update, $P = (I-KH)P(I-KH)^T + KRK^T$, stays symmetric and
positive semi-definite even under numerical roundoff — more robust than
the textbook-simplest form, at the cost of a bit more arithmetic.

## References

- Stevens, B.L., Lewis, F.L. & Johnson, E.N., *Aircraft Control and
  Simulation*, 3rd ed.
- Etkin, B. & Reid, L.D., *Dynamics of Flight: Stability and Control*, 3rd ed.
- Zarchan, P., *Tactical and Strategic Missile Guidance*, 6th ed.
- Nelson, R.C., *Flight Stability and Automatic Control*, 2nd ed.
- Zarchan, P. & Musoff, H., *Fundamentals of Kalman Filtering*, 4th ed.
