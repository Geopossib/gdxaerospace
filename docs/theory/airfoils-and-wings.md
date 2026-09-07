# Airfoils and finite wings

## NACA 4-digit series

For a NACA `MPTT` designation (max camber `M%`, camber position `P*10%`,
thickness `TT%`):

$$
y_t(x) = 5t \left(0.2969\sqrt{x} - 0.1260x - 0.3516x^2 + 0.2843x^3 - 0.1015x^4\right)
$$

with a two-segment parabolic-arc camber line meeting at $x = p$.
`airfoilpy` uses the closed-trailing-edge coefficient set by default
(the polynomial fit brings the residual gap at $x=1$ to about 0.1% of
chord — not exactly zero, since it's a 4-term least-squares fit, not an
exact closure).

## NACA 5-digit series

`airfoilpy` implements the standard (non-reflexed) 5-digit camber line,
restricted — as the original 1935 NACA report was — to a design lift
coefficient of 0.3 and the five published camber positions (5%-25% chord).

## Finite-wing corrections

`wingtools` corrects the 2D (infinite-wing) lift-curve slope for
finite-aspect-ratio effects. The Helmbold form
(`finite_wing_lift_curve_slope(..., model="helmbold")`, the default)
remains accurate down to AR ≈ 4, unlike the classic Prandtl lifting-line
result which assumes AR is large:

$$
a = \frac{a_0}{\sqrt{1 + \left(\dfrac{a_0}{\pi\, AR}\right)^2} + \dfrac{a_0}{\pi\, AR}}
$$

Induced drag follows directly from the span efficiency:

$$
C_{D,i} = \frac{C_L^2}{\pi\, e\, AR}
$$

`oswald_efficiency_estimate` is an empirical correlation (Raymer), not a
first-principles result — treat it as a conceptual-design estimate, not a
substitute for a real lifting-line or panel-method calculation of $e$.

## References

- Abbott, I.H. & Von Doenhoff, A.E., *Theory of Wing Sections*, Dover, 1959.
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 4-5.
- Raymer, D.P., *Aircraft Design: A Conceptual Approach*, 6th ed., Ch. 12.
