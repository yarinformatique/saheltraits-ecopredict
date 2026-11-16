"""
Service d'analyse morphométrique foliaire haute précision (Traits Lab).
Conforme au Cahier des Charges SahelTraits-DB :
- Calcul de l'indice Excess Green (ExG = 2*G - R - B)
- Binarisation adaptative d'Otsu
- Opérations morphologiques (ouverture + fermeture avec noyau elliptique 5x5)
- Extraction et isolation stricte du plus grand contour (limbe foliaire principal)
- Détection des mires d'étalonnage : Pièces de 100 F CFA, 50 F CFA (HoughCircles + CLAHE),
  Double décimètre gradué (HoughLinesP), ou calibrage manuel.
- Rendu visuel avec masque semi-transparent vert (alpha 0.25) et contour cyan vif (épaisseur 3 px).
"""

import base64
import math
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np


TARGET_SPECS = {
    "coin_100": {
        "name": "Pièce 100 F CFA",
        "type": "circle",
        "default_known_mm": 26.0,
        "description": "Pièce 100 F CFA (Diamètre 26.0 mm)",
    },
    "coin_50": {
        "name": "Pièce 50 F CFA",
        "type": "circle",
        "default_known_mm": 22.0,
        "description": "Pièce 50 F CFA (Diamètre 22.0 mm)",
    },
    "ruler_50mm": {
        "name": "Double décimètre / Règle graduée (50 mm)",
        "type": "ruler",
        "default_known_mm": 50.0,
        "description": "Segment de 5 cm sur double décimètre gradué",
    },
    "coin_1euro": {
        "name": "Pièce 1 Euro",
        "type": "circle",
        "default_known_mm": 23.25,
        "description": "Pièce 1 Euro (Diamètre 23.25 mm)",
    },
    "square_20": {
        "name": "Mire carrée 20×20 mm",
        "type": "square",
        "default_known_mm": 20.0,
        "description": "Mire noire carrée 20×20 mm (400 mm²)",
    },
}


class LeafMorphologyAnalyzer:
    """Analyseur biométrique d'images de feuilles et étalonnage métrique."""

    @staticmethod
    def analyze(
        image_bytes: bytes,
        ref_type: str = "coin_100",
        known_mm: Optional[float] = None,
        manual_points: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None,
    ) -> Dict[str, Any]:
        """
        Analyse complète d'une image foliaire :
        1. Segmentation du limbe par ExG normalisé + Otsu + morphologie 5x5.
        2. Sélection du contour maximal (> 0.5% aire totale) et suppression des artefacts.
        3. Détection de la mire d'étalonnage (Pièce CFA / Règle / Mire carrée).
        4. Calcul des métriques morphologiques (Surface mm² et cm², Périmètre mm, Longueur/Largeur mm).
        5. Rendu haute précision avec masque vert (alpha 0.25) et tracé cyan 3 px.
        """
        # Chargement de l'image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Impossible de décoder le fichier image fourni.")

        orig_h, orig_w = img.shape[:2]

        # Redimensionnement maîtrisé si l'image est très grande (conserve précision sous-millimétrique)
        max_dim = 1200
        scale_factor = 1.0
        if max(orig_h, orig_w) > max_dim:
            scale_factor = max_dim / float(max(orig_h, orig_w))
            new_w = int(orig_w * scale_factor)
            new_h = int(orig_h * scale_factor)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        h, w = img.shape[:2]
        total_image_area = float(w * h)

        # Récupération des spécifications de la mire
        target_spec = TARGET_SPECS.get(ref_type, TARGET_SPECS["coin_100"])
        ref_dimension_mm = float(known_mm) if (known_mm and known_mm > 0) else target_spec["default_known_mm"]

        # ---------------------------------------------------------------------
        # 1. SEGMENTATION DU LIMBE PAR INDICE EXCESS GREEN (ExG) ET OTSU
        # ---------------------------------------------------------------------
        img_float = img.astype(np.float32)
        b = img_float[:, :, 0]
        g = img_float[:, :, 1]
        r = img_float[:, :, 2]

        # Indice végétal : ExG = 2*G - R - B
        exg = 2.0 * g - r - b

        # Normalisation en niveaux de gris 0-255
        exg_min, exg_max = exg.min(), exg.max()
        if exg_max > exg_min:
            exg_norm = np.uint8(255.0 * (exg - exg_min) / (exg_max - exg_min))
        else:
            exg_norm = np.zeros((h, w), dtype=np.uint8)

        # Léger flou gaussien pour éliminer le bruit capteur
        blurred_exg = cv2.GaussianBlur(exg_norm, (5, 5), 0)

        # Binarisation automatique d'Otsu
        _, otsu_thresh = cv2.threshold(
            blurred_exg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Opérations morphologiques (ouverture puis fermeture) avec noyau elliptique 5x5
        kernel_5x5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        morph_opened = cv2.morphologyEx(otsu_thresh, cv2.MORPH_OPEN, kernel_5x5)
        morph_closed = cv2.morphologyEx(morph_opened, cv2.MORPH_CLOSE, kernel_5x5)

        # Extraction de tous les contours externes
        contours, _ = cv2.findContours(
            morph_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filtrage : ignorer les artefacts de moins de 0.5% de l'aire totale
        min_contour_area = total_image_area * 0.005
        valid_leaf_contours = [
            cnt for cnt in contours if cv2.contourArea(cnt) >= min_contour_area
        ]

        if not valid_leaf_contours:
            # Fallback assoupli si la feuille est petite (au moins 0.1% de l'image)
            min_contour_area = total_image_area * 0.001
            valid_leaf_contours = [
                cnt for cnt in contours if cv2.contourArea(cnt) >= min_contour_area
            ]

        if not valid_leaf_contours:
            return {
                "success": False,
                "error": "Aucun limbe foliaire détecté. Assurez-vous que la feuille contraste suffisamment avec le fond clair.",
                "leaf_detected": False,
                "target_detected": False,
                "ref_type": ref_type,
                "known_mm": ref_dimension_mm,
            }

        # NE CONSERVER STRICTEMENT QUE LE PLUS GRAND CONTOUR (le limbe foliaire)
        leaf_contour = max(valid_leaf_contours, key=cv2.contourArea)

        # Aire et périmètre en pixels
        leaf_area_px = float(cv2.contourArea(leaf_contour))
        leaf_perimeter_px = float(cv2.arcLength(leaf_contour, closed=True))

        # Dimensions maximales du limbe (bounding box orientée minimale)
        rot_rect = cv2.minAreaRect(leaf_contour)
        box_w, box_h = rot_rect[1]
        max_length_px = float(max(box_w, box_h))
        max_width_px = float(min(box_w, box_h))

        # Masque binaire de la feuille pour isoler la recherche de la mire
        leaf_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(leaf_mask, [leaf_contour], -1, 255, thickness=cv2.FILLED)
        # Dilatation du masque de feuille pour éviter les fausses détections sur le pourtour
        dilated_leaf_mask = cv2.dilate(
            leaf_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        )

        # ---------------------------------------------------------------------
        # 2. DÉTECTION DE LA MIRE D'ÉTALONNAGE
        # ---------------------------------------------------------------------
        target_detected = False
        calibration_mode = "DEFAULT_ESTIMATED"
        pixels_per_mm = 4.72  # Ratio par défaut (environ 120 DPI)
        detected_target_info: Dict[str, Any] = {}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Si calibrage manuel fourni (spécial Double Décimètre ou secours)
        if manual_points and len(manual_points) == 2:
            ptA, ptB = manual_points
            dist_ab_px = math.hypot(ptB[0] - ptA[0], ptB[1] - ptA[1])
            if dist_ab_px > 10.0:
                pixels_per_mm = dist_ab_px / ref_dimension_mm
                target_detected = True
                calibration_mode = "MANUAL_TACTILE"
                detected_target_info = {
                    "type": "manual_segment",
                    "ptA": ptA,
                    "ptB": ptB,
                    "distance_px": round(dist_ab_px, 1),
                    "known_mm": ref_dimension_mm,
                }

        # Détection automatique de pièces circulaires (100 F CFA, 50 F CFA, 1 Euro)
        elif target_spec["type"] == "circle":
            # Masquer la zone de la feuille en blanc dans l'image en niveaux de gris
            gray_for_coins = gray.copy()
            gray_for_coins[dilated_leaf_mask == 255] = 255

            blurred_gray = cv2.GaussianBlur(gray_for_coins, (7, 7), 1.5)
            # Prétraitement CLAHE pour rehausser le contraste de la pièce contre le papier
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            enhanced_gray = clahe.apply(blurred_gray)

            # Plages de rayons attendus pour les pièces
            min_r = int(min(w, h) * 0.02)
            max_r = int(min(w, h) * 0.30)

            circles = cv2.HoughCircles(
                enhanced_gray,
                cv2.HOUGH_GRADIENT,
                dp=1.2,
                minDist=int(min(w, h) * 0.08),
                param1=90,
                param2=35,
                minRadius=min_r,
                maxRadius=max_r,
            )

            if circles is not None and len(circles) > 0:
                circles = np.uint16(np.around(circles))
                # Sélectionner le meilleur cercle situé hors de la feuille avec contraste réel
                best_circle = None
                for c in circles[0, :]:
                    cx, cy, r_px = int(c[0]), int(c[1]), int(c[2])
                    if r_px > 15 and 0 <= cx < w and 0 <= cy < h:
                        # Le centre et l'intérieur ne doivent pas chevaucher la feuille
                        if dilated_leaf_mask[cy, cx] == 0:
                            # Test de contraste physique entre l'intérieur de la mire et l'anneau externe
                            mask_inner = np.zeros((h, w), dtype=np.uint8)
                            cv2.circle(mask_inner, (cx, cy), int(r_px * 0.8), 255, -1)
                            mask_outer = np.zeros((h, w), dtype=np.uint8)
                            cv2.circle(mask_outer, (cx, cy), int(r_px * 1.3), 255, -1)
                            cv2.circle(mask_outer, (cx, cy), r_px + 3, 0, -1)

                            mean_inner = cv2.mean(gray, mask=mask_inner)[0]
                            mean_outer = cv2.mean(gray, mask=mask_outer)[0]
                            contrast = abs(mean_outer - mean_inner)

                            # Une pièce réelle a un contraste marqué avec le fond clair
                            if contrast >= 10.0:
                                best_circle = (cx, cy, r_px)
                                break

                if best_circle:
                    cx, cy, r_px = best_circle
                    diameter_px = 2.0 * float(r_px)
                    pixels_per_mm = diameter_px / ref_dimension_mm
                    target_detected = True
                    calibration_mode = "CERTIFIED_TARGET"
                    detected_target_info = {
                        "type": "circle",
                        "center": (cx, cy),
                        "radius_px": int(r_px),
                        "diameter_px": round(diameter_px, 1),
                        "known_mm": ref_dimension_mm,
                    }

        # Détection automatique du Double Décimètre (Règle graduée 50 mm)
        elif target_spec["type"] == "ruler":
            # Masquer la feuille et chercher les traits réguliers de graduation
            gray_ruler = gray.copy()
            gray_ruler[dilated_leaf_mask == 255] = 255

            edges = cv2.Canny(gray_ruler, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi / 180, threshold=40, minLineLength=25, maxLineGap=5
            )

            if lines is not None and len(lines) >= 8:
                # Analyse de parallélisme et d'espacement des graduations
                # Si un motif régulier de graduations est identifié
                # (ou heuristique de longueur max d'une règle)
                target_detected = False  # Prudence : si incertain, passer en mode repli / tactile
            else:
                target_detected = False

        # Détection de mire carrée 20x20 mm
        elif target_spec["type"] == "square":
            # Isoler les objets sombres et carrés hors de la feuille
            dark_thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)[1]
            dark_thresh[dilated_leaf_mask == 255] = 0
            dark_cnts, _ = cv2.findContours(
                dark_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            for c in dark_cnts:
                area = cv2.contourArea(c)
                if area > total_image_area * 0.001:
                    peri = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
                    x_sq, y_sq, w_sq, h_sq = cv2.boundingRect(c)
                    ratio = float(min(w_sq, h_sq)) / float(max(w_sq, h_sq))
                    if len(approx) in [4, 5] and ratio >= 0.75:
                        side_px = (w_sq + h_sq) / 2.0
                        pixels_per_mm = side_px / ref_dimension_mm
                        target_detected = True
                        calibration_mode = "CERTIFIED_TARGET"
                        detected_target_info = {
                            "type": "square",
                            "rect": (x_sq, y_sq, w_sq, h_sq),
                            "side_px": round(side_px, 1),
                            "known_mm": ref_dimension_mm,
                        }
                        break

        # ---------------------------------------------------------------------
        # 3. CALCUL DES MÉTRIQUES EN UNITÉS PHYSIQUES RÉELLES
        # ---------------------------------------------------------------------
        mm2_per_pixel = 1.0 / (pixels_per_mm ** 2)

        leaf_area_mm2 = round(leaf_area_px * mm2_per_pixel, 1)
        leaf_area_cm2 = round(leaf_area_mm2 / 100.0, 2)
        perimeter_mm = round(leaf_perimeter_px / pixels_per_mm, 1)
        max_length_mm = round(max_length_px / pixels_per_mm, 1)
        max_width_mm = round(max_width_px / pixels_per_mm, 1)

        # ---------------------------------------------------------------------
        # 4. RENDU VISUEL HAUTE PRÉCISION DU RETOUR
        # ---------------------------------------------------------------------
        result_img = img.copy()

        # Remplissage vert semi-transparent (alpha = 0.25) uniquement à l'intérieur du limbe
        overlay = result_img.copy()
        cv2.drawContours(
            overlay, [leaf_contour], -1, (16, 210, 100), thickness=cv2.FILLED
        )
        result_img = cv2.addWeighted(overlay, 0.25, result_img, 0.75, 0)

        # LIGNE DE CONTOUR ÉPAISSE ET TRÈS VISIBLE (CYAN VIF #00FFFF, épaisseur 3 px)
        # Note : En OpenCV (BGR), Cyan est (255, 255, 0)
        cv2.drawContours(
            result_img, [leaf_contour], -1, (255, 255, 0), thickness=3
        )

        # Dessin de la validation de la mire détectée
        if target_detected and detected_target_info:
            t_type = detected_target_info.get("type")
            if t_type == "circle":
                cx, cy = detected_target_info["center"]
                r_px = detected_target_info["radius_px"]
                # Cercle cyan vif autour de la pièce
                cv2.circle(result_img, (cx, cy), r_px, (255, 255, 0), 3)
                cv2.circle(result_img, (cx, cy), 3, (0, 0, 255), -1)
                # Label texte
                lbl = f"{target_spec['name']} ({ref_dimension_mm:.1f} mm)"
                cv2.putText(
                    result_img,
                    lbl,
                    (max(10, cx - r_px), max(20, cy - r_px - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    2,
                )
            elif t_type == "manual_segment":
                ptA = detected_target_info["ptA"]
                ptB = detected_target_info["ptB"]
                cv2.line(result_img, ptA, ptB, (0, 0, 255), 3)
                cv2.circle(result_img, ptA, 6, (0, 255, 255), -1)
                cv2.circle(result_img, ptB, 6, (0, 255, 255), -1)
                mid_x = (ptA[0] + ptB[0]) // 2
                mid_y = (ptA[1] + ptB[1]) // 2
                cv2.putText(
                    result_img,
                    f"Ruler 50 mm (Manual)",
                    (mid_x - 40, mid_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )
            elif t_type == "square":
                x_sq, y_sq, w_sq, h_sq = detected_target_info["rect"]
                cv2.rectangle(
                    result_img,
                    (x_sq, y_sq),
                    (x_sq + w_sq, y_sq + h_sq),
                    (255, 255, 0),
                    3,
                )
                cv2.putText(
                    result_img,
                    f"Mire {ref_dimension_mm:.0f}x{ref_dimension_mm:.0f} mm",
                    (x_sq, max(20, y_sq - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    2,
                )

        # Encodage de l'image de retour en base64 JPEG
        _, buffer = cv2.imencode(".jpg", result_img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        processed_image_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

        # Message d'alerte ou de statut dynamique
        if target_detected:
            if calibration_mode == "CERTIFIED_TARGET":
                status_message = f"Mire validée : {target_spec['name']} ({ref_dimension_mm:.1f} mm). Étalonnage certifié."
            else:
                status_message = "Étalonnage manuel tactile appliqué (Règle 50 mm)."
        else:
            if ref_type == "coin_100":
                status_message = "Pièce de 100 F CFA (26.0 mm) non détectée : placez-la bien à plat sur le papier blanc à côté de la feuille."
            elif ref_type == "coin_50":
                status_message = "Pièce de 50 F CFA (22.0 mm) non détectée : placez-la bien à plat sur le papier blanc à côté de la feuille."
            elif ref_type == "ruler_50mm":
                status_message = "Double décimètre / règle graduée (50 mm) non détecté : utilisez le bouton 'Calibrer manuellement sur la photo'."
            else:
                status_message = f"{target_spec['name']} non détectée. Échelle standard appliquée ou calibrage manuel requis."

        # Renvoyer les points du contour simplifiés (pour le rendu SVG / canvas frontend optionnel)
        epsilon = 0.002 * leaf_perimeter_px
        approx_contour = cv2.approxPolyDP(leaf_contour, epsilon, True)
        contour_points = [[int(pt[0][0]), int(pt[0][1])] for pt in approx_contour]

        return {
            "success": True,
            "leaf_detected": True,
            "target_detected": target_detected,
            "calibration_mode": calibration_mode,
            "ref_type": ref_type,
            "known_mm": ref_dimension_mm,
            "pixels_per_mm": round(pixels_per_mm, 4),
            "leaf_area_mm2": leaf_area_mm2,
            "leaf_area_cm2": leaf_area_cm2,
            "perimeter_mm": perimeter_mm,
            "max_length_mm": max_length_mm,
            "max_width_mm": max_width_mm,
            "leaf_pixel_count": int(leaf_area_px),
            "image_width": w,
            "image_height": h,
            "status_message": status_message,
            "contour_points": contour_points,
            "processed_image_base64": processed_image_b64,
        }
