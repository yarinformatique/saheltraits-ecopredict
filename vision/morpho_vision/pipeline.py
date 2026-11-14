"""
Unified image processing pipeline for LEAF & SEED MORPHO-ANALYZER.
Orchestrates QR code detection, scale calibration, segmentation, morphometrics,
QC overlay rendering, and export in a single fast, sub-2-second workflow.
"""

from pathlib import Path
import time
from typing import Optional, Tuple, Union
import cv2
import numpy as np

from morpho_vision.calibration.calibrator import ScaleCalibrator
from morpho_vision.calibration.reference import CalibrationResult
from morpho_vision.config import DEFAULT_CONFIG, MorphoVisionConfig
from morpho_vision.leaf_analyzer.analyzer import LeafMorphoAnalyzer, LeafScanResult
from morpho_vision.seed_analyzer.morphometry import SeedMorphoAnalyzer, SeedScanResult
from morpho_vision.segmentation.morphological import MorphologicalCleaner
from morpho_vision.segmentation.thresholding import AdaptiveThresholdSegmenter
from morpho_vision.traceability.exporter import DataExporter
from morpho_vision.traceability.qr_reader import QRCodeReader
from morpho_vision.traceability.visualizer import QualityControlVisualizer


class MorphoVisionPipeline:
    """High-throughput vision pipeline for high-resolution 600 DPI botanical scans."""

    def __init__(self, config: Optional[MorphoVisionConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.qr_reader = QRCodeReader(prefer_engine=self.config.traceability.qr_engine)
        self.calibrator = ScaleCalibrator(self.config.calibration)
        self.threshold_segmenter = AdaptiveThresholdSegmenter(
            background_type=self.config.segmentation.background_type
        )
        self.cleaner = MorphologicalCleaner(
            min_area_px=50.0,
        )
        self.leaf_analyzer = LeafMorphoAnalyzer(self.config.leaf)
        self.seed_analyzer = SeedMorphoAnalyzer(self.config.seed)
        self.visualizer = QualityControlVisualizer()
        self.exporter = DataExporter()

    def process_leaf_scan(
        self,
        image_input: Union[str, Path, np.ndarray],
        is_compound: bool = False,
        qr_tag_override: Optional[str] = None,
        save_qc_overlay: bool = True,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> Tuple[LeafScanResult, Optional[Path], float]:
        """Processes a leaf scan image through the complete pipeline in < 2 seconds."""
        start_time = time.perf_counter()
        img, source_stem = self._load_image(image_input)
        h, w = img.shape[:2]

        # 1. Detect QR code
        scanned_qr, qr_box = self.qr_reader.read_qr_code(img)
        final_qr = qr_tag_override or scanned_qr

        # 2. Calibration of spatial scale
        calib = self.calibrator.calibrate(img)

        # 3. High-speed multi-scale segmentation
        scale = 1.0
        if max(h, w) > 2200:
            scale = 2.0
            seg_img = cv2.resize(img, (int(w / scale), int(h / scale)), interpolation=cv2.INTER_AREA)
        else:
            seg_img = img

        exclude_boxes = []
        if calib.marker_box:
            bx, by, bw, bh = calib.marker_box
            exclude_boxes.append((int(bx / scale), int(by / scale), int(bw / scale), int(bh / scale)))
        if qr_box:
            qx, qy, qw, qh = qr_box
            exclude_boxes.append((int(qx / scale), int(qy / scale), int(qw / scale), int(qh / scale)))

        raw_mask = self.threshold_segmenter.segment_leaf(seg_img, exclude_boxes=exclude_boxes)
        clean_mask_small = self.cleaner.clean_mask(raw_mask)

        if scale > 1.0:
            clean_mask = cv2.resize(clean_mask_small, (w, h), interpolation=cv2.INTER_NEAREST)
        else:
            clean_mask = clean_mask_small

        # 4. Leaf Morphometric Extraction
        result = self.leaf_analyzer.analyze(
            leaf_mask=clean_mask,
            calib=calib,
            qr_tag=final_qr,
            is_compound=is_compound,
        )

        # 5. Visualizer QC Overlay
        overlay_path = None
        if save_qc_overlay:
            qc_img = self.visualizer.render_leaf_qc_image(img, result, qr_box=qr_box)
            out_folder = Path(output_dir) if output_dir else self.config.output_dir / "qc_overlays"
            out_folder.mkdir(parents=True, exist_ok=True)
            overlay_path = out_folder / f"{source_stem}_{final_qr or 'leaf'}_qc.jpg"

            if max(qc_img.shape[:2]) > 1800:
                s_disp = 1800.0 / max(qc_img.shape[:2])
                save_img = cv2.resize(qc_img, (int(qc_img.shape[1] * s_disp), int(qc_img.shape[0] * s_disp)), interpolation=cv2.INTER_AREA)
            else:
                save_img = qc_img
            cv2.imwrite(str(overlay_path), save_img, [cv2.IMWRITE_JPEG_QUALITY, 85])

        elapsed = time.perf_counter() - start_time
        return result, overlay_path, round(elapsed, 3)

    def process_seed_scan(
        self,
        image_input: Union[str, Path, np.ndarray],
        qr_tag_override: Optional[str] = None,
        save_qc_overlay: bool = True,
        output_dir: Optional[Union[str, Path]] = None,
    ) -> Tuple[SeedScanResult, Optional[Path], float]:
        """Processes a seed scan image through the complete pipeline in < 2 seconds."""
        start_time = time.perf_counter()
        img, source_stem = self._load_image(image_input)
        h, w = img.shape[:2]

        # 1. QR code
        scanned_qr, qr_box = self.qr_reader.read_qr_code(img)
        final_qr = qr_tag_override or scanned_qr

        # 2. Scale calibration
        calib = self.calibrator.calibrate(img)

        # 3. High-speed multi-scale segmentation
        scale = 1.0
        if max(h, w) > 2200:
            scale = 2.0
            seg_img = cv2.resize(img, (int(w / scale), int(h / scale)), interpolation=cv2.INTER_AREA)
        else:
            seg_img = img

        exclude_boxes = []
        if calib.marker_box:
            bx, by, bw, bh = calib.marker_box
            exclude_boxes.append((int(bx / scale), int(by / scale), int(bw / scale), int(bh / scale)))
        if qr_box:
            qx, qy, qw, qh = qr_box
            exclude_boxes.append((int(qx / scale), int(qy / scale), int(qw / scale), int(qh / scale)))

        raw_mask = self.threshold_segmenter.segment_seed(seg_img, exclude_boxes=exclude_boxes)
        min_px = (calib.pixels_per_mm / scale) ** 2
        clean_mask_small = self.cleaner.clean_mask(raw_mask, min_area_px=min_px)

        # Build scale-adjusted calibration for fast watershed on seg_img
        if scale > 1.0:
            scaled_calib = CalibrationResult(
                pixels_per_cm=calib.pixels_per_cm / scale,
                pixels_per_mm=calib.pixels_per_mm / scale,
                cm2_per_pixel=calib.cm2_per_pixel * (scale**2),
                mm2_per_pixel=calib.mm2_per_pixel * (scale**2),
                marker_detected=calib.marker_detected,
                marker_box=calib.marker_box,
                marker_contour=calib.marker_contour,
                marker_pixel_area=calib.marker_pixel_area / (scale**2),
                method=calib.method,
                dpi_equivalent=calib.dpi_equivalent,
            )
            # Analyze on scaled resolution (10x faster watershed)
            scaled_result = self.seed_analyzer.analyze(
                seed_mask=clean_mask_small,
                orig_img_bgr=seg_img,
                calib=scaled_calib,
                qr_tag=final_qr,
            )
            # Map contours and bounding boxes back to full image
            for seed in scaled_result.seeds:
                seed.contour = (seed.contour * scale).astype(np.int32)
                bx, by, bw, bh = seed.bounding_box
                seed.bounding_box = (int(bx * scale), int(by * scale), int(bw * scale), int(bh * scale))
                seed.centroid_x *= scale
                seed.centroid_y *= scale
            scaled_result.scale_info = calib
            result = scaled_result
        else:
            result = self.seed_analyzer.analyze(
                seed_mask=clean_mask_small,
                orig_img_bgr=img,
                calib=calib,
                qr_tag=final_qr,
            )

        # 5. Visualizer QC Overlay
        overlay_path = None
        if save_qc_overlay:
            qc_img = self.visualizer.render_seed_qc_image(img, result, qr_box=qr_box)
            out_folder = Path(output_dir) if output_dir else self.config.output_dir / "qc_overlays"
            out_folder.mkdir(parents=True, exist_ok=True)
            overlay_path = out_folder / f"{source_stem}_{final_qr or 'seed'}_qc.jpg"

            if max(qc_img.shape[:2]) > 1800:
                s_disp = 1800.0 / max(qc_img.shape[:2])
                save_img = cv2.resize(qc_img, (int(qc_img.shape[1] * s_disp), int(qc_img.shape[0] * s_disp)), interpolation=cv2.INTER_AREA)
            else:
                save_img = qc_img
            cv2.imwrite(str(overlay_path), save_img, [cv2.IMWRITE_JPEG_QUALITY, 85])

        elapsed = time.perf_counter() - start_time
        return result, overlay_path, round(elapsed, 3)

    def _load_image(
        self,
        image_input: Union[str, Path, np.ndarray],
    ) -> Tuple[np.ndarray, str]:
        if isinstance(image_input, (str, Path)):
            p = Path(image_input)
            stem = p.stem
            data = np.fromfile(str(p), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError(f"Unable to read or decode image file: {p}")
            return img, stem
        elif isinstance(image_input, np.ndarray):
            return image_input, f"scan_{int(time.time())}"
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")
