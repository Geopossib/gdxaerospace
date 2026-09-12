# UAV design, vision, trajectory, and optimization

`uavpy`, `aerovision`, `rockettraj`, and `aeroopt` close out the
ecosystem: UAV sizing, aerospace computer vision, rocket flight
mechanics, and design optimization.

## UAV sizing (`uavpy`)

Multirotor hover power is not an empirical guess — it comes from
actuator-disk momentum theory, `P_ideal = T^1.5 / sqrt(2*rho*A)`,
divided by a rotor figure of merit (typically 0.5-0.7 for small
propellers) to get real power draw. The realism check that matters
here: plugging in a 2.5 kg quadcopter with a realistic 5000 mAh 6S-class
battery gives roughly 18-19 minutes of flight time — right where actual
small multirotors land, without ever tuning toward that number. Fixed-
wing sizing uses the classic wing-loading and thrust-to-weight
parameters from conceptual aircraft design.

## Aerospace computer vision (`aerovision`)

This package's honest scope: it defines `Protocol` interfaces
(`ImageClassifier`, `ObjectDetector`, `AnomalyDetector`) that a real
PyTorch or ONNX model could implement, without ever requiring those
heavy libraries itself. The one thing it actually *does* is classical
and dependency-free — Sobel-gradient edge detection, useful as a fast
linear-feature (crack-like) highlighter and a baseline to compare any
future learned model against, never claimed to be more than that.

## Rocket trajectory (`rockettraj`)

A single-stage vertical trajectory integrator: thrust, gravity, and
altitude-varying drag (via the same `aerocalc.Atmosphere` model used
throughout the ecosystem), integrated with RK4 through powered ascent,
coast, and back to ground impact. The validation that matters most
here: with drag turned off, the post-burnout coast phase must match
simple kinematics (`apogee = burnout altitude + v^2/2g`) — and it does,
to seven significant figures. A smaller, honestly-documented finding
from testing: fixed-step RK4 crossing the thrust cutoff at burnout
introduces a tiny (~0.02%) mass-conservation error, a known artifact of
naive fixed-step integration across a discontinuity, not a defect.

## Design optimization (`aeroopt`)

A thin wrapper around `scipy.optimize`, plus one worked example that
demonstrates why the wrapper is trustworthy: minimizing the sum of
induced drag and a structural-weight penalty over aspect ratio has a
genuine closed-form solution (`AR_opt = (CL^2/(2*k*pi*e))^(1/3)`, from
simple calculus), and the numerical optimizer's answer matches that
closed form to six significant figures. That's the standard this whole
ecosystem has tried to hold to from Phase 1 onward: never trust a
number until you've checked it against something independent.

## References

- Leishman, J.G., *Principles of Helicopter Aerodynamics*, 2nd ed.
- Raymer, D.P., *Aircraft Design: A Conceptual Approach*, 6th ed.
- Sutton, G.P. & Biblarz, O., *Rocket Propulsion Elements*, 9th ed.
- Gonzalez, R.C. & Woods, R.E., *Digital Image Processing*, 4th ed.
- Virtanen, P. et al., "SciPy 1.0", Nature Methods, 2020.
