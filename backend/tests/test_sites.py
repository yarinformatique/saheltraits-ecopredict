import pytest
from fastapi import status


def test_list_plots(client, seed_ecological_data):
    response = client.get("/api/v1/sites")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    assert any(p["plot_id"] == "BF-DOR-01" for p in data)


def test_filter_plots_by_climatic_zone(client, seed_ecological_data):
    response = client.get("/api/v1/sites?climatic_zone=Sahélienne")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["climatic_zone"] == "Sahélienne"


def test_create_plot_success(client, researcher_headers):
    payload = {
        "plot_id": "BF-PO-01",
        "site_name": "Pô - Parc National",
        "climatic_zone": "Soudanienne",
        "geom": {"type": "Point", "coordinates": [-1.1575, 11.2425]},
        "elevation_m": 290.0,
        "slope_deg": 3.1,
        "protection_status": "Parc National",
        "fire_frequency_20yr": 12.0,
    }
    response = client.post("/api/v1/sites", json=payload, headers=researcher_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["plot_id"] == "BF-PO-01"
    assert data["climatic_zone"] == "Soudanienne"
    assert data["geom"]["type"] == "Point"


def test_create_plot_duplicate(client, researcher_headers, seed_ecological_data):
    payload = {
        "plot_id": "BF-DOR-01",
        "site_name": "Duplicate Plot",
        "climatic_zone": "Sahélienne",
        "geom": "POINT(-0.09 14.03)",
    }
    response = client.post("/api/v1/sites", json=payload, headers=researcher_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_plot_by_id(client, seed_ecological_data):
    response = client.get("/api/v1/sites/BF-DOR-01")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["site_name"] == "Dori - Yakouta"


def test_update_plot(client, researcher_headers, seed_ecological_data):
    payload = {"site_name": "Dori - Yakouta Mare Réserve"}
    response = client.put("/api/v1/sites/BF-DOR-01", json=payload, headers=researcher_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["site_name"] == "Dori - Yakouta Mare Réserve"


def test_delete_plot_admin_only(client, admin_headers, researcher_headers):
    # Create temp plot
    client.post(
        "/api/v1/sites",
        json={"plot_id": "TEMP-01", "site_name": "Temp", "climatic_zone": "Sahélienne", "geom": "POINT(0 0)"},
        headers=researcher_headers,
    )
    # Chercheur cannot delete
    del_resp_unauth = client.delete("/api/v1/sites/TEMP-01", headers=researcher_headers)
    assert del_resp_unauth.status_code == status.HTTP_403_FORBIDDEN

    # Admin can delete
    del_resp_admin = client.delete("/api/v1/sites/TEMP-01", headers=admin_headers)
    assert del_resp_admin.status_code == status.HTTP_204_NO_CONTENT
