import pytest
from fastapi import status


def test_list_individuals(client, seed_ecological_data):
    response = client.get("/api/v1/individuals")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_get_individual_by_qr_code(client, seed_ecological_data):
    response = client.get("/api/v1/individuals/qr/QR-BAL-DOR-001")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["qr_code_tag"] == "QR-BAL-DOR-001"
    assert data["dbh_cm"] == 32.5
    assert data["health_status_score"] == 5


def test_get_individual_by_qr_code_not_found(client):
    response = client.get("/api/v1/individuals/qr/NON-EXISTENT-TAG")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_individual(client, operator_headers, seed_ecological_data):
    payload = {
        "plot_id": "BF-DOR-01",
        "taxon_id": "tax001",
        "qr_code_tag": "QR-NEW-TREE-999",
        "dbh_cm": 15.5,
        "total_height_m": 4.2,
        "crown_diameter_m": 3.1,
        "canopy_position": "Codominant",
        "health_status_score": 4,
        "geom_tree": {"type": "Point", "coordinates": [-0.0927, 14.0326]},
    }
    response = client.post("/api/v1/individuals", json=payload, headers=operator_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["qr_code_tag"] == "QR-NEW-TREE-999"
    assert data["health_status_score"] == 4


def test_create_individual_invalid_plot(client, operator_headers, seed_ecological_data):
    payload = {
        "plot_id": "INVALID-PLOT-ID",
        "taxon_id": "tax001",
        "qr_code_tag": "QR-FAIL",
        "health_status_score": 3,
        "geom_tree": "POINT(0 0)",
    }
    response = client.post("/api/v1/individuals", json=payload, headers=operator_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_individual(client, operator_headers, seed_ecological_data):
    payload = {"health_status_score": 3, "dbh_cm": 34.0}
    response = client.put("/api/v1/individuals/ind001", json=payload, headers=operator_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["health_status_score"] == 3
    assert data["dbh_cm"] == 34.0


def test_delete_individual(client, admin_headers, seed_ecological_data):
    # Create temp individual
    create_resp = client.post(
        "/api/v1/individuals",
        json={
            "plot_id": "BF-DOR-01",
            "taxon_id": "tax001",
            "qr_code_tag": "TEMP-DEL-IND",
            "health_status_score": 2,
            "geom_tree": "POINT(0 0)",
        },
        headers=admin_headers,
    )
    ind_id = create_resp.json()["ind_id"]

    del_resp = client.delete(f"/api/v1/individuals/{ind_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
