# Satellite telemetry

`sattelemetry` is a full decode/validate/calibrate/archive pipeline for
CCSDS-style spacecraft telemetry, built to have a clean seam for future
RTL-SDR, GNU Radio, or TCP/UDP ground-station integrations to plug into.

## Packet structure (CCSDS Space Packet Protocol)

Every packet starts with a fixed 6-byte primary header (CCSDS 133.0-B-2):
version, packet type (telemetry/telecommand), a secondary-header flag,
an 11-bit Application Process ID (APID) identifying *what kind* of
packet this is, a sequence count, and a data-field length. `sattelemetry`
packs and unpacks this header exactly per the standard's bit layout —
verified by round-tripping every field through non-trivial values.

## Integrity: CRC-16/CCITT-FALSE

`sattelemetry` uses the CRC-16/CCITT-FALSE variant (polynomial `0x1021`,
init `0xFFFF`), one of the most common checksums in embedded and space
telemetry protocols. Its correctness is anchored to the standard
published check value — the CRC of the ASCII string `"123456789"` is
`0x29B1` — which the test suite verifies directly rather than trusting
the implementation on faith.

**A real bug this caught during development:** the first version
computed the CRC over the data field when building a packet but verified
it over header+data when decoding — a scope mismatch that made every
valid packet fail verification. The fix was picking one explicit
convention (CRC covers the data field only, matching the ECSS/PUS
standard) and documenting it, since different real missions genuinely
do this differently.

## Calibration

Each telemetry point ("channel") is a raw field at a known byte offset
with a polynomial calibration curve, `value = c0 + c1*raw + c2*raw^2 +
...` — the standard way engineering values (volts, degrees, etc.) get
derived from raw ADC counts or sensor readings.

## Anomaly detection: two layers

- **Red/yellow limits** (`sattelemetry.limits`): fixed thresholds
  checked against every new value as it arrives — the first line of
  defense in any spacecraft operations center.
- **Statistical outlier detection** (`sattelemetry.archive`): a z-score
  screen over a channel's history, useful for catching drift or noise
  that doesn't cross a fixed limit. Its documented limitation is real
  and worth knowing: a single extreme outlier in a short series can
  inflate its own standard deviation enough to mask itself — this
  detector works best over a reasonably long, mostly-nominal history.

## References

- CCSDS 133.0-B-2, *Space Packet Protocol*, Blue Book.
- CRC RevEng catalogue (reveng.sourceforge.io/crc-catalogue) for the
  CRC-16/CCITT-FALSE check value.
- ECSS-E-70-41A, *Ground Systems and Operations — Telemetry and
  Telecommand Packet Utilization*, for the PUS packet conventions this
  module's defaults loosely follow.
