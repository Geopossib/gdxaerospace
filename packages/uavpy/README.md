# uavpy

UAV sizing and performance: multirotor hover power (actuator-disk
momentum theory) and flight-time estimation, plus fixed-wing wing
loading, thrust-to-weight ratio, and stall speed, for the GDX Aerospace
ecosystem.

```python
from uavpy import Multirotor

uav = Multirotor(mass=2.5, num_motors=4, rotor_radius=0.127, battery_voltage=22.2, battery_capacity_mah=5000)
print(uav.thrust_to_weight())
print(uav.flight_time_minutes())
```
