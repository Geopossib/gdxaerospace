"""gdxaerospace — the unified meta-package for the GDX Aerospace ecosystem.

Installing this package pulls in all 46 packages built across the
project's ten development phases. See :mod:`gdxaerospace.manifest` for
what's included and where — this package intentionally does not
re-export sub-package symbols into one flat namespace (see the README
for why); import what you need directly from its own package.
"""

from __future__ import annotations

from gdxaerospace.manifest import PackageInfo, list_packages, package_info, phase_names

__all__ = [
    "PackageInfo",
    "list_packages",
    "package_info",
    "phase_names",
]

__version__ = "1.0.0"
