"""
Quality Control (QC) Visualizer module.
Generates green/red diagnostic overlay images for rapid operator verification:
- Green mask: Valid leaf/seed lamina
- Red mask: Detected herbivory gaps or bruchid emergence holes
- Cyan box: Calibration reference square
- Purple box: Scanned tree QR code
- Overlay banner: Metadata, scale, sample count, and summary metrics.
"""

from datetime import datetime
from typing import Optional, Tuple
import cv2
import numpy as np

from morpho_vision.leaf_analyzer.analyzer import LeafScanResult
from morpho_vision.seed_analyzer.morphometry import SeedScanResult


class QualityControlVisualizer:
    """Renders inspection overlays on original scanned images with SIMD acceleration."""

    @staticmethod
    def render_leaf_qc_image(
        orig_img_bgr: np.ndarray,
        result: LeafScanResult,
        qr_box: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        """Renders diagnostic overlay for leaf scan."""
        overlay = orig_img_bgr.copy()
        color_layer = np.zeros_like(overlay)

        # 1. Draw green masks for leaves and red for herbivory holes
        for leaf in result.leaves:
            cv2.drawContours(color_layer, [leaf.contour], -1, (0, 220, 0), -1)

            if leaf.herbivory.hole_contours:
                bx, by, bw, bh = leaf.bounding_box
                pad = 5
                x1 = max(0, bx - pad)
                y1 = max(0, by - pad)
                for hc in leaf.herbivory.hole_contours:
                    shifted_hc = hc + np.array([x1, y1])
                    cv2.drawContours(color_layer, [shifted_hc], -1, (0, 0, 255), -1)

        # Fast SIMD alpha blending
        cv2.addWeighted(color_layer, 0.35, overlay, 0.65, 0, overlay)

        # Draw crisp contours and bounding boxes
        font = cv2.FONT_HERSHEY_SIMPLEX
        for leaf in result.leaves:
            cv2.drawContours(overlay, [leaf.contour], -1, (0, 180, 0), 2)
            bx, by, bw, bh = leaf.bounding_box
            cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), (255, 200, 0), 1)

            label = f"L{leaf.leaf_id}: {leaf.area_cm2} cm2"
            if leaf.herbivory.herbivory_percentage > 0:
                label += f" (-{leaf.herbivory.herbivory_percentage}%)"
            
            (tw, th), _ = cv2.getTextSize(label, font, 0.5, 1)
            cv2.rectangle(overlay, (bx, max(0, by - 18)), (bx + tw + 6, max(0, by)), (0, 0, 0), -1)
            cv2.putText(overlay, label, (bx + 3, max(12, by - 4)), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # 2. Draw calibration marker box (Cyan)
        if result.scale_info and result.scale_info.marker_box:
            mx, my, mw, mh = result.scale_info.marker_box
            cv2.rectangle(overlay, (mx, my), (mx + mw, my + mh), (255, 255, 0), 3)
            marker_lbl = f"CALIBRATION: 4.0 cm2 ({result.scale_info.pixels_per_cm:.1f} px/cm)"
            cv2.putText(overlay, marker_lbl, (mx, max(20, my - 8)), font, 0.6, (255, 255, 0), 2, cv2.LINE_AA)

        # 3. Draw QR-code box (Magenta)
        if qr_box:
            qx, qy, qw, qh = qr_box
            cv2.rectangle(overlay, (qx, qy), (qx + qw, qy + qh), (255, 0, 255), 3)
            qr_lbl = f"QR: {result.qr_code_tag or 'DETECTED'}"
            cv2.putText(overlay, qr_lbl, (qx, max(20, qy - 8)), font, 0.6, (255, 0, 255), 2, cv2.LINE_AA)

        # 4. Header banner
        overlay = QualityControlVisualizer._add_header_banner(
            img=overlay,
            title="LEAF MORPHO-ANALYSIS QC OVERLAY",
            tag=result.qr_code_tag or "UNTAGGED",
            count_info=f"Leaf Count: {result.leaf_count}",
            metric_info=f"Total LA: {result.total_leaf_area_cm2} cm2 | Mean: {result.mean_leaf_area_cm2} cm2 | Herbivory: {result.mean_herbivory_pct}%",
            scale_info=f"Scale: {result.scale_info.pixels_per_cm:.1f} px/cm ({result.scale_info.method})",
        )

        return overlay

    @staticmethod
    def render_seed_qc_image(
        orig_img_bgr: np.ndarray,
        result: SeedScanResult,
        qr_box: Optional[Tuple[int, int, int, int]] = None,
    ) -> np.ndarray:
        """Renders diagnostic overlay for seed scan."""
        overlay = orig_img_bgr.copy()
        color_layer = np.zeros_like(overlay)

        for seed in result.seeds:
            color = (0, 0, 255) if seed.bruchid.is_attacked else (0, 220, 0)
            cv2.drawContours(color_layer, [seed.contour], -1, color, -1)

        cv2.addWeighted(color_layer, 0.35, overlay, 0.65, 0, overlay)

        font = cv2.FONT_HERSHEY_SIMPLEX
        for seed in result.seeds:
            cnt_color = (0, 0, 255) if seed.bruchid.is_attacked else (0, 180, 0)
            cv2.drawContours(overlay, [seed.contour], -1, cnt_color, 1)

            bx, by, bw, bh = seed.bounding_box
            if seed.bruchid.is_attacked:
                cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
                cv2.putText(overlay, f"S{seed.seed_id}: BRUCHID", (bx, max(12, by - 4)), font, 0.4, (0, 0, 255), 1)

        # Calibration marker
        if result.scale_info and result.scale_info.marker_box:
            mx, my, mw, mh = result.scale_info.marker_box
            cv2.rectangle(overlay, (mx, my), (mx + mw, my + mh), (255, 255, 0), 3)
            cv2.putText(overlay, "CALIBRATION (4 cm2)", (mx, max(20, my - 8)), font, 0.6, (255, 255, 0), 2)

        # QR code
        if qr_box:
            qx, qy, qw, qh = qr_box
            cv2.rectangle(overlay, (qx, qy), (qx + qw, qy + qh), (255, 0, 255), 3)
            cv2.putText(overlay, f"QR: {result.qr_code_tag or 'DETECTED'}", (qx, max(20, qy - 8)), font, 0.6, (255, 0, 255), 2)

        # Header banner
        overlay = QualityControlVisualizer._add_header_banner(
            img=overlay,
            title="SEED LOT MORPHO-ANALYSIS QC OVERLAY",
            tag=result.qr_code_tag or "UNTAGGED",
            count_info=f"Seed Count: {result.total_seed_count} seeds",
            metric_info=f"Mean Area: {result.mean_area_mm2} mm2 | Length: {result.mean_length_mm} mm | Bruchid Predation: {result.bruchid_attack_rate_pct}% ({result.attacked_seed_count} attacked)",
            scale_info=f"Scale: {result.scale_info.pixels_per_mm:.1f} px/mm ({result.scale_info.method})",
        )

        return overlay

    @staticmethod
    def _add_header_banner(
        img: np.ndarray,
        title: str,
        tag: str,
        count_info: str,
        metric_info: str,
        scale_info: str,
    ) -> np.ndarray:
        banner_h = 70
        banner = np.zeros((banner_h, img.shape[1], 3), dtype=np.uint8)
        banner[:] = (35, 30, 25)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(banner, f"{title} | TAG: {tag}", (15, 25), font, 0.65, (0, 230, 255), 2, cv2.LINE_AA)
        
        subtitle = f"{count_info} | {metric_info} | {scale_info}"
        cv2.putText(banner, subtitle, (15, 52), font, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        (ts_w, _), _ = cv2.getTextSize(timestamp_str, font, 0.45, 1)
        cv2.putText(banner, timestamp_str, (img.shape[1] - ts_w - 15, 25), font, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

        return np.vstack([banner, img])
