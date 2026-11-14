"""
Seed morphometric analyzer module.
Extracts projected area (mm²), length (L), width (l), eccentricity, circularity,
and coordinates for each seed, plus batch-level summary and bruchid infestation rate.
"""

from dataclasses import dataclass, field
import math
from typing import List, Optional, Tuple
import cv2
import numpy as np

from morpho_vision.calibration.reference import CalibrationResult
from morpho_vision.config import SeedAnalysisConfig
from morpho_vision.seed_analyzer.bruchid_detector import BruchidDetectionResult, BruchidDetector
from morpho_vision.seed_analyzer.counter import SeedCounter


@dataclass
class SingleSeedMetrics:
    """Biometric morphometrics of an individual seed."""
    seed_id: int
    length_mm: float
    width_mm: float
    projected_area_mm2: float
    perimeter_mm: float
    circularity: float
    eccentricity: float
    aspect_ratio: float
    centroid_x: float
    centroid_y: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)
    bruchid: BruchidDetectionResult
    contour: np.ndarray


@dataclass
class SeedScanResult:
    """Aggregated seed morphometric measurements for an entire seed lot."""
    qr_code_tag: Optional[str]
    total_seed_count: int
    mean_area_mm2: float
    std_area_mm2: float
    mean_length_mm: float
    std_length_mm: float
    mean_width_mm: float
    std_width_mm: float
    mean_eccentricity: float
    mean_circularity: float
    attacked_seed_count: int
    bruchid_attack_rate_pct: float
    seeds: List[SingleSeedMetrics] = field(default_factory=list)
    scale_info: Optional[CalibrationResult] = None


class SeedMorphoAnalyzer:
    """Extracts seed morphometrics and bruchid predation metrics from scan images."""

    def __init__(self, config: Optional[SeedAnalysisConfig] = None):
        self.config = config or SeedAnalysisConfig()
        self.counter = SeedCounter(
            min_seed_distance_mm=self.config.seed_distance_peak_min_mm,
            min_seed_area_mm2=1.0,
        )
        self.bruchid_detector = BruchidDetector(
            min_hole_diameter_mm=self.config.min_bruchid_hole_diameter_mm,
            max_hole_diameter_mm=self.config.max_bruchid_hole_diameter_mm,
            min_circularity=self.config.hole_circularity_min,
        )

    def analyze(
        self,
        seed_mask: np.ndarray,
        orig_img_bgr: np.ndarray,
        calib: CalibrationResult,
        qr_tag: Optional[str] = None,
    ) -> SeedScanResult:
        """Analyzes a seed scan sheet and extracts individual and batch metrics.
        
        Args:
            seed_mask: Clean binary mask of seed pixels.
            orig_img_bgr: Original color image (needed for color/gradient bruchid hole detection).
            calib: Calibration result.
            qr_tag: Tree QR code tag.
            
        Returns:
            SeedScanResult with full lot statistics.
        """
        # Separate touching seeds
        total_count, seed_cnts, _ = self.counter.separate_and_count(
            seed_mask=seed_mask,
            pixels_per_mm=calib.pixels_per_mm,
            enable_watershed=self.config.enable_watershed_separation,
        )

        seed_metrics_list: List[SingleSeedMetrics] = []
        attacked_count = 0

        for seed_id, cnt in enumerate(seed_cnts, start=1):
            metrics = self._measure_single_seed(
                cnt=cnt,
                full_mask=seed_mask,
                orig_bgr=orig_img_bgr,
                calib=calib,
                seed_id=seed_id,
            )
            if metrics.bruchid.is_attacked:
                attacked_count += 1
            seed_metrics_list.append(metrics)

        # Batch statistics
        if seed_metrics_list:
            areas = [s.projected_area_mm2 for s in seed_metrics_list]
            lengths = [s.length_mm for s in seed_metrics_list]
            widths = [s.width_mm for s in seed_metrics_list]
            eccs = [s.eccentricity for s in seed_metrics_list]
            circs = [s.circularity for s in seed_metrics_list]

            mean_area = float(np.mean(areas))
            std_area = float(np.std(areas))
            mean_len = float(np.mean(lengths))
            std_len = float(np.std(lengths))
            mean_wid = float(np.mean(widths))
            std_wid = float(np.std(widths))
            mean_ecc = float(np.mean(eccs))
            mean_circ = float(np.mean(circs))
            attack_rate = (attacked_count / len(seed_metrics_list)) * 100.0
        else:
            mean_area = std_area = mean_len = std_len = mean_wid = std_wid = mean_ecc = mean_circ = attack_rate = 0.0

        return SeedScanResult(
            qr_code_tag=qr_tag,
            total_seed_count=len(seed_metrics_list),
            mean_area_mm2=round(mean_area, 2),
            std_area_mm2=round(std_area, 2),
            mean_length_mm=round(mean_len, 2),
            std_length_mm=round(std_len, 2),
            mean_width_mm=round(mean_wid, 2),
            std_width_mm=round(std_wid, 2),
            mean_eccentricity=round(mean_ecc, 3),
            mean_circularity=round(mean_circ, 3),
            attacked_seed_count=attacked_count,
            bruchid_attack_rate_pct=round(attack_rate, 2),
            seeds=seed_metrics_list,
            scale_info=calib,
        )

    def _measure_single_seed(
        self,
        cnt: np.ndarray,
        full_mask: np.ndarray,
        orig_bgr: np.ndarray,
        calib: CalibrationResult,
        seed_id: int,
    ) -> SingleSeedMetrics:
        """Extracts metrics for one individual seed."""
        px_area = cv2.contourArea(cnt)
        area_mm2 = px_area * calib.mm2_per_pixel

        # Perimeter
        px_peri = cv2.arcLength(cnt, True)
        peri_mm = px_peri / calib.pixels_per_mm if calib.pixels_per_mm > 0 else 0.0

        # Minimum Area Rect for Length and Width
        rect = cv2.minAreaRect(cnt)
        (_, _), (rw, rh), _ = rect
        len_px = max(rw, rh)
        wid_px = min(rw, rh)

        length_mm = len_px / calib.pixels_per_mm if calib.pixels_per_mm > 0 else 0.0
        width_mm = wid_px / calib.pixels_per_mm if calib.pixels_per_mm > 0 else 0.0

        # Aspect ratio
        aspect_ratio = (length_mm / width_mm) if width_mm > 0 else 1.0

        # Eccentricity: e = sqrt(1 - (b/a)^2) where a = length/2, b = width/2
        if length_mm > 0 and width_mm <= length_mm:
            ratio = width_mm / length_mm
            eccentricity = math.sqrt(max(0.0, 1.0 - ratio**2))
        else:
            eccentricity = 0.0

        # Circularity: 4 * pi * Area / Perimeter^2
        if px_peri > 0:
            circularity = (4.0 * math.pi * px_area) / (px_peri**2)
            circularity = min(1.0, max(0.0, circularity))
        else:
            circularity = 0.0

        # Centroid
        m = cv2.moments(cnt)
        if m["m00"] != 0:
            cx = m["m10"] / m["m00"]
            cy = m["m01"] / m["m00"]
        else:
            bx, by, bw, bh = cv2.boundingRect(cnt)
            cx = bx + bw / 2.0
            cy = by + bh / 2.0

        # Bounding box & ROI crop
        bx, by, bw, bh = cv2.boundingRect(cnt)
        pad = 4
        h_img, w_img = orig_bgr.shape[:2]
        x1 = max(0, bx - pad)
        y1 = max(0, by - pad)
        x2 = min(w_img, bx + bw + pad)
        y2 = min(h_img, by + bh + pad)

        seed_roi_bgr = orig_bgr[y1:y2, x1:x2]
        shifted_cnt = cnt - np.array([x1, y1])
        seed_roi_mask = full_mask[y1:y2, x1:x2].copy()

        # Bruchid beetle emergence hole detection
        if self.config.enable_bruchid_detection:
            bruchid = self.bruchid_detector.inspect_seed(
                seed_contour=shifted_cnt,
                seed_roi_bgr=seed_roi_bgr,
                seed_roi_mask=seed_roi_mask,
                pixels_per_mm=calib.pixels_per_mm,
                mm2_per_pixel=calib.mm2_per_pixel,
            )
        else:
            bruchid = BruchidDetectionResult(is_attacked=False, hole_count=0)

        return SingleSeedMetrics(
            seed_id=seed_id,
            length_mm=round(length_mm, 2),
            width_mm=round(width_mm, 2),
            projected_area_mm2=round(area_mm2, 2),
            perimeter_mm=round(peri_mm, 2),
            circularity=round(circularity, 3),
            eccentricity=round(eccentricity, 3),
            aspect_ratio=round(aspect_ratio, 2),
            centroid_x=round(cx, 1),
            centroid_y=round(cy, 1),
            bounding_box=(bx, by, bw, bh),
            bruchid=bruchid,
            contour=cnt,
        )
