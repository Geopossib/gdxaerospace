"""A structured database of common aerospace structural material properties.

Reference
---------
- Metallic properties: MMPDS-01 (*Metallic Materials Properties
  Development and Standardization*), the successor to MIL-HDBK-5 and
  the standard aerospace design-allowables reference, cross-checked
  against ASM Aerospace Specification Metals
  (asm.matweb.com) for the commonly published room-temperature values
  used here.
- T300/5208 graphite-epoxy lamina properties: Jones, R.M., *Mechanics
  of Composite Materials*, 2nd ed., a widely reproduced textbook
  example material system used throughout the composites-mechanics
  literature.
- ASTM A36 structural steel: per the ASTM A36 specification's own
  published minimum property values.

**These are reference/typical room-temperature values for common
material conditions, not a substitute for current, certified
MMPDS/specification design allowables.** Strength values in particular
are sensitive to exact heat treatment, product form, and thickness in
ways this database does not capture -- always verify against the
governing specification before using these numbers for actual design.

Convention
----------
- All properties are SI units: density (kg/m^3), Young's modulus and
  shear modulus (Pa), Poisson's ratio (dimensionless), yield and
  ultimate tensile strength (Pa).
- ``yield_strength``/``ultimate_strength`` are None for materials (or
  conditions) where strength is too heat-treatment-dependent to quote a
  single representative value responsibly; see each entry's ``source``
  string for what is and isn't covered.
"""

from __future__ import annotations

from dataclasses import dataclass

from aeromaterials.exceptions import UnknownMaterialError


@dataclass(frozen=True)
class Material:
    """A material's reference structural properties, with its data source.

    Parameters
    ----------
    name:
        Material designation (e.g. ``"Al7075-T6"``).
    density:
        Density, kg/m^3.
    youngs_modulus:
        Young's modulus (elastic modulus), Pa.
    shear_modulus:
        Shear modulus, Pa.
    poisson_ratio:
        Poisson's ratio, dimensionless.
    yield_strength:
        Tensile yield strength, Pa, or None if not responsibly
        quotable as a single value (see ``source``).
    ultimate_strength:
        Ultimate tensile strength, Pa, or None (see ``yield_strength``).
    source:
        The reference this entry's values are drawn from, and any
        caveats about condition-dependence.

    """

    name: str
    density: float
    youngs_modulus: float
    shear_modulus: float
    poisson_ratio: float
    yield_strength: float | None
    ultimate_strength: float | None
    source: str


_MATERIALS: dict[str, Material] = {
    "Al7075-T6": Material(
        name="Al7075-T6",
        density=2810.0,
        youngs_modulus=71.7e9,
        shear_modulus=26.9e9,
        poisson_ratio=0.33,
        yield_strength=503e6,
        ultimate_strength=572e6,
        source="MMPDS-01 / ASM Aerospace Specification Metals, room temperature, wrought plate.",
    ),
    "Al2024-T3": Material(
        name="Al2024-T3",
        density=2780.0,
        youngs_modulus=73.1e9,
        shear_modulus=28.0e9,
        poisson_ratio=0.33,
        yield_strength=345e6,
        ultimate_strength=483e6,
        source="MMPDS-01 / ASM Aerospace Specification Metals, room temperature, wrought sheet.",
    ),
    "Ti-6Al-4V": Material(
        name="Ti-6Al-4V",
        density=4430.0,
        youngs_modulus=113.8e9,
        shear_modulus=44.0e9,
        poisson_ratio=0.342,
        yield_strength=880e6,
        ultimate_strength=950e6,
        source="MMPDS-01 / ASM Aerospace Specification Metals, room temperature, annealed.",
    ),
    "AISI4340-normalized": Material(
        name="AISI4340-normalized",
        density=7850.0,
        youngs_modulus=200e9,
        shear_modulus=80e9,
        poisson_ratio=0.29,
        yield_strength=710e6,
        ultimate_strength=1080e6,
        source=(
            "ASM Metals Handbook, normalized condition. 4340 strength is strongly "
            "heat-treatment-dependent (quenched-and-tempered conditions reach much "
            "higher strength); confirm the actual heat treatment before using this value."
        ),
    ),
    "ASTM-A36-steel": Material(
        name="ASTM-A36-steel",
        density=7850.0,
        youngs_modulus=200e9,
        shear_modulus=79.3e9,
        poisson_ratio=0.26,
        yield_strength=250e6,
        ultimate_strength=400e6,
        source="ASTM A36 specification, published minimum properties.",
    ),
}


def get_material(name: str) -> Material:
    """Look up a material's reference properties by name.

    Parameters
    ----------
    name:
        Material designation. See :data:`available_materials` for the
        supported names.

    Returns
    -------
    Material

    Raises
    ------
    UnknownMaterialError
        If ``name`` is not in the database.

    Example
    -------
    >>> material = get_material("Al7075-T6")
    >>> material.density
    2810.0
    >>> material.yield_strength
    503000000.0

    """
    try:
        return _MATERIALS[name]
    except KeyError:
        valid = ", ".join(sorted(_MATERIALS))
        raise UnknownMaterialError(
            f"unknown material {name!r}; available materials: {valid}"
        ) from None


def available_materials() -> tuple[str, ...]:
    """Return the names of all materials in the database, sorted."""
    return tuple(sorted(_MATERIALS))
