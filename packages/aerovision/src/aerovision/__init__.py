"""aerovision — aerospace computer-vision interfaces and a classical baseline."""

from __future__ import annotations

from aerovision.edge_detection import detect_linear_features, gradient_magnitude, sobel_gradients
from aerovision.exceptions import InvalidImageError
from aerovision.protocols import AnomalyDetector, ImageClassifier, ObjectDetector

__all__ = [
    "AnomalyDetector",
    "ImageClassifier",
    "InvalidImageError",
    "ObjectDetector",
    "detect_linear_features",
    "gradient_magnitude",
    "sobel_gradients",
]

__version__ = "0.1.0"
