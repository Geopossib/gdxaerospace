# Compressible flow, shocks, and expansions

`compressibleflow` and `shockpy` implement the standard calorically-perfect-gas
relations for isentropic flow, normal/oblique shocks, and Prandtl-Meyer
expansions.

## Isentropic relations

$$
\frac{T_0}{T} = 1 + \frac{\gamma - 1}{2} M^2, \qquad
\frac{p_0}{p} = \left(\frac{T_0}{T}\right)^{\gamma/(\gamma-1)}, \qquad
\frac{\rho_0}{\rho} = \left(\frac{T_0}{T}\right)^{1/(\gamma-1)}
$$

## Normal shock

Across a normal shock with upstream Mach $M_1 > 1$:

$$
M_2^2 = \frac{1 + \frac{\gamma-1}{2}M_1^2}{\gamma M_1^2 - \frac{\gamma-1}{2}}, \qquad
\frac{p_2}{p_1} = 1 + \frac{2\gamma}{\gamma+1}(M_1^2 - 1)
$$

Stagnation pressure always decreases across a real (compression) shock —
`shockpy` returns `stagnation_pressure_ratio < 1` for every valid input, which
is a direct consequence of the second law of thermodynamics.

## Oblique shock (theta-beta-M)

`shockpy.oblique_shock` solves the implicit theta-beta-M relation by
bisection, then decomposes the flow into shock-normal and shock-tangential
components to apply the normal-shock relations. Two solutions generally
exist for a given deflection (weak/strong); `shockpy` defaults to the weak
solution, matching what is observed on most external surfaces. Beyond the
maximum deflection angle for a given Mach number, the shock detaches and
`shockpy` raises `DetachedShockError` rather than returning a bow-shock
approximation it does not model.

## Prandtl-Meyer expansion

Expansions around a convex corner are isentropic (`stagnation_pressure_ratio
== 1.0` always) and accelerate the flow. `shockpy.expansion_fan` inverts the
Prandtl-Meyer function by bisection since it has no closed-form inverse.

## References

- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 8-9.
