"""Generate a minimal OpenFOAM case directory (dictionary files only).

Reference
---------
- OpenFOAM User Guide, Ch. 4-5, for the standard case directory
  structure (``0/``, ``constant/``, ``system/``) and the OpenFOAM
  dictionary ("FoamFile") text format used by every case file.

Assumptions
-----------
- Generates a minimal, syntactically valid case skeleton for a simple
  external-aerodynamics steady RANS run (``simpleFoam`` with
  ``kOmegaSST`` by default) around a single patch named ``"body"`` --
  the mesh itself (``blockMeshDict``/``snappyHexMeshDict`` or an
  imported mesh) is NOT generated here, since mesh generation is
  geometry-specific; supply your own mesh into the case directory
  before running.
- Boundary patch names in the generated ``0/U`` and ``0/p`` files
  (``"inlet"``, ``"outlet"``, ``"body"``, ``"farfield"``) are a common
  convention, not a universal standard -- rename them to match your
  actual mesh's patch names before running.
"""

from __future__ import annotations

import math
from pathlib import Path

_FOAM_HEADER_TEMPLATE = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       {foam_class};
    object      {object_name};
}}
"""


def _write_dict_file(path: Path, foam_class: str, object_name: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = _FOAM_HEADER_TEMPLATE.format(foam_class=foam_class, object_name=object_name)
    path.write_text(header + "\n" + body)


def generate_control_dict(
    case_dir: Path,
    *,
    application: str = "simpleFoam",
    end_time: int = 1000,
    write_interval: int = 100,
) -> None:
    """Write ``system/controlDict``.

    Parameters
    ----------
    case_dir:
        Case root directory.
    application:
        OpenFOAM solver to run (e.g. ``"simpleFoam"``).
    end_time:
        Final iteration/time-step number for a steady-state run.
    write_interval:
        Write results every this many iterations.

    """
    body = f"""
application     {application};
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};
deltaT          1;
writeControl    timeStep;
writeInterval   {write_interval};
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
"""
    _write_dict_file(Path(case_dir) / "system" / "controlDict", "dictionary", "controlDict", body)


def generate_transport_properties(case_dir: Path, *, kinematic_viscosity: float = 1.5e-5) -> None:
    """Write ``constant/transportProperties``.

    Parameters
    ----------
    case_dir:
        Case root directory.
    kinematic_viscosity:
        Kinematic viscosity ``nu``, m^2/s. Defaults to air at
        approximately room temperature (~1.5e-5 m^2/s).

    """
    body = (
        "\ntransportModel  Newtonian;\n"
        f"nu              nu [0 2 -1 0 0 0 0] {kinematic_viscosity};\n"
    )
    _write_dict_file(
        Path(case_dir) / "constant" / "transportProperties",
        "dictionary",
        "transportProperties",
        body,
    )


def generate_turbulence_properties(case_dir: Path, *, turbulence_model: str = "kOmegaSST") -> None:
    """Write ``constant/turbulenceProperties``.

    Parameters
    ----------
    case_dir:
        Case root directory.
    turbulence_model:
        RANS turbulence model name (e.g. ``"kOmegaSST"``, ``"kEpsilon"``).
        Pass ``"laminar"`` for a laminar (no turbulence model) case.

    """
    if turbulence_model.lower() == "laminar":
        body = "\nsimulationType  laminar;\n"
    else:
        body = (
            "\nsimulationType  RAS;\n\nRAS\n{\n"
            f"    RASModel        {turbulence_model};\n"
            "    turbulence      on;\n"
            "    printCoeffs     on;\n}\n"
        )
    _write_dict_file(
        Path(case_dir) / "constant" / "turbulenceProperties",
        "dictionary",
        "turbulenceProperties",
        body,
    )


def generate_velocity_field(
    case_dir: Path, *, velocity: float = 50.0, angle_of_attack_deg: float = 0.0
) -> None:
    """Write the initial/boundary velocity field, ``0/U``.

    Parameters
    ----------
    case_dir:
        Case root directory.
    velocity:
        Freestream speed, m/s.
    angle_of_attack_deg:
        Angle of attack, degrees, used to resolve the freestream
        velocity vector's x/y components (2D case convention: z is spanwise).

    """
    aoa = math.radians(angle_of_attack_deg)
    vx, vy = velocity * math.cos(aoa), velocity * math.sin(aoa)
    body = f"""
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform ({vx:.6f} {vy:.6f} 0);

boundaryField
{{
    inlet
    {{
        type            freestreamVelocity;
        freestreamValue uniform ({vx:.6f} {vy:.6f} 0);
    }}
    outlet
    {{
        type            inletOutlet;
        inletValue      uniform (0 0 0);
        value           uniform ({vx:.6f} {vy:.6f} 0);
    }}
    body
    {{
        type            noSlip;
    }}
    farfield
    {{
        type            freestreamVelocity;
        freestreamValue uniform ({vx:.6f} {vy:.6f} 0);
    }}
}}
"""
    _write_dict_file(Path(case_dir) / "0" / "U", "volVectorField", "U", body)


def generate_pressure_field(case_dir: Path) -> None:
    """Write the initial/boundary pressure field, ``0/p`` (gauge, kinematic units)."""
    body = """
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            freestreamPressure;
        freestreamValue uniform 0;
    }
    outlet
    {
        type            freestreamPressure;
        freestreamValue uniform 0;
    }
    body
    {
        type            zeroGradient;
    }
    farfield
    {
        type            freestreamPressure;
        freestreamValue uniform 0;
    }
}
"""
    _write_dict_file(Path(case_dir) / "0" / "p", "volScalarField", "p", body)
