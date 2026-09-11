"""Exceptions for aerocfd."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class OpenFOAMNotFoundError(GDXAerospaceError):
    """Raised when an OpenFOAM solver/utility is required but not found on PATH."""

    def __init__(self, binary: str) -> None:
        message = (
            f"OpenFOAM binary {binary!r} was not found on PATH. aerocfd automates "
            "OpenFOAM case setup and execution but does not install OpenFOAM itself. "
            "Install it from https://openfoam.org or https://www.openfoam.com "
            "(or via your Linux distribution's package manager, e.g. "
            "'sudo apt install openfoam' on Ubuntu), then ensure its environment "
            "script (e.g. 'source /opt/openfoam.../etc/bashrc') has been sourced "
            "so its binaries are on PATH."
        )
        super().__init__(message)
        self.binary = binary


class InvalidCaseError(GDXAerospaceError):
    """Raised when an OpenFOAM case directory or configuration is invalid."""
