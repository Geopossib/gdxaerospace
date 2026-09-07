"""aerounits — shared aerospace unit system for GDX Aerospace.

This module exposes a single, shared :class:`pint.UnitRegistry` (``ureg``)
and its quantity constructor (``Q_``) so that every package in the GDX
Aerospace ecosystem that creates unit-aware quantities is interoperable.

Internal computation across GDX Aerospace is always performed in SI units.
``aerounits`` is meant to sit at API boundaries, converting user-friendly
units (knots, feet, psi, ...) to and from SI.

Example:
-------
>>> from aerounits import Q_
>>> speed = Q_(250, "knot").to("m/s")
>>> round(speed.magnitude, 3)
128.611

"""

from __future__ import annotations

import pint

#: Shared unit registry for the whole GDX Aerospace ecosystem.
#: Importing this instead of creating a new UnitRegistry() elsewhere is
#: required for cross-package unit compatibility (Pint quantities from two
#: different registries cannot be combined).
ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)

# Aerospace-relevant aliases not always enabled by default in Pint.
ureg.define("nautical_mile = 1852 * meter = nmi")
ureg.define("knot = nautical_mile / hour = kt = kts")
ureg.define("slug = 14.5939029372 * kilogram")

#: Convenience alias for building quantities: ``Q_(250, "knot")``.
Q_ = ureg.Quantity

__all__ = ["Q_", "ureg"]
