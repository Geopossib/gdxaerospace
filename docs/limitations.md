# Limitations and disclaimer

GDX Aerospace is an engineering research and education library.

- Every model exposed here is a simplification of real physics; the specific
  assumptions are documented in each module's docstring and in `docs/theory/`.
- Where a phenomenon has more than one accepted model, GDX Aerospace exposes
  the model as an explicit parameter rather than silently picking one.
- **No output from this library should be treated as certified
  flight-critical engineering analysis.** Results that will inform a real
  flight, launch, or structural decision must be independently verified by
  a licensed engineer against the applicable standards.
- Phase 1 covers only the standard atmosphere and basic flow properties.
  Aerodynamic coefficients, structural analysis, propulsion, and other
  disciplines are not yet implemented — see the README roadmap.
