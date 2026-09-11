"""High-level OpenFOAM case: configure, generate, run, and post-process.

Reference
---------
- See :mod:`aerocfd.case_files` for the individual dictionary-file
  writers this class orchestrates, and :mod:`aerocfd.detect` for how
  OpenFOAM availability is checked before attempting to run a solver.

Assumptions
-----------
- This class generates the case's dictionary files (``0/``,
  ``constant/``, ``system/``) but not a mesh -- see
  :mod:`aerocfd.case_files` for why. Place a mesh (``constant/polyMesh``)
  into the case directory before calling :meth:`OpenFOAMCase.run`.
- :meth:`OpenFOAMCase.postprocess` expects OpenFOAM's ``forceCoeffs``
  function object output in the conventional location
  (``postProcessing/forceCoeffs1/0/coefficient.dat``) with whitespace-
  separated columns; exact column layout varies slightly across
  OpenFOAM versions, so verify against your actual output file if this
  does not parse cleanly.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from aerocfd.case_files import (
    generate_control_dict,
    generate_pressure_field,
    generate_transport_properties,
    generate_turbulence_properties,
    generate_velocity_field,
)
from aerocfd.detect import is_openfoam_available
from aerocfd.exceptions import InvalidCaseError, OpenFOAMNotFoundError
from aerocfd.postprocess import ForceCoefficients, parse_force_coefficients


@dataclass
class OpenFOAMCase:
    """A simple external-aerodynamics OpenFOAM case (see module docstring for scope).

    Parameters
    ----------
    name:
        Case name, used as the case directory name under ``base_dir``.
    base_dir:
        Parent directory for the case directory. Defaults to the
        current working directory.

    """

    name: str
    base_dir: Path = field(default_factory=Path.cwd)
    _velocity: float = field(default=50.0, init=False)
    _angle_of_attack_deg: float = field(default=0.0, init=False)
    _turbulence_model: str = field(default="kOmegaSST", init=False)
    _application: str = field(default="simpleFoam", init=False)

    @property
    def case_dir(self) -> Path:
        """The full path to this case's directory."""
        return Path(self.base_dir) / self.name

    def set_velocity(self, velocity: float) -> None:
        """Set the freestream velocity magnitude, m/s."""
        if velocity <= 0:
            raise InvalidCaseError(f"velocity must be positive, got {velocity!r}")
        self._velocity = velocity

    def set_angle_of_attack(self, angle_deg: float) -> None:
        """Set the angle of attack, degrees."""
        self._angle_of_attack_deg = angle_deg

    def set_turbulence_model(self, model: str) -> None:
        """Set the RANS turbulence model name (or ``"laminar"``)."""
        self._turbulence_model = model

    def generate(self) -> None:
        """Write the case's dictionary files to :attr:`case_dir`.

        Does not generate a mesh -- see the module docstring.
        """
        generate_control_dict(self.case_dir, application=self._application)
        generate_transport_properties(self.case_dir)
        generate_turbulence_properties(self.case_dir, turbulence_model=self._turbulence_model)
        generate_velocity_field(
            self.case_dir,
            velocity=self._velocity,
            angle_of_attack_deg=self._angle_of_attack_deg,
        )
        generate_pressure_field(self.case_dir)

    def run(self) -> subprocess.CompletedProcess[str]:
        """Run the configured solver on this case.

        Raises
        ------
        OpenFOAMNotFoundError
            If the configured solver is not found on PATH.
        InvalidCaseError
            If :meth:`generate` has not been called yet (no case files
            present).

        """
        if not self.case_dir.exists():
            raise InvalidCaseError(
                f"case directory {self.case_dir} does not exist; call generate() first"
            )
        if not is_openfoam_available(self._application):
            raise OpenFOAMNotFoundError(self._application)
        return subprocess.run(
            [self._application, "-case", str(self.case_dir)],
            capture_output=True,
            text=True,
            check=True,
        )

    def postprocess(self) -> ForceCoefficients:
        """Parse this case's force-coefficient output.

        See the module docstring for the expected file location and format.
        """
        return parse_force_coefficients(self.case_dir)
