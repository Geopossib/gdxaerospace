"""Validate the classical Sobel edge/linear-feature detector."""

from __future__ import annotations

import math

import numpy as np
import pytest
from aerovision.edge_detection import detect_linear_features, gradient_magnitude, sobel_gradients
from aerovision.exceptions import InvalidImageError


def test_sobel_gradients_vertical_edge() -> None:
    image = np.zeros((5, 6))
    image[:, 3:] = 1.0
    gx, gy = sobel_gradients(image)
    assert math.isclose(gx[2, 1], 4.0, rel_tol=1e-9)
    assert math.isclose(gy[2, 1], 0.0, abs_tol=1e-9)


def test_sobel_gradients_horizontal_edge() -> None:
    """A horizontal edge should produce a strong vertical gradient, zero horizontal."""
    image = np.zeros((6, 5))
    image[3:, :] = 1.0
    gx, gy = sobel_gradients(image)
    assert math.isclose(gy[1, 2], 4.0, rel_tol=1e-9)
    assert math.isclose(gx[1, 2], 0.0, abs_tol=1e-9)


def test_sobel_gradients_uniform_image_has_zero_gradient() -> None:
    image = np.full((5, 5), 3.0)
    gx, gy = sobel_gradients(image)
    assert np.allclose(gx, 0.0)
    assert np.allclose(gy, 0.0)


def test_sobel_gradients_output_shape_shrinks_by_two() -> None:
    image = np.zeros((10, 8))
    gx, gy = sobel_gradients(image)
    assert gx.shape == (8, 6)
    assert gy.shape == (8, 6)


def test_sobel_gradients_rejects_non_2d_image() -> None:
    with pytest.raises(InvalidImageError):
        sobel_gradients(np.zeros((5, 5, 3)))


def test_sobel_gradients_rejects_too_small_image() -> None:
    with pytest.raises(InvalidImageError):
        sobel_gradients(np.zeros((2, 2)))


def test_gradient_magnitude_matches_pythagorean_combination() -> None:
    image = np.zeros((6, 6))
    image[3:, 3:] = 1.0  # a corner, producing both gx and gy components somewhere
    gx, gy = sobel_gradients(image)
    mag = gradient_magnitude(image)
    assert np.allclose(mag, np.sqrt(gx**2 + gy**2))


def test_gradient_magnitude_zero_for_uniform_image() -> None:
    image = np.full((5, 5), 7.0)
    mag = gradient_magnitude(image)
    assert np.allclose(mag, 0.0)


def test_detect_linear_features_matches_threshold_logic() -> None:
    image = np.zeros((5, 6))
    image[:, 3:] = 1.0
    mag = gradient_magnitude(image)
    mask = detect_linear_features(image, threshold=2.0)
    assert np.array_equal(mask, mag > 2.0)


def test_detect_linear_features_higher_threshold_flags_fewer_pixels() -> None:
    image = np.zeros((8, 8))
    image[:, 4:] = 1.0
    low_threshold_mask = detect_linear_features(image, threshold=0.5)
    high_threshold_mask = detect_linear_features(image, threshold=3.9)
    assert low_threshold_mask.sum() >= high_threshold_mask.sum()


def test_detect_linear_features_no_edges_in_uniform_image() -> None:
    image = np.full((5, 5), 1.0)
    mask = detect_linear_features(image, threshold=0.1)
    assert not mask.any()


def test_detect_linear_features_rejects_nonpositive_threshold() -> None:
    image = np.zeros((5, 5))
    with pytest.raises(InvalidImageError):
        detect_linear_features(image, threshold=0)
    with pytest.raises(InvalidImageError):
        detect_linear_features(image, threshold=-1.0)
