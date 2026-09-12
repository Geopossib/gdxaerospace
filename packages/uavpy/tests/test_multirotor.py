"""Validate multirotor hover power and flight-time estimation."""

from __future__ import annotations

import math

import pytest
from uavpy.exceptions import InvalidUAVInputError
from uavpy.multirotor import G0, Multirotor, actual_hover_power, ideal_hover_power


def test_ideal_hover_power_matches_formula() -> None:
    t, a, rho = 24.52, 0.2027, 1.225
    expected = t**1.5 / math.sqrt(2 * rho * a)
    assert math.isclose(ideal_hover_power(t, a, rho), expected, rel_tol=1e-9)


def test_ideal_hover_power_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidUAVInputError):
        ideal_hover_power(0, 0.2027)
    with pytest.raises(InvalidUAVInputError):
        ideal_hover_power(24.52, 0)
    with pytest.raises(InvalidUAVInputError):
        ideal_hover_power(24.52, 0.2027, air_density=0)


def test_actual_hover_power_exceeds_ideal() -> None:
    """Real rotors always need more than the ideal induced power (FM < 1)."""
    ideal = ideal_hover_power(24.52, 0.2027)
    actual = actual_hover_power(24.52, 0.2027, figure_of_merit=0.6)
    assert actual > ideal
    assert math.isclose(actual, ideal / 0.6, rel_tol=1e-9)


def test_actual_hover_power_higher_fm_reduces_power() -> None:
    low_fm = actual_hover_power(24.52, 0.2027, figure_of_merit=0.5)
    high_fm = actual_hover_power(24.52, 0.2027, figure_of_merit=0.8)
    assert high_fm < low_fm


def test_actual_hover_power_rejects_invalid_fm() -> None:
    with pytest.raises(InvalidUAVInputError):
        actual_hover_power(24.52, 0.2027, figure_of_merit=0)
    with pytest.raises(InvalidUAVInputError):
        actual_hover_power(24.52, 0.2027, figure_of_merit=1.5)


def test_multirotor_weight_matches_mass_times_g() -> None:
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0)
    assert math.isclose(uav.weight(), 2.5 * G0, rel_tol=1e-9)


def test_multirotor_total_disk_area_matches_formula() -> None:
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0)
    expected = 4 * math.pi * 0.127**2
    assert math.isclose(uav.total_disk_area(), expected, rel_tol=1e-9)


def test_multirotor_thrust_to_weight_matches_formula() -> None:
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0)
    ttw = uav.thrust_to_weight(max_thrust_per_motor=8.0)
    expected = (4 * 8.0) / uav.weight()
    assert math.isclose(ttw, expected, rel_tol=1e-9)


def test_multirotor_hover_power_matches_free_function() -> None:
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0, figure_of_merit=0.6)
    expected = actual_hover_power(uav.weight(), uav.total_disk_area(), figure_of_merit=0.6)
    assert math.isclose(uav.hover_power(), expected, rel_tol=1e-9)


def test_multirotor_battery_energy_matches_formula() -> None:
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0)
    assert math.isclose(uav.battery_energy_wh(), 22.2 * 5000.0 / 1000, rel_tol=1e-9)


def test_multirotor_flight_time_is_physically_plausible() -> None:
    """A 2.5 kg quad with a 5000 mAh 6S-class battery should give a realistic
    flight time in the ballpark of real-world small multirotor performance."""
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0)
    flight_time = uav.flight_time_minutes()
    assert 10 < flight_time < 30


def test_multirotor_heavier_uav_flies_less_time() -> None:
    light = Multirotor(2.0, 4, 0.127, 22.2, 5000.0)
    heavy = Multirotor(4.0, 4, 0.127, 22.2, 5000.0)
    assert heavy.flight_time_minutes() < light.flight_time_minutes()


def test_multirotor_bigger_battery_flies_longer() -> None:
    small_battery = Multirotor(2.5, 4, 0.127, 22.2, 3000.0)
    big_battery = Multirotor(2.5, 4, 0.127, 22.2, 6000.0)
    assert big_battery.flight_time_minutes() > small_battery.flight_time_minutes()


def test_multirotor_rejects_invalid_construction() -> None:
    with pytest.raises(InvalidUAVInputError):
        Multirotor(0, 4, 0.127, 22.2, 5000.0)
    with pytest.raises(InvalidUAVInputError):
        Multirotor(2.5, 0, 0.127, 22.2, 5000.0)
    with pytest.raises(InvalidUAVInputError):
        Multirotor(2.5, 4, 0, 22.2, 5000.0)
    with pytest.raises(InvalidUAVInputError):
        Multirotor(2.5, 4, 0.127, 0, 5000.0)
    with pytest.raises(InvalidUAVInputError):
        Multirotor(2.5, 4, 0.127, 22.2, 0)
    with pytest.raises(InvalidUAVInputError):
        Multirotor(2.5, 4, 0.127, 22.2, 5000.0, usable_capacity_fraction=1.5)


def test_multirotor_thrust_to_weight_rejects_nonpositive_thrust() -> None:
    uav = Multirotor(2.5, 4, 0.127, 22.2, 5000.0)
    with pytest.raises(InvalidUAVInputError):
        uav.thrust_to_weight(0)
