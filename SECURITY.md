# Security Policy

GDX Aerospace is a scientific/engineering computation library and does not
handle secrets, network services, or user authentication. Nonetheless, if
you find a security issue (e.g. in dependency handling, file parsing of
untrusted telemetry/config files, or CI configuration), please report it
privately via a GitHub security advisory on this repository rather than a
public issue.

## Engineering-safety note

This is separate from software security: no calculation in this library is
certified for flight-critical use. See the Disclaimer in the README.
