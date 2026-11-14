"""
Integration tests for FastAPI Microservice Endpoints.
"""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from morpho_vision.api.main import app

client = TestClient(app)


def test_health_check_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "opencv_version" in data


def test_analyze_leaf_endpoint():
    leaf_path = Path(__file__).parent.parent / "data" / "samples" / "sample_leaf_scan.png"
    assert leaf_path.exists()

    resp = client.post("/api/v1/analyze/leaf", data={"image_path": str(leaf_path)})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["leaf_count"] == 3
    assert data["qr_code_tag"] == "BF-KDG-ACARAD-001"
    assert data["total_leaf_area_cm2"] > 0
    assert len(data["leaves"]) == 3
    assert data["processing_time_sec"] < 2.0


def test_analyze_seed_endpoint():
    seed_path = Path(__file__).parent.parent / "data" / "samples" / "sample_seed_scan.png"
    assert seed_path.exists()

    resp = client.post("/api/v1/analyze/seed", data={"image_path": str(seed_path)})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["total_seed_count"] == 30
    assert data["attacked_seed_count"] == 6
    assert abs(data["bruchid_attack_rate_pct"] - 20.0) < 1.0


def test_qc_image_serving():
    leaf_path = Path(__file__).parent.parent / "data" / "samples" / "sample_leaf_scan.png"
    resp = client.post("/api/v1/analyze/leaf", data={"image_path": str(leaf_path)})
    qc_overlay_path = resp.json().get("qc_overlay_path")
    assert qc_overlay_path is not None

    filename = Path(qc_overlay_path).name
    resp_img = client.get(f"/api/v1/qc-image/{filename}")
    assert resp_img.status_code == 200
    assert resp_img.headers["content-type"] == "image/jpeg"
