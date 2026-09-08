# electricprop

Ion and Hall-effect electric thruster performance: ideal electrostatic
exhaust velocity, thrust, specific impulse, and total efficiency, for the
GDX Aerospace ecosystem.

```python
from electricprop import HallThruster

thruster = HallThruster(voltage=300.0, current=5.0, mass_flow=5e-6)
print(thruster.thrust())
print(thruster.specific_impulse())
print(thruster.efficiency())
```
