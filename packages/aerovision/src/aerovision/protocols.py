"""Structural interfaces for aerospace computer-vision tasks.

Reference
---------
- These are ``Protocol`` classes (PEP 544 structural typing) defining
  the method signatures a real inspection/detection backend would
  implement -- they contain no logic themselves. This lets the same
  "automate around a heavy external tool, don't require it" thinking
  used in ``aerocfd`` apply here too: aerovision's core package stays
  free of PyTorch/ONNX/OpenCV as hard dependencies, while giving
  callers (and future GDX Aerospace packages) a stable contract to code
  against once a real model backend is plugged in.

Assumptions
-----------
- No protocol here is "implemented" by a real ML model in this package
  -- see :mod:`aerovision.edge_detection` for the one classical,
  dependency-free (numpy-only) algorithm this package actually runs.
  Implementing ``ImageClassifier``/``ObjectDetector`` with a real
  PyTorch or ONNX model is left to the caller's own code, which can
  depend on this package's Protocols for a stable interface without
  aerovision itself needing to depend on those heavy libraries.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class ImageClassifier(Protocol):
    """A whole-image classifier (e.g. "damaged" vs "undamaged")."""

    def predict(self, image: np.ndarray) -> dict[str, float]:
        """Return a mapping of class label to predicted probability/score.

        Parameters
        ----------
        image:
            Input image, shape ``(H, W)`` or ``(H, W, C)``.

        Returns
        -------
        dict[str, float]
            Class label -> score.

        """
        ...


@runtime_checkable
class ObjectDetector(Protocol):
    """A bounding-box object detector (e.g. locating cracks or aircraft in an image)."""

    def predict(self, image: np.ndarray) -> list[dict[str, float | str]]:
        """Return a list of detections.

        Parameters
        ----------
        image:
            Input image, shape ``(H, W)`` or ``(H, W, C)``.

        Returns
        -------
        list[dict[str, float | str]]
            One dict per detection, expected to include at least
            ``"label"`` (str), ``"score"`` (float), and bounding-box
            coordinates (e.g. ``"x_min"``, ``"y_min"``, ``"x_max"``,
            ``"y_max"``) -- the exact key set is up to the implementing
            backend, since different detection frameworks use slightly
            different conventions.

        """
        ...


@runtime_checkable
class AnomalyDetector(Protocol):
    """A pixel-wise or region-wise anomaly/defect detector (e.g. corrosion, surface damage)."""

    def predict(self, image: np.ndarray) -> np.ndarray:
        """Return a per-pixel (or per-region) anomaly score map.

        Parameters
        ----------
        image:
            Input image, shape ``(H, W)`` or ``(H, W, C)``.

        Returns
        -------
        numpy.ndarray
            Anomaly score map, shape ``(H, W)``, higher values indicating
            more likely anomalies.

        """
        ...
