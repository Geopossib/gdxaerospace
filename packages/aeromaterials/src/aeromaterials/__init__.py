"""aeromaterials — a structured aerospace material property database for GDX Aerospace."""

from __future__ import annotations

from aeromaterials.database import Material, available_materials, get_material
from aeromaterials.exceptions import UnknownMaterialError

__all__ = [
    "Material",
    "UnknownMaterialError",
    "available_materials",
    "get_material",
]

__version__ = "0.1.0"
