"""Component-buildup parasitic (profile) drag estimation.

Reference
---------
- Raymer, D.P., *Aircraft Design: A Conceptual Approach*, 6th ed., Ch. 12
  ("component buildup method"): ``CD0 = sum(Cf_c * FF_c * Q_c * Swet_c) / Sref``.
- Hoerner, S.F., *Fluid-Dynamic Drag*, for the classic Hoerner form-factor
  correlation used here for streamlined bodies (struts, fuselages).

Assumptions
-----------
- Subsonic, fully turbulent flow over each component (a conservative,
  common simplifying assumption at the conceptual-design stage — see
  ``dragpy.skin_friction`` for laminar/turbulent choice at the component
  level).
- Form factor (FF) accounts for pressure drag due to component thickness;
  interference factor (Q) accounts for the mutual interference between
  adjacent components (e.g. wing-fuselage junction). Both default to 1.0
  (a thin flat plate with no interference) if not supplied, so the
  component-buildup collapses to pure skin-friction drag unless the caller
  supplies more realistic values for their geometry.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DragComponent:
    """One component in a parasitic-drag buildup.

    Parameters
    ----------
    name:
        Component label (e.g. ``"wing"``, ``"fuselage"``, ``"tail"``).
    skin_friction_coefficient:
        Average flat-plate skin-friction coefficient for this component
        (see :mod:`dragpy.skin_friction`).
    wetted_area:
        Wetted (total exposed surface) area of the component, m^2.
    form_factor:
        Form factor accounting for pressure drag from thickness/shape.
        Defaults to 1.0 (no correction).
    interference_factor:
        Interference factor accounting for drag increase from adjacent
        components. Defaults to 1.0 (no correction).

    """

    name: str
    skin_friction_coefficient: float
    wetted_area: float
    form_factor: float = 1.0
    interference_factor: float = 1.0

    def drag_area(self) -> float:
        """Component's contribution to ``sum(Cf * FF * Q * Swet)``, m^2."""
        return (
            self.skin_friction_coefficient
            * self.form_factor
            * self.interference_factor
            * self.wetted_area
        )


@dataclass
class ParasiteDragBuildup:
    """Aggregate parasitic drag coefficient from a set of components.

    Parameters
    ----------
    reference_area:
        Reference area (typically wing planform area), m^2, > 0.
    components:
        List of :class:`DragComponent` contributions.

    """

    reference_area: float
    components: list[DragComponent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.reference_area <= 0:
            raise ValueError(f"reference_area must be positive, got {self.reference_area!r}")

    def add(self, component: DragComponent) -> None:
        """Add a component to the buildup."""
        self.components.append(component)

    def cd0(self) -> float:
        """Total parasitic (zero-lift) drag coefficient ``CD0``.

        Example:
        -------
        >>> buildup = ParasiteDragBuildup(reference_area=16.2)
        >>> buildup.add(DragComponent("wing", 0.003, wetted_area=30.0, form_factor=1.2))
        >>> buildup.add(DragComponent("fuselage", 0.0028, wetted_area=25.0, form_factor=1.1))
        >>> round(buildup.cd0(), 5)
        0.01142

        """
        if not self.components:
            return 0.0
        total_drag_area = sum(c.drag_area() for c in self.components)
        return total_drag_area / self.reference_area
