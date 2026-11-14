"""
Bruchid beetle emergence hole detection module for tree seeds.
Targets seed predation by bruchids (Bruchidius spp., Caryedon serratus, Callosobruchus)
common in Sahelian trees (Vachellia tortilis, Faidherbia albida, Parkia biglobosa).
Detects characteristic circular exit holes (0.8 mm - 3.5 mm).
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional, Tuple
import cv2
import numpy as np


@dataclass
class BruchidDetectionResult:
    """Detection results for a single seed."""
    is_attacked: bool
    hole_count: int
    hole_diameters_mm: List[float] = field(default_factory=list)
    hole_contours: List[np.ndarray] = field(default_factory=list)


class BruchidDetector:
    """Detects circular emergence holes drilled by bruchid beetles into seeds."""

    def __init__(
        self,
        min_hole_diameter_mm: float = 0.8,
        max_hole_diameter_mm: float = 3.5,
        min_circularity: float = 0.50,
    ):
        self.min_hole_diameter_mm = min_hole_diameter_mm
        self.max_hole_diameter_mm = max_hole_diameter_mm
        self.min_circularity = min_circularity

    def inspect_seed(
        self,
        seed_contour: np.ndarray,
        seed_roi_bgr: np.ndarray,
        seed_roi_mask: np.ndarray,
        pixels_per_mm: float,
        mm2_per_pixel: float,
    ) -> BruchidDetectionResult:
        """Inspects a single seed for bruchid beetle exit holes.
        
        Args:
            seed_contour: Contour in ROI coordinates.
            seed_roi_bgr: Color image cropped to seed bounding box.
            seed_roi_mask: Binary mask of the seed in the ROI (with potential holes as 0).
            pixels_per_mm: Scale factor.
            mm2_per_pixel: Scale factor.
            
        Returns:
            BruchidDetectionResult with attack flag, hole count, and diameters.
        """
        min_hole_px = max(4.0, math.pi * ((self.min_hole_diameter_mm / 2.0) * pixels_per_mm) ** 2)
        max_hole_px = math.pi * ((self.max_hole_diameter_mm / 2.0) * pixels_per_mm) ** 2

        detected_holes: List[np.ndarray] = []
        hole_diameters: List[float] = []

        # 1. Filled seed representation: fill the outer contour of this seed
        h_roi, w_roi = seed_roi_mask.shape
        filled_seed = np.zeros((h_roi, w_roi), dtype=np.uint8)
        cv2.drawContours(filled_seed, [seed_contour], -1, 255, -1)

        # 2. Mode A: Perforations exposing scanner background
        # Pixels that belong to filled seed body but are missing (0) in seed_roi_mask
        internal_voids = cv2.bitwise_and(filled_seed, cv2.bitwise_not(seed_roi_mask))

        # Erode border of filled seed slightly to avoid detecting boundary irregularities
        border_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        eroded_filled = cv2.erode(filled_seed, border_kernel, iterations=1)
        internal_voids = cv2.bitwise_and(internal_voids, eroded_filled)

        void_cnts, _ = cv2.findContours(internal_voids, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for vc in void_cnts:
            area = cv2.contourArea(vc)
            if min_hole_px * 0.6 <= area <= max_hole_px * 1.4:
                peri = cv2.arcLength(vc, True)
                if peri > 0:
                    circ = (4.0 * math.pi * area) / (peri**2)
                    if circ >= self.min_circularity:
                        d_mm = 2.0 * math.sqrt(area * mm2_per_pixel / math.pi)
                        detected_holes.append(vc)
                        hole_diameters.append(round(d_mm, 2))

        # 3. Mode B: Dark cavities inside seed coat (unperforated or shadowed exit holes)
        if len(detected_holes) == 0 and seed_roi_bgr.size > 0:
            gray_roi = cv2.cvtColor(seed_roi_bgr, cv2.COLOR_BGR2GRAY)
            # Mask out background
            masked_gray = cv2.bitwise_and(gray_roi, gray_roi, mask=eroded_filled)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            blackhat = cv2.morphologyEx(masked_gray, cv2.MORPH_BLACKHAT, kernel)
            _, spot_mask = cv2.threshold(blackhat, 25, 255, cv2.THRESH_BINARY)
            spot_mask = cv2.bitwise_and(spot_mask, eroded_filled)

            spot_cnts, _ = cv2.findContours(spot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for sc in spot_cnts:
                s_area = cv2.contourArea(sc)
                if min_hole_px <= s_area <= max_hole_px:
                    s_peri = cv2.arcLength(sc, True)
                    if s_peri > 0:
                        s_circ = (4.0 * math.pi * s_area) / (s_peri**2)
                        if s_circ >= self.min_circularity:
                            d_mm = 2.0 * math.sqrt(s_area * mm2_per_pixel / math.pi)
                            detected_holes.append(sc)
                            hole_diameters.append(round(d_mm, 2))

        is_attacked = len(detected_holes) > 0

        return BruchidDetectionResult(
            is_attacked=is_attacked,
            hole_count=len(detected_holes),
            hole_diameters_mm=hole_diameters,
            hole_contours=detected_holes,
        )
