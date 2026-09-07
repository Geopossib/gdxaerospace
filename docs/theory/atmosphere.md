# International Standard Atmosphere

`aerocalc.Atmosphere` implements the 1976 U.S. Standard Atmosphere, which is
numerically identical to ICAO Doc 7488 over the altitude range GDX Aerospace
supports (0–86,000 m geopotential altitude).

## Governing equations

Within each of the seven layers, temperature varies linearly with
geopotential altitude $h$:

$$
T(h) = T_b + L_b (h - h_b)
$$

where $T_b$, $L_b$, $h_b$ are the base temperature, lapse rate, and base
altitude of the layer containing $h$.

For layers with nonzero lapse rate ($L_b \neq 0$), pressure follows the
barometric formula:

$$
P(h) = P_b \left( \frac{T(h)}{T_b} \right)^{-g_0 / (L_b R)}
$$

For isothermal layers ($L_b = 0$):

$$
P(h) = P_b \exp\left(-\frac{g_0 (h - h_b)}{R\, T_b}\right)
$$

Density follows from the ideal gas law:

$$
\rho(h) = \frac{P(h)}{R\, T(h)}
$$

and the speed of sound assumes a calorically perfect gas:

$$
a(h) = \sqrt{\gamma R\, T(h)}
$$

with $g_0 = 9.80665\ \text{m/s}^2$, $R = 287.05287\ \text{J/(kg·K)}$, and
$\gamma = 1.4$ for air.

## Assumptions and limitations

- Dry air only — no humidity correction.
- Geopotential altitude is used directly as geometric altitude (the
  difference is under 0.1% below 86 km and is neglected, per the standard's
  own convention).
- Calorically perfect gas: $\gamma$ and $R$ are treated as constant, which
  becomes less accurate above roughly 50 km where real-gas effects grow.
- The model is undefined outside 0–86,000 m; `Atmosphere` raises
  `InvalidAltitudeError` outside that range rather than extrapolating.

## References

- U.S. Standard Atmosphere, 1976, NOAA-S/T 76-1562.
- ICAO Doc 7488/3, *Manual of the ICAO Standard Atmosphere*.
- Anderson, J.D., *Introduction to Flight*, 8th ed., Chapter 3.
