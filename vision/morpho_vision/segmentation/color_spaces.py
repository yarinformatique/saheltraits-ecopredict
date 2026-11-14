"""
Color space conversions and vegetation indices for leaf and seed isolation.
Supports BGR, HSV, CIELAB and Excess Green (ExG) representations.
"""

from typing import Tuple
import cv2
import numpy as np


class ColorSpaceTransformer:
    """Provides color space conversions and plant-specific spectral indices."""

    @staticmethod
    def excess_green_index(img_bgr: np.ndarray) -> np.ndarray:
        """Computes Normalized Excess Green Index (ExG = 2*G - R - B).
        Ideal for separating green plant tissues from white, gray, or dark scanner plates.
        """
        b = img_bgr[:, :, 0].astype(np.float32)
        g = img_bgr[:, :, 1].astype(np.float32)
        r = img_bgr[:, :, 2].astype(np.float32)

        exg = 2.0 * g - r - b
        # Clip to 0-255 range
        exg_norm = np.clip(exg, 0, 255).astype(np.uint8)
        return exg_norm

    @staticmethod
    def get_cielab_channels(img_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Converts to CIELAB and returns (L, a, b) channels.
        In OpenCV:
        - L*: 0-255 (Lightness)
        - a*: 0-255 (Green at low values < 128, Red at high values > 128)
        - b*: 0-255 (Blue at low values < 128, Yellow at high values > 128)
        """
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        return l, a, b

    @staticmethod
    def get_hsv_channels(img_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Converts to HSV and returns (H, S, V) channels."""
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        return h, s, v

    @staticmethod
    def extract_green_mask(img_bgr: np.ndarray) -> np.ndarray:
        """Robust leaf green mask combining HSV and CIELAB green thresholds."""
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)

        # HSV green: Hue 25-95, Saturation > 25, Value > 25
        lower_green_hsv = np.array([25, 25, 25], dtype=np.uint8)
        upper_green_hsv = np.array([95, 255, 255], dtype=np.uint8)
        mask_hsv = cv2.inRange(hsv, lower_green_hsv, upper_green_hsv)

        # CIELAB green: a* < 125 (green axis)
        _, a_chan, _ = cv2.split(lab)
        _, mask_lab = cv2.threshold(a_chan, 125, 255, cv2.THRESH_BINARY_INV)

        # Logical OR for broad capture + refine
        mask_green = cv2.bitwise_or(mask_hsv, mask_lab)
        return mask_green

    @staticmethod
    def extract_seed_mask_from_white_bg(img_bgr: np.ndarray) -> np.ndarray:
        """Segments seeds on standard white scanner background.
        Seeds are typically brown, black, beige, or red-brown, contrasting strongly with white.
        """
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        # Invert so seeds become bright foreground
        inv_gray = cv2.bitwise_not(gray)
        # Otsu thresholding
        _, mask = cv2.threshold(inv_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return mask

    @staticmethod
    def extract_seed_mask_from_blue_bg(img_bgr: np.ndarray) -> np.ndarray:
        """Segments seeds placed on a high-contrast blue background tray."""
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # Blue background: Hue 95-135, Saturation > 60
        lower_blue = np.array([95, 60, 40], dtype=np.uint8)
        upper_blue = np.array([135, 255, 255], dtype=np.uint8)
        blue_bg_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # Seeds are NOT blue background
        seeds_mask = cv2.bitwise_not(blue_bg_mask)
        return seeds_mask
