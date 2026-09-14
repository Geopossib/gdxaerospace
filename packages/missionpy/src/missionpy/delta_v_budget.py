"""Mission delta-v budget summation.

Reference
---------
- Wertz, J.R. & Larson, W.J. (eds.), *Space Mission Analysis and
  Design* (SMAD), 3rd ed., Ch. 17, for the standard practice of
  building a mission delta-v budget as a named, itemized sum of
  individual maneuver costs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from missionpy.exceptions import InvalidMissionInputError


@dataclass
class DeltaVBudget:
    """An itemized mission delta-v budget.

    Parameters
    ----------
    margin_fraction:
        Fractional margin applied to the summed delta-v (e.g. 0.05 for a
        5% margin), a standard mission-design practice to cover
        navigation and execution errors. Defaults to 0.0 (no margin).

    """

    margin_fraction: float = 0.0
    _items: dict[str, float] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if self.margin_fraction < 0:
            raise InvalidMissionInputError(
                f"margin_fraction must be non-negative, got {self.margin_fraction!r}"
            )

    def add(self, name: str, delta_v: float) -> None:
        """Add a named maneuver's delta-v, m/s, to the budget.

        Parameters
        ----------
        name:
            A label for this maneuver (e.g. ``"orbit insertion"``,
            ``"stationkeeping (10 yr)"``). Adding the same name twice
            overwrites the previous value rather than double-counting it.
        delta_v:
            Delta-v for this maneuver, m/s, >= 0.

        """
        if delta_v < 0:
            raise InvalidMissionInputError(f"delta_v must be non-negative, got {delta_v!r}")
        self._items[name] = delta_v

    def subtotal(self) -> float:
        """Sum of all itemized delta-v, before margin, m/s."""
        return sum(self._items.values())

    def total_with_margin(self) -> float:
        """Compute total delta-v including the configured margin, m/s.

        Example
        -------
        >>> budget = DeltaVBudget(margin_fraction=0.05)
        >>> budget.add("orbit insertion", 3000.0)
        >>> budget.add("stationkeeping", 500.0)
        >>> budget.total_with_margin()
        3675.0

        """
        return self.subtotal() * (1 + self.margin_fraction)

    def items(self) -> dict[str, float]:
        """Return a copy of the itemized maneuvers as a dict."""
        return dict(self._items)
