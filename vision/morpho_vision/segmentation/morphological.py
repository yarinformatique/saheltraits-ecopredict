"""
Morphological cleaning, noise suppression, and petiole handling module.
Removes scanner glass dust, scanner lid artifacts, and enables optional petiole clipping.
"""

from typing import Optional, Tuple
import cv2
import numpy as np


class MorphologicalCleaner:
    """Cleans binary masks with mathematical morphology and component filtering."""

    def __init__(
        self,
        min_area_px: float = 50.0,
        closing_kernel_size: int = 5,
        opening_kernel_size: int = 3,
    ):
        self.min_area_px = min_area_px
        self.closing_kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (closing_kernel_size, closing_kernel_size)
        )
        self.opening_kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (opening_kernel_size, opening_kernel_size)
        )

    def clean_mask(
        self,
        mask: np.ndarray,
        min_area_px: Optional[float] = None,
        close_holes: bool = False,
    ) -> np.ndarray:
        """Removes dust particles and small noise components.
        
        Args:
            mask: Binary mask (0 or 255).
            min_area_px: Minimum component area to keep.
            close_holes: If True, fills internal holes.
            
        Returns:
            Cleaned binary mask.
        """
        threshold_area = min_area_px if min_area_px is not None else self.min_area_px

        # Morphological opening to detach tiny filaments / dust
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.opening_kernel)

        # Connected component analysis for fast size filtering
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)

        cleaned = np.zeros_like(mask)
        for i in range(1, num_labels):  # Skip background label 0
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= threshold_area:
                cleaned[labels == i] = 255

        # Border artifact removal: remove components directly touching the outer 2 pixels of image
        h, w = mask.shape
        cv2.rectangle(cleaned, (0, 0), (w - 1, h - 1), 0, 2)

        if close_holes:
            cleaned = self.fill_holes(cleaned)

        return cleaned

    @staticmethod
    def fill_holes(mask: np.ndarray) -> np.ndarray:
        """Fills all internal enclosed holes in a binary mask using floodFill."""
        h, w = mask.shape
        flood_fill_mask = np.zeros((h + 2, w + 2), np.uint8)
        filled = mask.copy()
        cv2.floodFill(filled, flood_fill_mask, (0, 0), 255)
        # Invert flooded image to isolate holes
        inv_flooded = cv2.bitwise_not(filled)
        # Combine original with filled holes
        return cv2.bitwise_or(mask, inv_flooded)

    def separate_petiole(
        self,
        leaf_mask: np.ndarray,
        petiole_width_px: int = 15,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Separates the narrow petiole from the broad leaf lamina.
        Uses morphological opening with a kernel larger than the petiole width.
        
        Returns:
            Tuple of (lamina_mask, petiole_mask).
        """
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (petiole_width_px, petiole_width_px)
        )
        lamina = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, kernel)
        petiole = cv2.bitwise_and(leaf_mask, cv2.bitwise_not(lamina))
        return lamina, petiole
