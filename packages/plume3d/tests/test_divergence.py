"""Validate the simplified single-angle plume-divergence loss model."""

from __future__ import annotations

import math

import pytest
from plume3d.divergence import (
    divergence_thrust_correction,
    effective_specific_impulse,
    effective_thrust,
    half_angle_from_correction,
)
from plume3d.exceptions import InvalidPlumeGeometryError


def test_divergence_correction_matches_cosine() -> None:
    theta = math.radians(20.0)
    assert math.isclose(divergence_thrust_correction(theta), math.cos(theta), rel_tol=1e-9)


def test_zero_divergence_gives_no_loss() -> None:
    assert math.isclose(divergence_thrust_correction(0.0), 1.0, rel_tol=1e-9)


def test_correction_decreases_with_half_angle() -> None:
    small = divergence_thrust_correction(math.radians(10.0))
    large = divergence_thrust_correction(math.radians(40.0))
    assert large < small


def test_correction_rejects_out_of_range_angle() -> None:
    with pytest.raises(InvalidPlumeGeometryError):
        divergence_thrust_correction(-0.1)
    with pytest.raises(InvalidPlumeGeometryError):
        divergence_thrust_correction(math.pi / 2)
    with pytest.raises(InvalidPlumeGeometryError):
        divergence_thrust_correction(math.pi)


def test_effective_thrust_matches_ideal_times_correction() -> None:
    ideal, theta = 0.105, 0.3
    expected = ideal * math.cos(theta)
    assert math.isclose(effective_thrust(ideal, theta), expected, rel_tol=1e-9)


def test_effective_thrust_never_exceeds_ideal() -> None:
    ideal = 0.105
    for theta_deg in (0, 10, 20, 30, 45, 60):
        assert effective_thrust(ideal, math.radians(theta_deg)) <= ideal


def test_effective_thrust_rejects_nonpositive_ideal_thrust() -> None:
    with pytest.raises(InvalidPlumeGeometryError):
        effective_thrust(0, 0.3)


def test_effective_specific_impulse_matches_ideal_times_correction() -> None:
    ideal, theta = 2141.2, 0.3
    expected = ideal * math.cos(theta)
    assert math.isclose(effective_specific_impulse(ideal, theta), expected, rel_tol=1e-9)


def test_effective_specific_impulse_rejects_nonpositive_ideal_isp() -> None:
    with pytest.raises(InvalidPlumeGeometryError):
        effective_specific_impulse(0, 0.3)


def test_half_angle_from_correction_round_trips() -> None:
    for theta_deg in (5, 15, 30, 45):
        theta = math.radians(theta_deg)
        correction = divergence_thrust_correction(theta)
        recovered = half_angle_from_correction(correction)
        assert math.isclose(recovered, theta, rel_tol=1e-6)


def test_half_angle_from_correction_rejects_out_of_range() -> None:
    with pytest.raises(InvalidPlumeGeometryError):
        half_angle_from_correction(0)
    with pytest.raises(InvalidPlumeGeometryError):
        half_angle_from_correction(1.5)
