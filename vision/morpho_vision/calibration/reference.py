"""
Reference target models and specifications for scale calibration.
Inspired by Easy Leaf Area standards and ISO biometric calibration.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class CalibrationTarget:
    """Represents a geometric calibration target with known physical dimensions."""
    name: str = "Standard Red Square"
    shape: str = "square"  # "square", "rectangle", "circle"
    color: str = "red"     # "red", "blue", "green"
    area_cm2: float = 4.0  # 2.0 cm x 2.0 cm
    width_cm: float = 2.0
    height_cm: float = 2.0


@dataclass
class CalibrationResult:
    """Result of scale calibration on a scanned image."""
    pixels_per_cm: float
    pixels_per_mm: float
    cm2_per_pixel: float
    mm2_per_pixel: float
    marker_detected: bool
    marker_box: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h) in pixels
    marker_contour: Optional[any] = None
    marker_pixel_area: float = 0.0
    method: str = "MARKER"  # "MARKER" or "DPI_FALLBACK"
    dpi_equivalent: float = 0.0
    relative_error_pct: Optional[float] = None  # Populated when validating standard
