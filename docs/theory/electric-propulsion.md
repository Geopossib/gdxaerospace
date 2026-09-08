# Electric propulsion and plasma physics

`electricprop`, `plasmathrust`, `plume3d`, and `plasmaspace` cover
ion/Hall-effect electric propulsion and the underlying plasma physics at
the conceptual-design and preliminary-analysis level.

## Ideal electrostatic acceleration (`electricprop`)

An ion of mass $M$ and charge $Ze$ accelerated from rest through a
voltage $V$ reaches an ideal exhaust velocity

$$
V_e = \sqrt{\frac{2 Z e V}{M}}
$$

Thrust follows from $F = \dot{m} V_e$, specific impulse from
$I_{sp} = V_e/g_0$, and total efficiency from
$\eta_T = F^2 / (2\dot{m}P)$. These are *ideal* relations — real
thrusters fall short due to beam divergence (`plume3d`), multiply-charged
ions, and ionization losses not modeled here.

## Fundamental plasma parameters (`plasmathrust`)

Debye length $\lambda_D$ sets the scale over which a plasma screens
electric fields; the Hall parameter $\beta = \omega_c/\nu_{coll}$
(gyrations per collision) is the figure of merit that makes Hall-effect
thrusters work — a magnetic field magnetizes the much-lighter electrons
(large $\beta$) while leaving the heavy ions essentially unmagnetized,
creating an azimuthal Hall current that ionizes and accelerates
propellant without physical grids.

## Plume divergence (`plume3d`)

Ions don't all leave exactly along the thrust axis. `plume3d` uses the
simplest possible correction — a single effective divergence half-angle
$\theta$, with $F_{eff} = F_{ideal}\cos\theta$ — and is explicit that this
is an optimistic upper bound relative to integrating a real (measured or
Gaussian) angular current-density profile.

## Spacecraft-plasma interaction (`plasmaspace`)

An isolated conductor in a plasma floats negative of the local plasma
potential, because unretarded electrons would otherwise arrive far
faster than the much heavier ions. Balancing the retarded electron
thermal flux against the Bohm ion flux gives

$$
V_f = -\frac{kT_e}{2e}\ln\!\left(\frac{M}{2\pi m_e}\right)
$$

which reproduces the well-known reference coefficients
($V_f \approx -4.68\,T_e[\text{eV}]$ for argon,
$\approx -5.27\,T_e[\text{eV}]$ for xenon). This captures only the
plasma-current-balance piece of spacecraft charging — real spacecraft
charging analysis must also account for photoemission (which can drive
sunlit surfaces positive), secondary-electron emission, and differential
charging between surfaces, none of which `plasmaspace` models. GDX
Aerospace does not claim to replace NASCAP or SPIS for a flight charging
assessment.

## References

- Goebel, D.M. & Katz, I., *Fundamentals of Electric Propulsion: Ion and
  Hall Thrusters*, JPL Space Science and Technology Series, 2008.
- Chen, F.F., *Introduction to Plasma Physics and Controlled Fusion*,
  3rd ed.
- Lieberman, M.A. & Lichtenberg, A.J., *Principles of Plasma Discharges
  and Materials Processing*, 2nd ed.
- Hastings, D. & Garrett, H., *Spacecraft-Environment Interactions*,
  Cambridge, 1996.
