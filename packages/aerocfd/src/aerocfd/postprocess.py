"""Parse OpenFOAM ``forceCoeffs`` function-object output.

Reference
---------
- OpenFOAM's ``forceCoeffs`` function object writes a whitespace-
  separated text file (conventionally
  ``postProcessing/forceCoeffs1/0/coefficient.dat``) with a time column
  followed by force/moment coefficient columns. This module parses the
  common column layout ``Time Cd Cl CmPitch``; exact column sets vary
  by OpenFOAM version and configuration (some versions add Cd(f), Cd(r)
  front/rear breakdown columns, for example) -- adjust the column
  indices here if your output differs.

Assumptions
-----------
- Lines starting with ``#`` are treated as comments/headers and skipped,
  per the file format's own convention.
- Only the last (converged, for a steady-state run) data row is
  returned by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aerocfd.exceptions import InvalidCaseError


@dataclass(frozen=True)
class ForceCoefficients:
    """Aerodynamic force/moment coefficients from an OpenFOAM ``forceCoeffs`` run."""

    time: float
    cd: float
    cl: float
    cm_pitch: float


def _find_coefficient_file(case_dir: Path) -> Path:
    post_dir = Path(case_dir) / "postProcessing"
    if not post_dir.exists():
        raise InvalidCaseError(
            f"no postProcessing directory found under {case_dir}; has the case been run "
            "with a forceCoeffs function object enabled?"
        )
    candidates = sorted(post_dir.glob("forceCoeffs*/*/coefficient.dat"))
    if not candidates:
        candidates = sorted(post_dir.glob("forceCoeffs*/*/*.dat"))
    if not candidates:
        raise InvalidCaseError(
            f"no forceCoeffs output file found under {post_dir}; expected a path like "
            "'postProcessing/forceCoeffs1/0/coefficient.dat'"
        )
    return candidates[-1]


def parse_force_coefficients(case_dir: Path) -> ForceCoefficients:
    r"""Parse the final (converged) row of a case's ``forceCoeffs`` output.

    Parameters
    ----------
    case_dir:
        OpenFOAM case directory containing a ``postProcessing/forceCoeffs*``
        subdirectory.

    Returns
    -------
    ForceCoefficients

    Raises
    ------
    InvalidCaseError
        If no force-coefficient output file can be found, or it
        contains no data rows.

    Example
    -------
    >>> import tempfile
    >>> from pathlib import Path
    >>> case_dir = Path(tempfile.mkdtemp())
    >>> out_dir = case_dir / "postProcessing" / "forceCoeffs1" / "0"
    >>> out_dir.mkdir(parents=True)
    >>> _ = (out_dir / "coefficient.dat").write_text(
    ...     "# Time Cd Cl CmPitch\n100 0.0234 0.512 -0.021\n200 0.0231 0.515 -0.020\n"
    ... )
    >>> result = parse_force_coefficients(case_dir)
    >>> result.cd, result.cl
    (0.0231, 0.515)

    """
    coefficient_file = _find_coefficient_file(case_dir)
    data_lines = [
        line
        for line in coefficient_file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not data_lines:
        raise InvalidCaseError(f"{coefficient_file} contains no data rows")

    last_row = data_lines[-1].split()
    try:
        time, cd, cl, cm_pitch = (float(x) for x in last_row[:4])
    except (ValueError, IndexError) as exc:
        raise InvalidCaseError(
            f"could not parse expected 'Time Cd Cl CmPitch' columns from row: {last_row!r}"
        ) from exc

    return ForceCoefficients(time=time, cd=cd, cl=cl, cm_pitch=cm_pitch)
