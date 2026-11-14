"""
Adaptive and hybrid thresholding module for scanner images.
Handles white/blue background separation, Otsu thresholding, and shadow suppression.
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np

from morpho_vision.segmentation.color_spaces import ColorSpaceTransformer


class AdaptiveThresholdSegmenter:
    """Performs adaptive and hybrid thresholding to isolate plant organs."""

    def __init__(self, background_type: str = "white"):
        self.background_type = background_type.lower()
        self.color_trans = ColorSpaceTransformer()

    def segment_leaf(
        self,
        img_bgr: np.ndarray,
        exclude_boxes: Optional[List[Tuple[int, int, int, int]]] = None,
    ) -> np.ndarray:
        """Segments leaf tissue using a hybrid Excess Green + CIELAB + Otsu pipeline.
        
        Args:
            img_bgr: BGR input image.
            exclude_boxes: List of (x, y, w, h) bounding boxes to blank out (e.g. marker, QR code).
            
        Returns:
            Binary mask (uint8, 0 or 255) of clean leaf tissue.
        """
        # 1. Excess Green Index
        exg = self.color_trans.excess_green_index(img_bgr)

        # 2. CIELAB Greenness: in Lab, green corresponds to lower 'a*' channel
        l, a, b = self.color_trans.get_cielab_channels(img_bgr)
        # Invert 'a*' so green becomes bright
        a_green = cv2.bitwise_not(a)

        # 3. Combine ExG and a_green for high-contrast vegetation map
        veg_map = cv2.addWeighted(exg, 0.6, a_green, 0.4, 0)

        # 4. Otsu thresholding on vegetation map
        blurred = cv2.GaussianBlur(veg_map, (5, 5), 0)
        _, binary_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 5. Suppress scanner shadows:
        # Shadows on white scanner platen have high L* (> 180) and low ExG
        shadow_mask = (l > 170) & (exg < 15)
        binary_mask[shadow_mask] = 0

        # 6. Blank out excluded regions (marker, QR code, etc.)
        if exclude_boxes:
            for bx, by, bw, bh in exclude_boxes:
                # Add small padding around exclusion boxes
                pad = 4
                x1 = max(0, bx - pad)
                y1 = max(0, by - pad)
                x2 = min(img_bgr.shape[1], bx + bw + pad)
                y2 = min(img_bgr.shape[0], by + bh + pad)
                binary_mask[y1:y2, x1:x2] = 0

        return binary_mask

    def segment_seed(
        self,
        img_bgr: np.ndarray,
        exclude_boxes: Optional[List[Tuple[int, int, int, int]]] = None,
    ) -> np.ndarray:
        """Segments seeds on either white scanner bed or blue contrasting tray."""
        if self.background_type == "blue":
            binary_mask = self.color_trans.extract_seed_mask_from_blue_bg(img_bgr)
        else:
            # White background
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            # Invert grayscale so dark seeds become bright
            inv_gray = cv2.bitwise_not(gray)
            blurred = cv2.GaussianBlur(inv_gray, (5, 5), 0)
            _, binary_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Blank out excluded regions (marker, QR code)
        if exclude_boxes:
            for bx, by, bw, bh in exclude_boxes:
                pad = 4
                x1 = max(0, bx - pad)
                y1 = max(0, by - pad)
                x2 = min(img_bgr.shape[1], bx + bw + pad)
                y2 = min(img_bgr.shape[0], by + bh + pad)
                binary_mask[y1:y2, x1:x2] = 0

        return binary_mask
