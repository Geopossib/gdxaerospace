# Orbital mechanics, propagation, and mission analysis

`orbitpy`, `tletools`, `satprop`, `groundtrack`, `missionpy`, and
`constellationpy` cover two-body orbital mechanics, real-world satellite
tracking, and mission-design geometry.

## A note on scope: wrap, don't reinvent

Orbital propagation from real tracking data (TLEs) is a mature, heavily
validated problem — libraries like `sgp4` and Skyfield represent decades
of institutional effort. GDX Aerospace does not reimplement SGP4;
`satprop` wraps the MIT-licensed `sgp4` package directly. What GDX
Aerospace adds is the two-body Keplerian mechanics that has no equivalent
incumbent worth deferring to (`orbitpy`), TLE text parsing with its own
validation (`tletools`), and the mission-design layer on top
(`groundtrack`, `missionpy`, `constellationpy`).

## Two-body mechanics (`orbitpy`)

Classical orbital elements (semi-major axis, eccentricity, inclination,
RAAN, argument of periapsis, true anomaly) convert to and from Cartesian
state vectors via Vallado's standard algorithms — verified here by
round-tripping through circular, elliptical, equatorial, and polar test
cases and recovering the original elements exactly.

Kepler's equation, $M = E - e\sin E$, has no closed-form solution and is
solved by Newton-Raphson. The vis-viva equation, $v = \sqrt{\mu(2/r -
1/a)}$, gives speed anywhere on an orbit from its semi-major axis alone.

Hohmann and bi-elliptic transfers trade total delta-v against transfer
time. Bi-elliptic only wins for large radius ratios — the crossover point
(~11.94, per Vallado) is confirmed directly in this package's test suite
by computing both transfer types on either side of that threshold.

## TLEs and propagation (`tletools`, `satprop`)

A Two-Line Element set is a fixed-column text format with a mod-10
checksum on each line. `tletools` parses every field (epoch, drag terms,
orbital elements) and validates checksums; `satprop` hands the raw lines
to `sgp4` for actual propagation, since TLEs encode a specific
perturbation theory (SGP4/SDP4) that only that theory's own propagator
interprets correctly.

SGP4 accuracy degrades away from the TLE's epoch — always propagate from
a *current* TLE for the time of interest, not an old one.

## Ground track and visibility (`groundtrack`)

Converting a satellite's inertial position to a ground track requires
knowing how far Earth has rotated since a reference epoch — Greenwich
Mean Sidereal Time. From there, ECI-to-ECEF is a single rotation, and
ECEF-to-geodetic latitude/longitude/altitude requires iterating against
the WGS84 ellipsoid (Earth isn't a sphere, so this doesn't have a trivial
closed form except at the poles and equator).

## Mission analysis (`missionpy`, `constellationpy`)

Eclipse fraction follows from simple shadow-cylinder geometry: a LEO
satellite spends roughly a third to 40% of every orbit in Earth's shadow
at worst-case beta angle. A Walker Delta constellation ("i:t/p/f"
notation) spaces satellites evenly across planes and within each plane,
with a phasing factor controlling how planes offset from each other —
the pattern behind most communications and navigation constellations
(GPS, Starlink, Iridium).

## References

- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th ed.
- Curtis, H.D., *Orbital Mechanics for Engineering Students*, 3rd ed.
- Vallado et al., "Revisiting Spacetrack Report #3", AIAA 2006-6753.
- Wertz, J.R. & Larson, W.J. (eds.), *Space Mission Analysis and Design*, 3rd ed.
- Walker, J.G., "Satellite Constellations", JBIS, 1984.
