"""
Compound leaf leaflet distinction and separation module.
Designed specifically for Sahelian compound-leaved trees:
- Parkia biglobosa (Néré)
- Vachellia tortilis / Vachellia nilotica (Acacias)
- Faidherbia albida (Gao)
- Tamarindus indica (Tamarinier)

Uses Euclidean Distance Transform and Marker-Controlled Watershed segmentation.
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.segmentation import watershed


class LeafletSeparator:
    """Separates touching or clustered leaflets in compound leaves and distinguishes rachis."""

    def __init__(
        self,
        min_distance_px: int = 10,
        min_leaflet_area_px: float = 30.0,
        rachis_aspect_ratio_min: float = 6.0,
    ):
        self.min_distance_px = min_distance_px
        self.min_leaflet_area_px = min_leaflet_area_px
        self.rachis_aspect_ratio_min = rachis_aspect_ratio_min

    def separate_leaflets(
        self,
        compound_mask: np.ndarray,
        rgb_img: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, List[np.ndarray], Optional[np.ndarray]]:
        """Segments compound leaf mask into individual leaflets and identifies the rachis.
        
        Args:
            compound_mask: Binary mask of the compound leaf.
            rgb_img: Optional color image for watershed boundaries.
            
        Returns:
            Tuple of:
            - labeled_mask: 2D array where each leaflet has a unique integer ID (0 = background).
            - leaflet_contours: List of contour arrays for each separated leaflet.
            - rachis_mask: Binary mask of detected rachis (or None if no rachis found).
        """
        # Ensure binary
        binary = (compound_mask > 0).astype(np.uint8) * 255

        # 1. Detect thin rachis if present (via morphological line detection / skeleton)
        rachis_mask, lamina_only = self._extract_rachis(binary)

        # 2. Compute Euclidean Distance Transform on leaflet lamina
        dist_transform = cv2.distanceTransform(lamina_only, cv2.DIST_L2, 5)

        if dist_transform.max() == 0:
            return np.zeros_like(compound_mask, dtype=np.int32), [], rachis_mask

        # 3. Detect local maxima (leaflet centers)
        coordinates = peak_local_max(
            dist_transform,
            min_distance=self.min_distance_px,
            labels=lamina_only,
            exclude_border=False,
        )

        # If very few peaks found, fallback to connected components
        if len(coordinates) == 0:
            num_labels, labels = cv2.connectedComponents(lamina_only)
            contours, _ = cv2.findContours(lamina_only, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return labels.astype(np.int32), contours, rachis_mask

        # 4. Generate watershed markers
        markers = np.zeros(dist_transform.shape, dtype=np.int32)
        for i, coord in enumerate(coordinates, start=1):
            markers[coord[0], coord[1]] = i

        # 5. Marker-controlled watershed
        # Invert distance so peaks become basins
        labels = watershed(-dist_transform, markers, mask=lamina_only)

        # 6. Extract individual leaflet contours & filter tiny fragments
        leaflet_contours = []
        final_labeled = np.zeros_like(labels, dtype=np.int32)
        current_id = 1

        for label_id in np.unique(labels):
            if label_id == 0:
                continue

            single_leaflet_mask = (labels == label_id).astype(np.uint8) * 255
            area = cv2.countNonZero(single_leaflet_mask)
            if area < self.min_leaflet_area_px:
                continue

            cnts, _ = cv2.findContours(single_leaflet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if cnts:
                best_cnt = max(cnts, key=cv2.contourArea)
                leaflet_contours.append(best_cnt)
                final_labeled[labels == label_id] = current_id
                current_id += 1

        return final_labeled, leaflet_contours, rachis_mask

    def _extract_rachis(self, binary_mask: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray]:
        """Distinguishes long thin central rachis from leaflets based on aspect ratio and skeleton."""
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_mask)
        rachis_mask = np.zeros_like(binary_mask)
        lamina_mask = binary_mask.copy()

        for i in range(1, num_labels):
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            aspect = max(w, h) / (min(w, h) + 1e-5)

            # A rachis typically has very high aspect ratio and occupies a large length across the leaf
            if aspect >= self.rachis_aspect_ratio_min and max(w, h) > 100:
                # Isolate this component
                comp_mask = (labels == i).astype(np.uint8) * 255
                # Verify thickness using distance transform: rachis is narrow throughout
                dist = cv2.distanceTransform(comp_mask, cv2.DIST_L2, 3)
                if dist.max() < 18:  # Narrow stem
                    rachis_mask = cv2.bitwise_or(rachis_mask, comp_mask)
                    lamina_mask[labels == i] = 0

        if cv2.countNonZero(rachis_mask) == 0:
            return None, binary_mask

        return rachis_mask, lamina_mask
