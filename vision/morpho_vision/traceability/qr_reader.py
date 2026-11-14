"""
QR-Code reading and traceability module with multi-scale acceleration.
Links scanned images directly to SahelTraits-DB tree records via qr_code_tag.
Employs fast downsampled ROI scanning + dual-engine decoding (pyzbar + cv2.QRCodeDetector).
"""

from typing import Optional, Tuple
import cv2
import numpy as np


class QRCodeReader:
    """Reads QR codes rapidly from sample scan sheets."""

    def __init__(self, prefer_engine: str = "dual"):
        self.prefer_engine = prefer_engine

    def read_qr_code(
        self,
        img_bgr: np.ndarray,
    ) -> Tuple[Optional[str], Optional[Tuple[int, int, int, int]]]:
        """Detects and decodes QR code with fast hierarchical downsampling.
        
        Args:
            img_bgr: Full resolution BGR image.
            
        Returns:
            Tuple of (qr_text, full_res_bbox_xywh) or (None, None).
        """
        h, w = img_bgr.shape[:2]

        # Optimization: Downscale huge scans (> 1200px) for ultra-fast QR decoding
        scale_factor = 1.0
        max_dim = max(h, w)
        if max_dim > 1400:
            scale_factor = max_dim / 1200.0
            small_img = cv2.resize(
                img_bgr,
                (int(w / scale_factor), int(h / scale_factor)),
                interpolation=cv2.INTER_AREA,
            )
        else:
            small_img = img_bgr

        # 1. Fast attempt with pyzbar on scaled image
        text, bbox = self._try_pyzbar(small_img)
        if text:
            full_bbox = self._scale_bbox(bbox, scale_factor)
            return text, full_bbox

        # 2. Fast attempt with cv2.QRCodeDetector on scaled image
        text, bbox = self._try_cv2(small_img)
        if text:
            full_bbox = self._scale_bbox(bbox, scale_factor)
            return text, full_bbox

        # 3. If not found on small image, try top 40% header ROI (where tags are normally located)
        header_h = int(h * 0.40)
        header_roi = img_bgr[0:header_h, :]
        text, bbox = self._try_pyzbar(header_roi)
        if text:
            return text, bbox

        # 4. Fallback to full resolution CLAHE contrast enhancement
        gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        text, bbox = self._try_pyzbar(enhanced)
        if text:
            full_bbox = self._scale_bbox(bbox, scale_factor)
            return text, full_bbox

        return None, None

    def _try_pyzbar(self, img: np.ndarray) -> Tuple[Optional[str], Optional[Tuple[int, int, int, int]]]:
        try:
            from pyzbar.pyzbar import decode
            decoded = decode(img)
            for d in decoded:
                if d.type in ["QRCODE", "QR_CODE"]:
                    text = d.data.decode("utf-8")
                    r = d.rect
                    return text, (r.left, r.top, r.width, r.height)
        except Exception:
            pass
        return None, None

    def _try_cv2(self, img: np.ndarray) -> Tuple[Optional[str], Optional[Tuple[int, int, int, int]]]:
        try:
            detector = cv2.QRCodeDetector()
            val, pts, _ = detector.detectAndDecode(img)
            if val and pts is not None:
                pts = pts[0].astype(int)
                x = int(np.min(pts[:, 0]))
                y = int(np.min(pts[:, 1]))
                w = int(np.max(pts[:, 0]) - x)
                h = int(np.max(pts[:, 1]) - y)
                return val, (x, y, w, h)
        except Exception:
            pass
        return None, None

    @staticmethod
    def _scale_bbox(
        bbox: Optional[Tuple[int, int, int, int]],
        scale: float,
    ) -> Optional[Tuple[int, int, int, int]]:
        if not bbox or scale == 1.0:
            return bbox
        x, y, w, h = bbox
        return (int(x * scale), int(y * scale), int(w * scale), int(h * scale))
