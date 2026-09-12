"""Validate OpenFOAM detection, case generation, and post-processing."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from aerocfd.case import OpenFOAMCase
from aerocfd.case_files import (
    generate_control_dict,
    generate_pressure_field,
    generate_transport_properties,
    generate_turbulence_properties,
    generate_velocity_field,
)
from aerocfd.detect import is_openfoam_available
from aerocfd.exceptions import InvalidCaseError, OpenFOAMNotFoundError
from aerocfd.postprocess import parse_force_coefficients


def test_is_openfoam_available_false_for_nonexistent_binary() -> None:
    assert is_openfoam_available("this-binary-definitely-does-not-exist-anywhere") is False


def test_is_openfoam_available_true_for_a_real_common_binary() -> None:
    """Sanity check the detection mechanism itself works for a binary known to
    exist in this environment, even though it isn't an OpenFOAM binary."""
    assert is_openfoam_available("python3") is True


def test_generate_control_dict_writes_expected_file(tmp_path: Path) -> None:
    generate_control_dict(tmp_path, application="simpleFoam", end_time=500)
    content = (tmp_path / "system" / "controlDict").read_text()
    assert "application     simpleFoam;" in content
    assert "endTime         500;" in content
    assert "FoamFile" in content


def test_generate_transport_properties_includes_viscosity(tmp_path: Path) -> None:
    generate_transport_properties(tmp_path, kinematic_viscosity=2e-5)
    content = (tmp_path / "constant" / "transportProperties").read_text()
    assert "2e-05" in content or "2e-5" in content or "0.00002" in content


def test_generate_turbulence_properties_ras_model(tmp_path: Path) -> None:
    generate_turbulence_properties(tmp_path, turbulence_model="kEpsilon")
    content = (tmp_path / "constant" / "turbulenceProperties").read_text()
    assert "simulationType  RAS;" in content
    assert "kEpsilon" in content


def test_generate_turbulence_properties_laminar(tmp_path: Path) -> None:
    generate_turbulence_properties(tmp_path, turbulence_model="laminar")
    content = (tmp_path / "constant" / "turbulenceProperties").read_text()
    assert "simulationType  laminar;" in content


def test_generate_velocity_field_resolves_angle_of_attack(tmp_path: Path) -> None:
    generate_velocity_field(tmp_path, velocity=100.0, angle_of_attack_deg=0.0)
    content = (tmp_path / "0" / "U").read_text()
    assert "uniform (100.000000 0.000000 0)" in content


def test_generate_velocity_field_nonzero_aoa_matches_trig(tmp_path: Path) -> None:
    velocity, aoa_deg = 50.0, 10.0
    generate_velocity_field(tmp_path, velocity=velocity, angle_of_attack_deg=aoa_deg)
    content = (tmp_path / "0" / "U").read_text()
    expected_vx = velocity * math.cos(math.radians(aoa_deg))
    expected_vy = velocity * math.sin(math.radians(aoa_deg))
    assert f"{expected_vx:.6f}" in content
    assert f"{expected_vy:.6f}" in content


def test_generate_pressure_field_writes_expected_file(tmp_path: Path) -> None:
    generate_pressure_field(tmp_path)
    content = (tmp_path / "0" / "p").read_text()
    assert "volScalarField" in content
    assert "internalField   uniform 0;" in content


def test_openfoam_case_generate_creates_all_expected_files(tmp_path: Path) -> None:
    case = OpenFOAMCase("test_case", base_dir=tmp_path)
    case.set_velocity(50.0)
    case.set_angle_of_attack(5.0)
    case.set_turbulence_model("kOmegaSST")
    case.generate()

    assert (case.case_dir / "0" / "U").exists()
    assert (case.case_dir / "0" / "p").exists()
    assert (case.case_dir / "constant" / "transportProperties").exists()
    assert (case.case_dir / "constant" / "turbulenceProperties").exists()
    assert (case.case_dir / "system" / "controlDict").exists()


def test_openfoam_case_set_velocity_rejects_nonpositive() -> None:
    case = OpenFOAMCase("test_case")
    with pytest.raises(InvalidCaseError):
        case.set_velocity(0)
    with pytest.raises(InvalidCaseError):
        case.set_velocity(-10.0)


def test_openfoam_case_run_raises_without_generate(tmp_path: Path) -> None:
    case = OpenFOAMCase("test_case", base_dir=tmp_path)
    with pytest.raises(InvalidCaseError):
        case.run()


def test_openfoam_case_run_raises_not_found_when_generated_but_no_openfoam(tmp_path: Path) -> None:
    case = OpenFOAMCase("test_case", base_dir=tmp_path)
    case.generate()
    with pytest.raises(OpenFOAMNotFoundError):
        case.run()


def test_openfoam_not_found_error_message_gives_install_guidance() -> None:
    try:
        raise OpenFOAMNotFoundError("simpleFoam")
    except OpenFOAMNotFoundError as exc:
        message = str(exc)
        assert "openfoam" in message.lower()
        assert "install" in message.lower()


def test_parse_force_coefficients_reads_last_row(tmp_path: Path) -> None:
    out_dir = tmp_path / "postProcessing" / "forceCoeffs1" / "0"
    out_dir.mkdir(parents=True)
    (out_dir / "coefficient.dat").write_text(
        "# Time Cd Cl CmPitch\n100 0.0234 0.512 -0.021\n200 0.0231 0.515 -0.020\n"
    )
    result = parse_force_coefficients(tmp_path)
    assert math.isclose(result.time, 200.0)
    assert math.isclose(result.cd, 0.0231)
    assert math.isclose(result.cl, 0.515)
    assert math.isclose(result.cm_pitch, -0.020)


def test_parse_force_coefficients_raises_without_postprocessing_dir(tmp_path: Path) -> None:
    with pytest.raises(InvalidCaseError):
        parse_force_coefficients(tmp_path)


def test_parse_force_coefficients_raises_on_empty_data(tmp_path: Path) -> None:
    out_dir = tmp_path / "postProcessing" / "forceCoeffs1" / "0"
    out_dir.mkdir(parents=True)
    (out_dir / "coefficient.dat").write_text("# Time Cd Cl CmPitch\n")
    with pytest.raises(InvalidCaseError):
        parse_force_coefficients(tmp_path)


def test_openfoam_case_postprocess_integrates_with_parser(tmp_path: Path) -> None:
    case = OpenFOAMCase("test_case", base_dir=tmp_path)
    out_dir = case.case_dir / "postProcessing" / "forceCoeffs1" / "0"
    out_dir.mkdir(parents=True)
    (out_dir / "coefficient.dat").write_text("# Time Cd Cl CmPitch\n500 0.025 0.6 -0.01\n")
    result = case.postprocess()
    assert math.isclose(result.cl, 0.6)
