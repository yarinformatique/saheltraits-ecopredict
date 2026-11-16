"""
Tests unitaires et d'intégration pour le pipeline de vision Traits Lab :
Segmentation du limbe (ExG + Otsu + morphologie 5x5 + plus grand contour),
Détection de mires (Pièces 100 CFA / 50 CFA / Règle 50mm / Calibrage manuel tactile).
"""

import io
import cv2
import numpy as np
import pytest
from fastapi import status


def create_synthetic_leaf_and_coin_image(
    w=800, h=600, include_coin=True, coin_r=45, include_corner_noise=True
) -> bytes:
    """Génère une image synthétique avec fond clair, feuille verte, pièce et reflets parasites."""
    # Fond papier blanc/beige clair (245, 242, 238)
    img = np.full((h, w, 3), (238, 242, 245), dtype=np.uint8)

    # Bruit de fond / reflets dans les coins (doivent être éliminés par le filtre 0.5% et max contour)
    if include_corner_noise:
        # Petit reflet vert/jaune dans le coin supérieur gauche (moins de 0.2% de l'image)
        cv2.circle(img, (20, 20), 12, (50, 200, 100), -1)
        # Petit reflet dans le coin inférieur droit
        cv2.rectangle(img, (w - 30, h - 30), (w - 5, h - 5), (60, 180, 80), -1)

    # Dessin d'une feuille verte principale (centre 350, 300, axes 160x70, inclinée 30°)
    leaf_center = (350, 300)
    leaf_axes = (160, 75)
    cv2.ellipse(
        img,
        leaf_center,
        leaf_axes,
        angle=30,
        startAngle=0,
        endAngle=360,
        color=(34, 139, 34),  # Vert forêt BGR
        thickness=-1,
    )

    # Dessin de dentelures sur le contour foliaire pour tester la haute précision du détourage
    for deg in range(0, 360, 15):
        rad = np.radians(deg)
        x = int(leaf_center[0] + (leaf_axes[0] + 5) * np.cos(rad) * np.cos(np.radians(30)) - (leaf_axes[1] + 5) * np.sin(rad) * np.sin(np.radians(30)))
        y = int(leaf_center[1] + (leaf_axes[0] + 5) * np.cos(rad) * np.sin(np.radians(30)) + (leaf_axes[1] + 5) * np.sin(rad) * np.cos(np.radians(30)))
        cv2.circle(img, (x, y), 6, (40, 150, 40), -1)

    # Dessin de la pièce (mire circulaire sombre/métallique hors de la feuille)
    if include_coin:
        coin_center = (650, 200)
        # Cercle avec bord sombre contrasté
        cv2.circle(img, coin_center, coin_r, (110, 115, 120), -1)
        cv2.circle(img, coin_center, coin_r, (40, 45, 50), 3)

    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def test_leaf_scan_coin_100_detection(client, seed_ecological_data):
    """Vérifie la détection de la pièce 100 F CFA et l'élimination des reflets parasites de coin."""
    img_bytes = create_synthetic_leaf_and_coin_image(include_coin=True, coin_r=52)

    files = {"file": ("test_leaf.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    data = {"ref_type": "coin_100", "known_mm": "26.0"}

    response = client.post("/api/v1/traits/leaf-scan", files=files, data=data)
    assert response.status_code == status.HTTP_200_OK

    res = response.json()
    assert res["success"] is True
    assert res["leaf_detected"] is True
    assert res["target_detected"] is True
    assert res["calibration_mode"] == "CERTIFIED_TARGET"
    assert res["ref_type"] == "coin_100"
    assert res["known_mm"] == 26.0

    # Vérification métrique
    assert res["leaf_area_mm2"] > 0
    assert res["leaf_area_cm2"] == round(res["leaf_area_mm2"] / 100.0, 2)
    assert res["perimeter_mm"] > 0
    assert res["max_length_mm"] > res["max_width_mm"]
    assert "Mire validée : Pièce 100 F CFA" in res["status_message"]
    assert "processed_image_base64" in res
    assert res["processed_image_base64"].startswith("data:image/jpeg;base64,")


def test_leaf_scan_coin_50_detection(client, seed_ecological_data):
    """Vérifie la détection avec une pièce de 50 F CFA (22.0 mm)."""
    img_bytes = create_synthetic_leaf_and_coin_image(include_coin=True, coin_r=44)

    files = {"file": ("test_leaf.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    data = {"ref_type": "coin_50", "known_mm": "22.0"}

    response = client.post("/api/v1/traits/leaf-scan", files=files, data=data)
    assert response.status_code == status.HTTP_200_OK

    res = response.json()
    assert res["success"] is True
    assert res["target_detected"] is True
    assert res["known_mm"] == 22.0
    assert res["calibration_mode"] == "CERTIFIED_TARGET"


def test_leaf_scan_manual_tactile_calibration(client, seed_ecological_data):
    """Vérifie le calibrage manuel tactile de secours (Point A vers Point B sur règle 50 mm)."""
    img_bytes = create_synthetic_leaf_and_coin_image(include_coin=False)

    files = {"file": ("test_leaf.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    # Simule l'utilisateur qui a posé le Point A à (100, 500) et le Point B à (300, 500) sur 50 mm
    data = {
        "ref_type": "ruler_50mm",
        "known_mm": "50.0",
        "ptA_x": 100,
        "ptA_y": 500,
        "ptB_x": 300,
        "ptB_y": 500,
    }

    response = client.post("/api/v1/traits/leaf-scan", files=files, data=data)
    assert response.status_code == status.HTTP_200_OK

    res = response.json()
    assert res["success"] is True
    assert res["target_detected"] is True
    assert res["calibration_mode"] == "MANUAL_TACTILE"
    # distance = 200 px / 50 mm = 4.0 px/mm
    assert abs(res["pixels_per_mm"] - 4.0) < 0.05
    assert "Étalonnage manuel tactile appliqué" in res["status_message"]


def test_leaf_scan_target_missing_dynamic_message(client, seed_ecological_data):
    """Vérifie le message dynamique lorsque la mire sélectionnée n'est pas présente."""
    img_bytes = create_synthetic_leaf_and_coin_image(include_coin=False)

    files = {"file": ("test_leaf.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    data = {"ref_type": "coin_100"}

    response = client.post("/api/v1/traits/leaf-scan", files=files, data=data)
    assert response.status_code == status.HTTP_200_OK

    res = response.json()
    assert res["success"] is True
    assert res["leaf_detected"] is True
    assert res["target_detected"] is False
    assert res["calibration_mode"] == "DEFAULT_ESTIMATED"
    # Message dynamique sans mention en dur de carré noir 20x20
    assert "Pièce de 100 F CFA (26.0 mm) non détectée" in res["status_message"]
    assert "20×20 mm" not in res["status_message"]
