"""Validate the GDX Aerospace ecosystem manifest against the actual workspace."""

from __future__ import annotations

from pathlib import Path

import pytest
from gdxaerospace.manifest import list_packages, package_info, phase_names


def _actual_workspace_packages() -> set[str]:
    packages_dir = Path(__file__).resolve().parents[2]
    return {
        p.name
        for p in packages_dir.iterdir()
        if p.is_dir() and p.name != "gdxaerospace" and (p / "pyproject.toml").exists()
    }


def test_manifest_matches_actual_workspace_packages() -> None:
    """Every package directory in the workspace must appear in the manifest,
    and vice versa -- this is the test that would catch a forgotten or
    misspelled entry."""
    assert set(list_packages()) == _actual_workspace_packages()


def test_list_packages_returns_sorted_names() -> None:
    names = list_packages()
    assert names == sorted(names)


def test_list_packages_phase_filter_matches_individual_lookups() -> None:
    for phase in range(1, 11):
        filtered = list_packages(phase=phase)
        assert filtered  # every phase 1-10 should have at least one package
        for name in filtered:
            assert package_info(name).phase == phase


def test_list_packages_phase_filter_covers_all_packages() -> None:
    """Every package should belong to exactly one of phases 1-10."""
    all_names = set(list_packages())
    phase_union: set[str] = set()
    for phase in range(1, 11):
        phase_union.update(list_packages(phase=phase))
    assert phase_union == all_names


def test_package_info_returns_correct_entry() -> None:
    info = package_info("orbitpy")
    assert info.name == "orbitpy"
    assert info.phase == 6
    assert info.phase_name == "Space"
    assert len(info.description) > 0


def test_package_info_unknown_name_raises_key_error() -> None:
    with pytest.raises(KeyError):
        package_info("not-a-real-package")


def test_phase_names_covers_phases_one_through_ten() -> None:
    names = phase_names()
    assert set(names.keys()) == set(range(1, 11))


def test_phase_names_values_are_nonempty_strings() -> None:
    for name in phase_names().values():
        assert isinstance(name, str)
        assert len(name) > 0


def test_every_manifest_entry_has_nonempty_description() -> None:
    for name in list_packages():
        assert len(package_info(name).description) > 0


def test_every_manifest_entry_phase_matches_its_own_phase_name() -> None:
    names_by_phase = phase_names()
    for name in list_packages():
        info = package_info(name)
        assert names_by_phase[info.phase] == info.phase_name
