"""Geometric properties (area, centroid, moment of inertia) of common cross-sections.

Reference
---------
- Hibbeler, R.C., *Mechanics of Materials*, 10th ed., Appendix A
  (standard cross-section area-moment-of-inertia formulas).
- Megson, T.H.G., *Aircraft Structures for Engineering Students*, 6th
  ed., Ch. 15-16, for the composite-section (parallel-axis) approach
  used here for built-up sections like I-beams.

Convention
----------
- ``ixx``/``iyy`` are second moments of area about centroidal axes
  (bending stiffness about the x and y axes respectively); ``j`` is the
  polar second moment of area (torsional stiffness), meaningful here
  only for the circular sections where simple torsion theory applies
  directly.
- Composite sections (e.g. I-beams) are built from simple sub-shapes
  combined via the parallel-axis theorem, rather than using a single
  memorized combined formula -- this is both more transparent and
  reusable for other built-up shapes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from aerostruct.exceptions import InvalidSectionError


@dataclass(frozen=True)
class SectionProperties:
    """Geometric properties of a cross-section, about its own centroid."""

    area: float
    ixx: float
    iyy: float
    j: float | None = None


def parallel_axis_theorem(centroidal_i: float, area: float, distance: float) -> float:
    """Transfer a moment of inertia to a parallel axis: ``I = I_c + A*d^2``.

    Parameters
    ----------
    centroidal_i:
        Moment of inertia about the shape's own centroidal axis, m^4, >= 0.
    area:
        Shape's area, m^2, > 0.
    distance:
        Perpendicular distance between the centroidal axis and the new
        (parallel) axis, m.

    Returns
    -------
    float
        Moment of inertia about the new axis, m^4.

    Example
    -------
    >>> round(parallel_axis_theorem(centroidal_i=1e-6, area=0.001, distance=0.05), 8)
    3.5e-06

    """
    if centroidal_i < 0:
        raise InvalidSectionError(f"centroidal_i must be non-negative, got {centroidal_i!r}")
    if area <= 0:
        raise InvalidSectionError(f"area must be positive, got {area!r}")
    return centroidal_i + area * distance**2


def rectangle_properties(width: float, height: float) -> SectionProperties:
    """Area and centroidal second moments of area for a solid rectangle.

    ``Ixx = width * height^3 / 12`` (bending about the horizontal
    centroidal axis), ``Iyy = height * width^3 / 12``.

    Parameters
    ----------
    width:
        Rectangle width (horizontal dimension), m, > 0.
    height:
        Rectangle height (vertical dimension), m, > 0.

    Example
    -------
    >>> props = rectangle_properties(width=0.02, height=0.1)
    >>> props.area
    0.002
    >>> round(props.ixx, 9)
    1.667e-06

    """
    if width <= 0 or height <= 0:
        raise InvalidSectionError(
            f"width and height must be positive, got {width!r}, {height!r}"
        )
    area = width * height
    ixx = width * height**3 / 12
    iyy = height * width**3 / 12
    return SectionProperties(area=area, ixx=ixx, iyy=iyy)


def circle_properties(radius: float) -> SectionProperties:
    """Area and second moments of area for a solid circular section.

    ``I = pi*r^4/4`` (equal about any centroidal axis, by symmetry),
    ``J = pi*r^4/2`` (polar moment, for torsion of a circular shaft).

    Parameters
    ----------
    radius:
        Circle radius, m, > 0.

    Example
    -------
    >>> props = circle_properties(radius=0.05)
    >>> round(props.area, 6)
    0.007854
    >>> round(props.j, 9)
    9.817e-06

    """
    if radius <= 0:
        raise InvalidSectionError(f"radius must be positive, got {radius!r}")
    area = math.pi * radius**2
    i = math.pi * radius**4 / 4
    j = math.pi * radius**4 / 2
    return SectionProperties(area=area, ixx=i, iyy=i, j=j)


def hollow_circle_properties(outer_radius: float, inner_radius: float) -> SectionProperties:
    """Area and second moments of area for a hollow circular (tube) section.

    Parameters
    ----------
    outer_radius:
        Outer radius, m, > ``inner_radius``.
    inner_radius:
        Inner radius, m, >= 0.

    Example
    -------
    >>> props = hollow_circle_properties(outer_radius=0.05, inner_radius=0.04)
    >>> round(props.area, 6)
    0.002827

    """
    if inner_radius < 0:
        raise InvalidSectionError(f"inner_radius must be non-negative, got {inner_radius!r}")
    if outer_radius <= inner_radius:
        raise InvalidSectionError(
            f"outer_radius ({outer_radius!r}) must exceed inner_radius ({inner_radius!r})"
        )
    area = math.pi * (outer_radius**2 - inner_radius**2)
    i = math.pi * (outer_radius**4 - inner_radius**4) / 4
    j = math.pi * (outer_radius**4 - inner_radius**4) / 2
    return SectionProperties(area=area, ixx=i, iyy=i, j=j)


def i_beam_properties(
    flange_width: float, flange_thickness: float, web_height: float, web_thickness: float
) -> SectionProperties:
    """Compute area and Ixx for a symmetric I-beam (wide-flange) section.

    Built from three rectangles (top flange, web, bottom flange)
    combined via the parallel-axis theorem, rather than a single
    memorized combined-section formula.

    Parameters
    ----------
    flange_width:
        Width of each (identical) flange, m, > 0.
    flange_thickness:
        Thickness of each flange, m, > 0.
    web_height:
        Height of the web between the flanges (i.e. the clear web
        height, not including the flanges), m, > 0.
    web_thickness:
        Web thickness, m, > 0.

    Returns
    -------
    SectionProperties
        ``iyy`` is the sum of the three rectangles' own ``Iyy`` (no
        parallel-axis shift needed, since all three are centered on the
        same vertical axis).

    Example
    -------
    >>> props = i_beam_properties(
    ...     flange_width=0.08, flange_thickness=0.01, web_height=0.1, web_thickness=0.006
    ... )
    >>> round(props.area, 6)
    0.0022

    """
    if flange_width <= 0 or flange_thickness <= 0 or web_height <= 0 or web_thickness <= 0:
        raise InvalidSectionError("all I-beam dimensions must be positive")

    flange = rectangle_properties(flange_width, flange_thickness)
    web = rectangle_properties(web_thickness, web_height)

    flange_centroid_distance = web_height / 2 + flange_thickness / 2
    flange_ixx_shifted = parallel_axis_theorem(flange.ixx, flange.area, flange_centroid_distance)

    total_area = 2 * flange.area + web.area
    total_ixx = 2 * flange_ixx_shifted + web.ixx
    total_iyy = 2 * flange.iyy + web.iyy

    return SectionProperties(area=total_area, ixx=total_ixx, iyy=total_iyy)
