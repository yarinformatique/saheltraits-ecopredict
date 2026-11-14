"""
Seed separation and counting module.
Separates touching or clustered seeds on the scanner plate using Euclidean Distance Transform
and Watershed segmentation, ensuring accurate seed lot counting (e.g. 100 seeds per tree).
"""

from typing import List, Tuple
import cv2
import numpy as np
from skimage.feature import peak_local_max
from skimage.segmentation import watershed

from morpho_vision.segmentation.morphological import MorphologicalCleaner


class SeedCounter:
    """Handles seed separation and counting."""

    def __init__(
        self,
        min_seed_distance_mm: float = 3.5,
        min_seed_area_mm2: float = 1.0,
    ):
        self.min_seed_distance_mm = min_seed_distance_mm
        self.min_seed_area_mm2 = min_seed_area_mm2

    def separate_and_count(
        self,
        seed_mask: np.ndarray,
        pixels_per_mm: float,
        enable_watershed: bool = True,
    ) -> Tuple[int, List[np.ndarray], np.ndarray]:
        """Separates touching seeds and counts the lot.
        
        Args:
            seed_mask: Binary mask of seeds (255 = seeds, 0 = background).
            pixels_per_mm: Spatial resolution.
            enable_watershed: If True, uses distance transform + watershed to separate clusters.
            
        Returns:
            Tuple of:
            - total_count: Total number of identified seeds.
            - seed_contours: List of individual seed contours.
            - labeled_mask: 2D array of labeled seeds.
        """
        binary = (seed_mask > 0).astype(np.uint8) * 255
        min_area_px = self.min_seed_area_mm2 * (pixels_per_mm**2)

        if not enable_watershed:
            cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_cnts = [c for c in cnts if cv2.contourArea(c) >= min_area_px]
            labeled = np.zeros_like(binary, dtype=np.int32)
            for idx, c in enumerate(valid_cnts, start=1):
                cv2.drawContours(labeled, [c], -1, idx, -1)
            return len(valid_cnts), valid_cnts, labeled

        # Fill internal holes (e.g., bruchid exit holes) so that each seed has a single central peak
        filled_binary = MorphologicalCleaner.fill_holes(binary)

        # Compute Euclidean Distance Transform on solid seed silhouettes
        dist_transform = cv2.distanceTransform(filled_binary, cv2.DIST_L2, 5)

        if dist_transform.max() == 0:
            return 0, [], np.zeros_like(binary, dtype=np.int32)

        # Distance threshold in pixels
        min_dist_px = max(5, int(self.min_seed_distance_mm * pixels_per_mm * 1.5))

        # Local maxima detection (seed centroids)
        coordinates = peak_local_max(
            dist_transform,
            min_distance=min_dist_px,
            labels=filled_binary,
            exclude_border=False,
        )

        if len(coordinates) == 0:
            cnts, _ = cv2.findContours(filled_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_cnts = [c for c in cnts if cv2.contourArea(c) >= min_area_px]
            return len(valid_cnts), valid_cnts, binary.astype(np.int32)

        # Build markers
        markers = np.zeros(dist_transform.shape, dtype=np.int32)
        for i, coord in enumerate(coordinates, start=1):
            markers[coord[0], coord[1]] = i

        # Watershed segmentation on filled binary to separate silhouettes
        labels = watershed(-dist_transform, markers, mask=filled_binary)

        # Extract individual seed contours
        seed_contours: List[np.ndarray] = []
        final_labeled = np.zeros_like(labels, dtype=np.int32)
        current_id = 1

        for label_id in np.unique(labels):
            if label_id == 0:
                continue

            single_seed_mask = (labels == label_id).astype(np.uint8) * 255
            area = cv2.countNonZero(single_seed_mask)
            if area < min_area_px:
                continue

            cnts, _ = cv2.findContours(single_seed_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if cnts:
                best_cnt = max(cnts, key=cv2.contourArea)
                seed_contours.append(best_cnt)
                final_labeled[labels == label_id] = current_id
                current_id += 1

        # Spatial sorting: top-to-bottom, left-to-right
        seed_contours.sort(key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))

        return len(seed_contours), seed_contours, final_labeled
