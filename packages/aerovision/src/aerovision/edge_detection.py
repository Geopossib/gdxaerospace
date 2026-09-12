"""A classical, dependency-free (numpy-only) edge/linear-feature detector.

Reference
---------
- Sobel, I. & Feldman, G. (1968), the Sobel operator -- a standard,
  simple gradient-based edge detector, widely used as a first-pass
  feature extractor before (or instead of) a learned model. Gonzalez &
  Woods, *Digital Image Processing*, 4th ed., Ch. 10, for the standard
  3x3 kernel form and gradient-magnitude combination used here.

Assumptions
-----------
- This is a genuinely simple, general-purpose edge detector -- not a
  crack- or corrosion-specific classifier. Its usefulness for aerospace
  inspection is as a fast, interpretable first-pass highlighter of
  linear features (which cracks often are) and a baseline to compare
  a real learned model against, not a substitute for one.
- Operates on 2D grayscale arrays; convert color images to grayscale
  (e.g. by averaging channels) before calling.
"""

from __future__ import annotations

import numpy as np

from aerovision.exceptions import InvalidImageError

_SOBEL_X = np.array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]])
_SOBEL_Y = np.array([[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]])


def _check_grayscale_image(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=float)
    if image.ndim != 2:
        raise InvalidImageError(
            f"image must be a 2D grayscale array, got shape {image.shape}; "
            "convert color images to grayscale first"
        )
    if image.shape[0] < 3 or image.shape[1] < 3:
        raise InvalidImageError(
            f"image must be at least 3x3 for a 3x3 Sobel kernel, got shape {image.shape}"
        )
    return image


def _convolve3x3(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Valid-mode 2D convolution with a 3x3 kernel, via 9 shifted-and-summed slices."""
    height, width = image.shape
    out = np.zeros((height - 2, width - 2))
    for i in range(3):
        for j in range(3):
            # Correlation (not flipped kernel) -- the conventional form used for Sobel.
            out += kernel[i, j] * image[i : i + height - 2, j : j + width - 2]
    return out


def sobel_gradients(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute horizontal and vertical Sobel gradients of a grayscale image.

    Parameters
    ----------
    image:
        2D grayscale image array, at least 3x3.

    Returns
    -------
    (gx, gy):
        Horizontal and vertical gradient arrays, each shape
        ``(H-2, W-2)`` (valid-mode convolution: no padding, so the
        output is smaller than the input by one pixel on each edge).

    Example
    -------
    A synthetic vertical edge (left half dark, right half bright) should
    produce a strong horizontal gradient and near-zero vertical gradient:

    >>> import numpy as np
    >>> image = np.zeros((5, 6))
    >>> image[:, 3:] = 1.0
    >>> gx, gy = sobel_gradients(image)
    >>> float(gx[2, 1])
    4.0
    >>> float(gy[2, 1])
    0.0

    """
    image = _check_grayscale_image(image)
    gx = _convolve3x3(image, _SOBEL_X)
    gy = _convolve3x3(image, _SOBEL_Y)
    return gx, gy


def gradient_magnitude(image: np.ndarray) -> np.ndarray:
    """Compute the Sobel gradient magnitude: ``sqrt(gx^2 + gy^2)``.

    Parameters
    ----------
    image:
        2D grayscale image array, at least 3x3.

    Returns
    -------
    numpy.ndarray
        Gradient magnitude, shape ``(H-2, W-2)``.

    Example
    -------
    >>> import numpy as np
    >>> image = np.zeros((5, 6))
    >>> image[:, 3:] = 1.0
    >>> mag = gradient_magnitude(image)
    >>> float(mag[2, 1])
    4.0

    """
    gx, gy = sobel_gradients(image)
    return np.asarray(np.sqrt(gx**2 + gy**2))


def detect_linear_features(image: np.ndarray, threshold: float) -> np.ndarray:
    """Flag pixels whose gradient magnitude exceeds a threshold.

    A simple, general-purpose edge/crack highlighter.

    Parameters
    ----------
    image:
        2D grayscale image array, at least 3x3.
    threshold:
        Gradient-magnitude threshold, > 0. Pixels with magnitude above
        this value are flagged.

    Returns
    -------
    numpy.ndarray
        Boolean mask, shape ``(H-2, W-2)``, True where a linear feature
        (edge-like structure) is detected.

    Example
    -------
    >>> import numpy as np
    >>> image = np.zeros((5, 6))
    >>> image[:, 3:] = 1.0
    >>> mask = detect_linear_features(image, threshold=2.0)
    >>> bool(mask[2, 1])
    True
    >>> bool(mask[2, 3])
    False

    """
    if threshold <= 0:
        raise InvalidImageError(f"threshold must be positive, got {threshold!r}")
    return gradient_magnitude(image) > threshold
