"""
Leaf morphometric analyzer module.
Extracts individual and total leaf area, perimeter, Feret length, maximum width,
circularity index, aspect ratio, and coordinates.
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional, Tuple
import cv2
import numpy as np

from morpho_vision.calibration.reference import CalibrationResult
from morpho_vision.config import LeafAnalysisConfig
from morpho_vision.leaf_analyzer.herbivory import HerbivoryEstimator, HerbivoryResult
from morpho_vision.segmentation.leaflet_separator import LeafletSeparator
from morpho_vision.segmentation.morphological import MorphologicalCleaner


@dataclass
class SingleLeafMetrics:
    """Morphometric measurements of an individual leaf or leaflet."""
    leaf_id: int
    area_cm2: float
    perimeter_cm: float
    length_cm: float
    width_cm: float
    circularity: float
    aspect_ratio: float
    centroid_x: float
    centroid_y: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h) in pixels
    herbivory: HerbivoryResult
    contour: np.ndarray


@dataclass
class LeafScanResult:
    """Aggregated leaf morphometric measurements for an entire scan sheet."""
    qr_code_tag: Optional[str]
    total_leaf_area_cm2: float
    mean_leaf_area_cm2: float
    std_leaf_area_cm2: float
    leaf_count: int
    mean_length_cm: float
    mean_width_cm: float
    mean_circularity: float
    mean_herbivory_pct: float
    leaves: List[SingleLeafMetrics] = field(default_factory=list)
    is_compound: bool = False
    rachis_detected: bool = False
    scale_info: Optional[CalibrationResult] = None


class LeafMorphoAnalyzer:
    """Extracts functional trait morphometrics from segmented leaf images."""

    def __init__(self, config: Optional[LeafAnalysisConfig] = None):
        self.config = config or LeafAnalysisConfig()
        self.herbivory_estimator = HerbivoryEstimator(
            min_hole_area_mm2=self.config.min_hole_area_mm2,
            convex_closing_kernel_mm=self.config.convex_hull_gap_closing_mm,
        )
        self.cleaner = MorphologicalCleaner()
        self.leaflet_separator = LeafletSeparator()

    def analyze(
        self,
        leaf_mask: np.ndarray,
        calib: CalibrationResult,
        qr_tag: Optional[str] = None,
        is_compound: Optional[bool] = None,
    ) -> LeafScanResult:
        """Analyzes a leaf mask and returns comprehensive biometric metrics.
        
        Args:
            leaf_mask: Clean binary mask of leaf tissue.
            calib: Calibration result providing spatial scale.
            qr_tag: Optional scanned tree QR code tag.
            is_compound: Whether to treat as compound leaf (Parkia, Vachellia, etc.).
            
        Returns:
            LeafScanResult with summary and per-leaf metrics.
        """
        compound_flag = is_compound if is_compound is not None else self.config.is_compound_leaf
        rachis_detected = False

        if compound_flag:
            labeled, contours, rachis_mask = self.leaflet_separator.separate_leaflets(leaf_mask)
            rachis_detected = rachis_mask is not None
        else:
            # Simple or discrete leaves
            contours, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter out dust/tiny noise (< 0.1 cm²)
        min_area_px = 0.1 / calib.cm2_per_pixel if calib.cm2_per_pixel > 0 else 50
        valid_contours = [c for c in contours if cv2.contourArea(c) >= min_area_px]

        # Sort contours spatially (top to bottom, left to right)
        valid_contours.sort(key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))

        leaf_metrics_list: List[SingleLeafMetrics] = []
        for leaf_id, cnt in enumerate(valid_contours, start=1):
            metrics = self._measure_single_leaf(cnt, leaf_mask, calib, leaf_id)
            leaf_metrics_list.append(metrics)

        # Aggregate summary statistics
        if leaf_metrics_list:
            areas = [m.area_cm2 for m in leaf_metrics_list]
            lengths = [m.length_cm for m in leaf_metrics_list]
            widths = [m.width_cm for m in leaf_metrics_list]
            circs = [m.circularity for m in leaf_metrics_list]
            herbs = [m.herbivory.herbivory_percentage for m in leaf_metrics_list]

            total_area = sum(areas)
            mean_area = float(np.mean(areas))
            std_area = float(np.std(areas))
            mean_len = float(np.mean(lengths))
            mean_wid = float(np.mean(widths))
            mean_circ = float(np.mean(circs))
            mean_herb = float(np.mean(herbs))
        else:
            total_area = mean_area = std_area = mean_len = mean_wid = mean_circ = mean_herb = 0.0

        return LeafScanResult(
            qr_code_tag=qr_tag,
            total_leaf_area_cm2=round(total_area, 3),
            mean_leaf_area_cm2=round(mean_area, 3),
            std_leaf_area_cm2=round(std_area, 3),
            leaf_count=len(leaf_metrics_list),
            mean_length_cm=round(mean_len, 2),
            mean_width_cm=round(mean_wid, 2),
            mean_circularity=round(mean_circ, 3),
            mean_herbivory_pct=round(mean_herb, 2),
            leaves=leaf_metrics_list,
            is_compound=compound_flag,
            rachis_detected=rachis_detected,
            scale_info=calib,
        )

    def _measure_single_leaf(
        self,
        cnt: np.ndarray,
        full_mask: np.ndarray,
        calib: CalibrationResult,
        leaf_id: int,
    ) -> SingleLeafMetrics:
        """Extracts morphometrics for one individual leaf/leaflet."""
        px_area = cv2.contourArea(cnt)
        area_cm2 = px_area * calib.cm2_per_pixel

        # Perimeter
        px_perimeter = cv2.arcLength(cnt, True)
        perimeter_cm = px_perimeter / calib.pixels_per_cm if calib.pixels_per_cm > 0 else 0.0

        # Minimum Area Rect (oriented bounding box) for Length and Width
        rect = cv2.minAreaRect(cnt)
        (_, _), (rw, rh), _ = rect
        len_px = max(rw, rh)
        wid_px = min(rw, rh)

        # Compute exact Maximum Feret Diameter via convex hull pairwise distance if points > 4
        hull = cv2.convexHull(cnt)
        if len(hull) >= 4:
            # Pairwise distance along hull
            hull_pts = hull[:, 0, :]
            # Fast Feret diameter via coordinate difference
            dists = np.linalg.norm(hull_pts[:, None, :] - hull_pts[None, :, :], axis=-1)
            feret_max_px = dists.max()
            if feret_max_px > len_px:
                len_px = feret_max_px

        length_cm = len_px / calib.pixels_per_cm if calib.pixels_per_cm > 0 else 0.0
        width_cm = wid_px / calib.pixels_per_cm if calib.pixels_per_cm > 0 else 0.0

        # Circularity Index: 4 * pi * Area / Perimeter^2 (1.0 = perfect circle)
        if px_perimeter > 0:
            circularity = (4.0 * math.pi * px_area) / (px_perimeter**2)
            circularity = min(1.0, max(0.0, circularity))
        else:
            circularity = 0.0

        # Aspect ratio: Length / Width
        aspect_ratio = (length_cm / width_cm) if width_cm > 0 else 1.0

        # Centroid
        m = cv2.moments(cnt)
        if m["m00"] != 0:
            cx = m["m10"] / m["m00"]
            cy = m["m01"] / m["m00"]
        else:
            bx, by, bw, bh = cv2.boundingRect(cnt)
            cx = bx + bw / 2.0
            cy = by + bh / 2.0

        # Bounding box
        bx, by, bw, bh = cv2.boundingRect(cnt)

        # Isolate this leaf's local mask for internal hole / herbivory estimation
        pad = 5
        h_full, w_full = full_mask.shape
        x1 = max(0, bx - pad)
        y1 = max(0, by - pad)
        x2 = min(w_full, bx + bw + pad)
        y2 = min(h_full, by + bh + pad)

        local_mask = np.zeros((y2 - y1, x2 - x1), dtype=np.uint8)
        # Shift contour to local roi
        shifted_cnt = cnt - np.array([x1, y1])
        cv2.drawContours(local_mask, [shifted_cnt], -1, 255, -1)

        # Herbivory estimation
        herbivory = self.herbivory_estimator.estimate_herbivory(
            leaf_contour=cnt,
            leaf_mask=local_mask,
            cm2_per_pixel=calib.cm2_per_pixel,
            mm2_per_pixel=calib.mm2_per_pixel,
        )

        return SingleLeafMetrics(
            leaf_id=leaf_id,
            area_cm2=round(area_cm2, 3),
            perimeter_cm=round(perimeter_cm, 2),
            length_cm=round(length_cm, 2),
            width_cm=round(width_cm, 2),
            circularity=round(circularity, 3),
            aspect_ratio=round(aspect_ratio, 2),
            centroid_x=round(cx, 1),
            centroid_y=round(cy, 1),
            bounding_box=(bx, by, bw, bh),
            herbivory=herbivory,
            contour=cnt,
        )
