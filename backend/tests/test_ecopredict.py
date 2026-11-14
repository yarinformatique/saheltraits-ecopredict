"""
Tests du module EcoPredict (Simulateur Climatique & Aide à la décision).
"""

from fastapi.testclient import TestClient


def test_ecopredict_raster_metadata(client: TestClient):
    response = client.get("/api/v1/ecopredict/raster-metadata")
    assert response.status_code == 200
    data = response.json()
    assert "bounding_box" in data
    assert data["bounding_box"]["min_lat"] == 9.0
    assert len(data["available_variables"]) >= 4


def test_ecopredict_projections_list(client: TestClient):
    response = client.get("/api/v1/ecopredict/projections?scenario=ssp245&horizon=2050")
    assert response.status_code == 200
    data = response.json()
    assert "projections" in data
    assert len(data["projections"]) > 0
    sp_balanites = next((p for p in data["projections"] if "Balanites" in p["species"]), None)
    assert sp_balanites is not None
    assert sp_balanites["scenario"] == "ssp245"


def test_ecopredict_diagnose_point_sahel(client: TestClient):
    payload = {
        "latitude": 14.0325,
        "longitude": -0.0925,
        "horizon": "2050",
        "scenario": "ssp245"
    }
    response = client.post("/api/v1/ecopredict/diagnose-point", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["climate_diagnostic"]["zone"] == "Sahélienne"
    assert len(data["species_ranking"]) > 0
    assert data["summary"]["recommended_count"] > 0


def test_ecopredict_diagnose_polygon(client: TestClient):
    payload = {
        "site_name": "Périmètre de Reboisement Dori Nord",
        "coordinates": [
            [-0.095, 14.030],
            [-0.090, 14.030],
            [-0.090, 14.035],
            [-0.095, 14.035],
            [-0.095, 14.030]
        ],
        "horizon": "2080",
        "scenario": "ssp585"
    }
    response = client.post("/api/v1/ecopredict/diagnose-polygon", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["site_name"] == "Périmètre de Reboisement Dori Nord"
    assert "polygon_centroid" in data
    assert "species_ranking" in data
