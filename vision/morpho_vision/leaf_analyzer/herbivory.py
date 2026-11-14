"""
Herbivory damage quantification module for leaves.
Estimates the percentage of leaf area lost to herbivory (caterpillars, beetles, grasshoppers)
by reconstructing the intact leaf boundary using Convex Hull and contour closing,
and detecting internal chewing perforations.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import cv2
import numpy as np


@dataclass
class HerbivoryResult:
    """Quantitative results of herbivory analysis on a single leaf."""
    leaf_area_measured_cm2: float
    reconstructed_intact_area_cm2: float
    consumed_area_cm2: float
    herbivory_percentage: float  # (consumed / intact) * 100
    internal_hole_count: int
    internal_holes_area_cm2: float
    marginal_damage_area_cm2: float
    intact_hull_contour: np.ndarray
    hole_contours: List[np.ndarray]


class HerbivoryEstimator:
    """Calculates herbivory damage through boundary reconstruction and hole detection."""

    def __init__(
        self,
        min_hole_area_mm2: float = 0.5,
        convex_closing_kernel_mm: float = 2.0,
    ):
        self.min_hole_area_mm2 = min_hole_area_mm2
        self.convex_closing_kernel_mm = convex_closing_kernel_mm

    def estimate_herbivory(
        self,
        leaf_contour: np.ndarray,
        leaf_mask: np.ndarray,
        cm2_per_pixel: float,
        mm2_per_pixel: float,
    ) -> HerbivoryResult:
        """Analyzes a leaf for marginal and internal herbivory damage.
        
        Args:
            leaf_contour: Exterior contour of the leaf.
            leaf_mask: Binary mask of this specific leaf (lamina = 255, background = 0).
            cm2_per_pixel: Spatial scale (cm² per pixel).
            mm2_per_pixel: Spatial scale (mm² per pixel).
            
        Returns:
            HerbivoryResult with consumed area, damage %, and contours.
        """
        measured_pixel_area = cv2.contourArea(leaf_contour)
        measured_cm2 = measured_pixel_area * cm2_per_pixel

        # 1. Detect internal holes (perforations/chewing windows)
        # Using RETR_CCOMP to get two-level hierarchy (exterior contour and interior holes)
        contours, hierarchy = cv2.findContours(
            leaf_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
        )

        internal_holes = []
        internal_holes_px_area = 0.0

        if hierarchy is not None and len(contours) > 1:
            for idx, cnt in enumerate(contours):
                # In RETR_CCOMP, hierarchy[0][idx][3] != -1 indicates a hole inside an outer contour
                if hierarchy[0][idx][3] != -1:
                    hole_area_px = cv2.contourArea(cnt)
                    hole_area_mm2 = hole_area_px * mm2_per_pixel
                    if hole_area_mm2 >= self.min_hole_area_mm2:
                        internal_holes.append(cnt)
                        internal_holes_px_area += hole_area_px

        internal_holes_cm2 = internal_holes_px_area * cm2_per_pixel

        # 2. Reconstruct intact leaf perimeter via Convex Hull
        hull = cv2.convexHull(leaf_contour)
        hull_pixel_area = cv2.contourArea(hull)

        # For natural leaves that are naturally concave (lobed leaves, heart-shaped cordate bases),
        # an unconstrained convex hull can slightly overestimate intact area.
        # We perform alpha-shape inspired morphological reconstruction:
        # Reconstruct missing notches using morphological closing on the leaf mask.
        closing_px = max(5, int(self.convex_closing_kernel_mm / np.sqrt(mm2_per_pixel) * 4))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (closing_px, closing_px))
        closed_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE, kernel)
        
        # Fill any internal cavities in closed mask
        closed_filled = self._fill_holes_mask(closed_mask)
        closed_px_area = cv2.countNonZero(closed_filled)

        # Reconstructed intact area is bounded between closed_px_area and hull_pixel_area
        # Weighted combination: 70% closed-filled, 30% convex hull
        intact_pixel_area = max(measured_pixel_area + internal_holes_px_area, 
                                0.70 * closed_px_area + 0.30 * hull_pixel_area)
        
        intact_cm2 = intact_pixel_area * cm2_per_pixel
        consumed_cm2 = max(0.0, intact_cm2 - measured_cm2)
        
        marginal_cm2 = max(0.0, consumed_cm2 - internal_holes_cm2)
        herbivory_pct = (consumed_cm2 / intact_cm2 * 100.0) if intact_cm2 > 0 else 0.0

        return HerbivoryResult(
            leaf_area_measured_cm2=measured_cm2,
            reconstructed_intact_area_cm2=intact_cm2,
            consumed_area_cm2=consumed_cm2,
            herbivory_percentage=round(herbivory_pct, 2),
            internal_hole_count=len(internal_holes),
            internal_holes_area_cm2=round(internal_holes_cm2, 4),
            marginal_damage_area_cm2=round(marginal_cm2, 4),
            intact_hull_contour=hull,
            hole_contours=internal_holes,
        )

    @staticmethod
    def _fill_holes_mask(mask: np.ndarray) -> np.ndarray:
        """Fills internal holes in a binary mask."""
        h, w = mask.shape
        fill_mask = np.zeros((h + 2, w + 2), np.uint8)
        flooded = mask.copy()
        cv2.floodFill(flooded, fill_mask, (0, 0), 255)
        inv_flooded = cv2.bitwise_not(flooded)
        return cv2.bitwise_or(mask, inv_flooded)
