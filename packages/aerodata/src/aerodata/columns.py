"""Standard flight-test/telemetry variable name conventions.

Reference
---------
- These are conventional column-name labels commonly used across flight
  test data reduction and telemetry systems (e.g. as seen in typical
  flight test instrumentation lists and FDR/QAR parameter naming). They
  are provided here purely as a documented, shared vocabulary --
  aerodata's functions operate on whatever pandas Series/DataFrame you
  pass them and do not require using these exact names.
"""

from __future__ import annotations

#: Standard flight-test/telemetry variable name conventions, by physical quantity.
STANDARD_COLUMNS: dict[str, str] = {
    "altitude": "ALTITUDE",
    "indicated_airspeed": "IAS",
    "true_airspeed": "TAS",
    "calibrated_airspeed": "CAS",
    "mach": "MACH",
    "angle_of_attack": "AOA",
    "temperature": "TEMPERATURE",
    "pressure": "PRESSURE",
    "engine_rpm": "RPM",
    "thrust": "THRUST",
    "fuel_flow": "FUEL_FLOW",
    "acceleration": "ACCELERATION",
    "latitude": "GPS_LAT",
    "longitude": "GPS_LON",
    "imu_angular_rate": "IMU_RATE",
}
