"""
Unit tests for Scale Calibration & Certified Geometric Standard Error Verification.
Acceptance Criterion: Relative error on surface measurement < 1.5% compared to certified standard.
"""

from pathlib import Path
import cv2
import numpy as np
import pytest

from morpho_vision.calibration.calibrator import ScaleCalibrator
from morpho_vision.config import CalibrationConfig


@pytest.fixture
def sample_standard_path():
    p = Path(__file__).parent.parent / "data" / "samples" / "sample_geometric_standard.png"
    assert p.exists(), "Sample geometric standard image missing"
    return p


def test_marker_detection_and_scale(sample_standard_path):
    """Verifies that the red 4.0 cm² calibration square is detected accurately."""
    data = np.fromfile(str(sample_standard_path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

    config = CalibrationConfig(known_area_cm2=4.0)
    calibrator = ScaleCalibrator(config)
    calib = calibrator.calibrate(img)

    assert calib.marker_detected is True
    assert calib.method == "MARKER"
    # Image was generated at 300 DPI (118.11 px/cm)
    expected_px_per_cm = 300.0 / 2.54
    error_scale_pct = abs(calib.pixels_per_cm - expected_px_per_cm) / expected_px_per_cm * 100.0

    print(f"Scale detected: {calib.pixels_per_cm:.2f} px/cm, error: {error_scale_pct:.3f}%")
    assert error_scale_pct < 1.0, f"Scale error too high: {error_scale_pct:.2f}%"


def test_certified_geometric_standard_surface_error(sample_standard_path):
    """Acceptance Test: Relative error on surface measurement < 1.5%

    Evaluates:
    - Certified Square: 4.0 cm x 4.0 cm = 16.0 cm²
    - Certified Circle: radius 2.0 cm = 12.566 cm²
    - Certified Rectangle: 5.0 cm x 3.0 cm = 15.0 cm²
    """
    data = np.fromfile(str(sample_standard_path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

    calibrator = ScaleCalibrator(CalibrationConfig(known_area_cm2=4.0))
    calib = calibrator.calibrate(img)
    assert calib.marker_detected is True

    # Segment the green test shapes (excluding the red marker)
    # Green shapes are around x > 400
    green_roi = img[:, 350:]
    hsv = cv2.cvtColor(green_roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([25, 40, 40]), np.array([95, 255, 255]))

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Sort largest shapes
    valid_cnts = [c for c in cnts if cv2.contourArea(c) > 5000]
    valid_cnts.sort(key=cv2.contourArea, reverse=True)

    assert len(valid_cnts) >= 3, f"Expected 3 certified shapes, found {len(valid_cnts)}"

    measured_areas_cm2 = [cv2.contourArea(c) * calib.cm2_per_pixel for c in valid_cnts]

    # Ground truths: 16.0 cm², 15.0 cm², 12.566 cm²
    ground_truths = [16.0, 15.0, 12.566]

    for measured, truth in zip(measured_areas_cm2, ground_truths):
        rel_error = abs(measured - truth) / truth * 100.0
        print(f"Certified Standard: {truth} cm² | Measured: {measured:.3f} cm² | Error: {rel_error:.2f}%")
        assert rel_error < 1.5, f"Relative error {rel_error:.2f}% exceeds acceptance threshold of 1.5%"


def test_fallback_dpi_mode():
    """Verifies DPI fallback mode when no marker is present."""
    calibrator = ScaleCalibrator(CalibrationConfig(fallback_dpi=600.0))
    calib = calibrator.calibrate(np.ones((500, 500, 3), dtype=np.uint8) * 255, force_dpi=True)

    assert calib.marker_detected is False
    assert calib.method == "DPI_FALLBACK"
    assert abs(calib.pixels_per_cm - (600.0 / 2.54)) < 1e-4
    assert abs(calib.cm2_per_pixel - (2.54 / 600.0) ** 2) < 1e-6
