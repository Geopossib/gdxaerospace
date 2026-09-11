"""Detect whether OpenFOAM is installed and available on PATH.

Reference
---------
- OpenFOAM (openfoam.org / openfoam.com) is a large, separately
  installed CFD package. aerocfd automates *using* OpenFOAM -- case
  generation, execution, and post-processing -- but never assumes it is
  present, and never attempts to install it.

Assumptions
-----------
- "Available" is determined by checking whether a given solver/utility
  binary name resolves on the current ``PATH`` (via ``shutil.which``).
  This does not verify the binary actually runs correctly (e.g. a
  broken installation, missing shared libraries, or an unset
  ``WM_PROJECT_DIR`` environment variable could still cause a solver
  invocation to fail even though its binary is found on PATH).
"""

from __future__ import annotations

import shutil


def is_openfoam_available(binary: str = "simpleFoam") -> bool:
    """Check whether an OpenFOAM binary is available on the current PATH.

    Parameters
    ----------
    binary:
        Name of the OpenFOAM solver or utility to check for. Defaults
        to ``"simpleFoam"``, a commonly available steady-state
        incompressible solver, as a reasonable general availability check.

    Returns
    -------
    bool
        True if ``binary`` resolves on PATH.

    Example
    -------
    >>> is_openfoam_available("this-binary-definitely-does-not-exist-anywhere")
    False

    """
    return shutil.which(binary) is not None
