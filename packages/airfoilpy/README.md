# airfoilpy

NACA 4-digit and standard NACA 5-digit airfoil geometry generation
(camber line, thickness distribution, surface coordinates) for the
GDX Aerospace ecosystem.

```python
from airfoilpy import naca4_coordinates

coords = naca4_coordinates("2412", n_points=200)
```
