# sattelemetry

CCSDS-style satellite telemetry: Space Packet primary header pack/unpack,
CRC-16/CCITT-FALSE checksums, engineering-unit calibration, a
bit-field-driven packet decoder, red/yellow limit checking, and a
queryable in-memory telemetry archive, for the GDX Aerospace ecosystem.

Designed so that future RTL-SDR, GNU Radio, or TCP/UDP ground-station
integrations have a clean decode/validate/archive layer to plug into.
