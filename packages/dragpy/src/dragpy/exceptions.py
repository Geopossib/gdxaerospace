"""Exceptions for dragpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidDragModelError(GDXAerospaceError):
    """Raised when an unsupported ``model=`` name is passed to a drag function."""

    def __init__(self, model: str, *, valid_models: tuple[str, ...]) -> None:
        message = (
            f"Unknown drag model {model!r}. Valid options are: "
            f"{', '.join(repr(m) for m in valid_models)}."
        )
        super().__init__(message)
        self.model = model
        self.valid_models = valid_models
