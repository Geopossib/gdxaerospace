# aerounits

Aerospace-aware unit handling for the GDX Aerospace ecosystem, built on
[Pint](https://pint.readthedocs.io/).

```python
from aerounits import Q_, ureg

v = Q_(250, "knot")
print(v.to("m/s"))

altitude = Q_(35_000, "ft").to("m")
```

`aerounits` does not reinvent unit conversion — it configures Pint's unit
registry with aerospace-standard aliases (`knot`, `ft`, `nmi`, `slug`,
`psi`, `degR`, etc.) and exposes a single shared registry (`ureg`) so that
quantities created in one GDX Aerospace package are compatible with every
other package.

All internal computation across GDX Aerospace packages uses SI units; use
`aerounits` at the API boundary to accept/return quantities in the caller's
preferred unit system.
