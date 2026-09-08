# Propulsion

`aeroprop`, `rocketperf`, `nozzleanalysis`, `combustionpy`, and `turbomachpy`
cover air-breathing and rocket propulsion performance at the conceptual-design
level.

## Air-breathing thrust and efficiency (`aeroprop`)

$$
F = (\dot{m}_{air} + \dot{m}_{fuel}) V_e - \dot{m}_{air} V_0 + (p_e - p_a) A_e
$$

Propulsive (Froude) efficiency $\eta_p = \dfrac{2V_0}{V_0+V_e}$ shows the
fundamental trade in jet propulsion: efficiency improves as $V_e \to V_0$,
but thrust vanishes at the same limit — hence the drive toward high-bypass
turbofans (large mass flow, small $V_e - V_0$) for efficient cruise thrust.

## Rocket performance (`rocketperf`)

Effective exhaust velocity $c = F/\dot{m}$ and specific impulse
$I_{sp} = c/g_0$ characterize overall engine performance. Characteristic
velocity $c^* = p_c A_t / \dot{m}$ isolates combustion-chamber performance
from nozzle expansion, while thrust coefficient $C_F = F/(p_c A_t)$ isolates
the nozzle's contribution. The ideal (Tsiolkovsky) rocket equation,
$\Delta v = c \ln(m_0/m_f)$, excludes gravity and drag losses — real
launch $\Delta v$ requirements are always somewhat higher.

## Nozzle flow (`nozzleanalysis`)

A choked nozzle's mass flow depends only on chamber conditions and throat
area — not on what happens downstream. `nozzleanalysis` also inverts the
isentropic area-Mach relation from `compressibleflow` by bisection, since
it has no closed form, to find the Mach number for a given expansion ratio.

## Combustion (`combustionpy`)

Stoichiometric air-fuel ratio follows directly from balancing the
combustion equation. The temperature-rise estimate is a **simplified**
constant-cp energy balance — real flame/combustor temperature calculations
require temperature-dependent gas properties (or full chemical
equilibrium) for engineering accuracy; treat this module's output as a
conceptual-design screening estimate only.

## Turbomachinery (`turbomachpy`)

Compressor and turbine stage temperature change follows from the
isentropic relation and a stage isentropic efficiency:

$$
\Delta T_{c,actual} = \frac{T_1\left(\pi_c^{(\gamma-1)/\gamma} - 1\right)}{\eta_c}, \qquad
\Delta T_{t,actual} = \eta_t\, T_3\left(1 - \pi_t^{-(\gamma-1)/\gamma}\right)
$$

Note the efficiency appears in the denominator for a compressor (it always
needs more real work than ideal) and as a direct multiplier for a turbine
(it always extracts less real work than ideal) — this asymmetry is a
frequent source of sign errors and is exactly why `turbomachpy` exposes two
separate functions rather than one generic one.

## References

- Mattingly, J.D., *Elements of Gas Turbine Propulsion*, 2nd ed.
- Sutton, G.P. & Biblarz, O., *Rocket Propulsion Elements*, 9th ed.
- Turns, S.R., *An Introduction to Combustion*, 3rd ed.
- Cohen, H., Rogers, G.F.C. & Saravanamuttoo, H.I.H., *Gas Turbine Theory*,
  4th ed.
