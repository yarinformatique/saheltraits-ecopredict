import pytest
from fastapi import status


def test_create_and_list_soil_record(client, researcher_headers, seed_ecological_data):
    payload = {
        "plot_id": "BF-DOR-01",
        "depth_cm": "0-20",
        "clay_pct": 14.5,
        "silt_pct": 20.0,
        "sand_pct": 65.5,
        "ph_h2o": 6.8,
        "organic_carbon_gkg": 4.5,
        "total_n_gkg": 0.38,
        "avail_p_mgkg": 7.2,
        "cec_cmolkg": 5.8,
        "dry_season_moisture_pct": 2.2,
    }
    response = client.post("/api/v1/environment/soil", json=payload, headers=researcher_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["depth_cm"] == "0-20"
    assert data["ph_h2o"] == 6.8

    # List soil records
    list_resp = client.get("/api/v1/environment/soil?plot_id=BF-DOR-01")
    assert list_resp.status_code == status.HTTP_200_OK
    assert len(list_resp.json()) >= 1


def test_update_soil_record(client, researcher_headers, seed_ecological_data):
    create_resp = client.post(
        "/api/v1/environment/soil",
        json={"plot_id": "BF-DOR-01", "depth_cm": "20-40", "ph_h2o": 7.0},
        headers=researcher_headers,
    )
    env_id = create_resp.json()["env_id"]

    update_resp = client.put(
        f"/api/v1/environment/soil/{env_id}",
        json={"ph_h2o": 7.2},
        headers=researcher_headers,
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["ph_h2o"] == 7.2


def test_delete_soil_record(client, admin_headers, seed_ecological_data):
    create_resp = client.post(
        "/api/v1/environment/soil",
        json={"plot_id": "BF-DOR-01", "depth_cm": "40-60", "ph_h2o": 7.5},
        headers=admin_headers,
    )
    env_id = create_resp.json()["env_id"]

    del_resp = client.delete(f"/api/v1/environment/soil/{env_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
