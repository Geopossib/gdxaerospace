# Thermal analysis, CFD automation, and flight data

`aerothermal`, `aerocfd`, and `aerodata` round out the ecosystem's
analysis toolchain: heat transfer, CFD workflow automation, and
telemetry/flight-test data reduction.

## Thermal analysis (`aerothermal`)

Three heat transfer mechanisms, three formulas: conduction (`Q =
kA*dT/L`), convection (`Q = hA*dT`), and radiation (`Q =
eps*sigma*A*(T_h^4-T_c^4)`). Thermal resistances combine exactly like
electrical resistances — series adds, parallel adds reciprocals — which
is why the resistance-network formulation is so useful for multi-layer
spacecraft thermal design.

The lumped-capacitance transient model assumes a body's internal
temperature is uniform (valid when the Biot number is small) and gives
a clean exponential relaxation toward ambient. Spacecraft equilibrium
temperature is a one-line energy balance: absorbed solar power in,
emitted thermal-IR power out — a genuinely useful first-order estimate,
though it ignores albedo, Earth-IR, eclipse cycling, and internal heat
generation.

## CFD automation (`aerocfd`)

This package automates *using* OpenFOAM — case-file generation,
execution, and force-coefficient post-processing — without ever
assuming OpenFOAM is installed. It checks for the solver binary on
PATH before attempting to run anything, and raises a clear error with
installation instructions if it isn't found, exactly the failure mode
you want instead of a cryptic subprocess crash. The generated case
files follow OpenFOAM's real dictionary ("FoamFile") text format, but
mesh generation is deliberately out of scope here — a mesh is
geometry-specific in a way that doesn't generalize into a template.

## Flight-test and telemetry data (`aerodata`)

Built on pandas: moving-average smoothing, linear resampling to a
uniform time base (a near-universal first step before frequency-domain
analysis of flight test data), and a z-score outlier screen. The
outlier detector shares its core idea — and its known limitation — with
`sattelemetry`'s statistical anomaly detection: a single extreme
outlier in a short series can inflate its own standard deviation enough
to partially mask itself, so it's most reliable over a reasonably long,
mostly-nominal history.

## References

- Incropera, F.P. & DeWitt, D.P., *Fundamentals of Heat and Mass Transfer*, 6th ed.
- Wertz, J.R. & Larson, W.J. (eds.), *Space Mission Analysis and Design*, 3rd ed.
- OpenFOAM User Guide.
- Klein, V. & Morelli, E.A., *Aircraft System Identification: Theory and Practice*, AIAA.
