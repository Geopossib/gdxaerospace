# Structures and materials

`aeromaterials`, `aerostruct`, `stresspy`, `sparcalc`, `bucklingpy`,
`fatiguepy`, `compositepy`, and `laminatepy` cover metallic and
composite structural analysis, from material properties through
stress, buckling, fatigue, and laminate theory.

## Materials (`aeromaterials`)

A small, honestly-sourced database — five materials, every value cited
to MMPDS-01/ASM or the governing ASTM specification, with explicit
caveats where strength is too heat-treatment-dependent to responsibly
quote a single number (4340 steel's strength, for instance, varies
enormously with tempering — the database says so rather than picking
one value and hiding the caveat).

## Section properties (`aerostruct`)

Bending stiffness depends on how material is distributed relative to
the neutral axis, not just how much material there is — an I-beam
resists bending far better than a solid rectangle of the same area,
because moving material away from the neutral axis and using the
parallel-axis theorem (`I = I_c + A·d²`) to account for it captures most
of a structural section's design logic in one formula.

## Stress and failure (`stresspy`)

Axial, bending, and torsional stress are single formulas; combining
them into a 2D stress state is where Mohr's circle and von Mises
equivalent stress come in. Two invariants worth knowing: the trace
`σ₁+σ₂ = σₓ+σᵧ` is preserved under any principal-stress transform, and
pure shear gives von Mises stress of exactly `√3·τ` — both checked
directly in this package's test suite rather than assumed.

## Beams and buckling (`sparcalc`, `bucklingpy`)

A cantilever spar's tip deflection scales with the *cube* of its length
(`δ = PL³/3EI`) — double the span and deflection goes up 8×, which is
why wing spar sizing gets harder fast as span increases. Euler buckling
is exquisitely sensitive to end conditions: a fixed-fixed column
carries **16 times** the buckling load of an otherwise-identical
fixed-free (cantilever) column at the same length, since buckling load
scales as `1/K²` and K ranges from 0.5 to 2.0 across the four standard
conditions.

## Fatigue (`fatiguepy`)

The Basquin power law, `σₐ = A·Nᵇ`, fits remarkably well across many
decades of cycle life despite its simplicity. Miner's rule then sums
damage fractions (`n/N`) linearly across different stress levels — a
useful engineering approximation, not an exact law, since it ignores
load-sequence effects entirely.

## Composites (`compositepy`, `laminatepy`)

A unidirectional composite lamina is wildly anisotropic — for the
canonical T300/5208 graphite-epoxy system used throughout this
package's tests, the fiber-direction stiffness (`Q11 ~182 GPa`) is
over 17x the transverse stiffness (`Q22 ~10.3 GPa`). Classical
Laminate Theory assembles a stack of these anisotropic plies, each at
its own angle, into a single equivalent plate stiffness (the `A`, `B`,
`D` matrices). The single most important identity in CLT -- and the one
this package's test suite leans on hardest -- is that a laminate
symmetric about its mid-plane has **exactly zero** coupling stiffness
(`B = 0`), decoupling in-plane loading from bending entirely.

## References

- MMPDS-01, *Metallic Materials Properties Development and
  Standardization*.
- Hibbeler, R.C., *Mechanics of Materials*, 10th ed.
- Megson, T.H.G., *Aircraft Structures for Engineering Students*, 6th ed.
- Timoshenko, S.P. & Gere, J.M., *Theory of Elastic Stability*, 2nd ed.
- Dowling, N.E., *Mechanical Behavior of Materials*, 4th ed.
- Jones, R.M., *Mechanics of Composite Materials*, 2nd ed.
