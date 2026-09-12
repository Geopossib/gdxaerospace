"""Validate that the aerovision Protocols correctly perform structural typing."""

from __future__ import annotations

import numpy as np
from aerovision.protocols import AnomalyDetector, ImageClassifier, ObjectDetector


class _FakeClassifier:
    def predict(self, image: np.ndarray) -> dict[str, float]:
        return {"damaged": 0.1, "undamaged": 0.9}


class _FakeDetector:
    def predict(self, image: np.ndarray) -> list[dict[str, float | str]]:
        return [{"label": "crack", "score": 0.8, "x_min": 0.0, "y_min": 0.0}]


class _FakeAnomalyDetector:
    def predict(self, image: np.ndarray) -> np.ndarray:
        return np.zeros(image.shape[:2])


class _NotAClassifier:
    def some_other_method(self) -> None:
        pass


def test_fake_classifier_satisfies_image_classifier_protocol() -> None:
    assert isinstance(_FakeClassifier(), ImageClassifier)


def test_fake_detector_satisfies_object_detector_protocol() -> None:
    assert isinstance(_FakeDetector(), ObjectDetector)


def test_fake_anomaly_detector_satisfies_anomaly_detector_protocol() -> None:
    assert isinstance(_FakeAnomalyDetector(), AnomalyDetector)


def test_unrelated_class_does_not_satisfy_any_protocol() -> None:
    obj = _NotAClassifier()
    assert not isinstance(obj, ImageClassifier)
    assert not isinstance(obj, ObjectDetector)
    assert not isinstance(obj, AnomalyDetector)


def test_classifier_predict_returns_expected_shape() -> None:
    classifier = _FakeClassifier()
    result = classifier.predict(np.zeros((10, 10)))
    assert isinstance(result, dict)
    assert "damaged" in result


def test_anomaly_detector_predict_returns_2d_array() -> None:
    detector = _FakeAnomalyDetector()
    image = np.zeros((10, 12, 3))
    result = detector.predict(image)
    assert result.shape == (10, 12)
