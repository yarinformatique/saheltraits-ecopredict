import pytest
from fastapi import status


def test_create_and_list_germination_trial(client, researcher_headers, seed_ecological_data):
    payload = {
        "ind_id": "ind001",
        "seed_batch_qr": "BATCH-BAL-2026-X",
        "temp_regime_c": "30/20",
        "osmotic_potential_mpa": -0.4,
        "pretreatment_type": "Scarification mécanique",
        "total_seeds": 100,
        "germinated_count": 75,
        "t50_days": 5.2,
    }
    response = client.post("/api/v1/germination", json=payload, headers=researcher_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["seed_batch_qr"] == "BATCH-BAL-2026-X"
    assert data["final_gp_pct"] == 75.0

    # Test listing
    list_resp = client.get("/api/v1/germination?seed_batch_qr=BATCH-BAL-2026-X")
    assert list_resp.status_code == status.HTTP_200_OK
    assert len(list_resp.json()) == 1


def test_create_germination_invalid_counts(client, researcher_headers, seed_ecological_data):
    payload = {
        "ind_id": "ind001",
        "seed_batch_qr": "BATCH-INVALID",
        "temp_regime_c": "30/20",
        "total_seeds": 50,
        "germinated_count": 60,  # Invalid: germinated > total
    }
    response = client.post("/api/v1/germination", json=payload, headers=researcher_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_germination_trial(client, researcher_headers, seed_ecological_data):
    create_resp = client.post(
        "/api/v1/germination",
        json={
            "ind_id": "ind001",
            "seed_batch_qr": "BATCH-UPDATE-TEST",
            "temp_regime_c": "35/25",
            "total_seeds": 100,
            "germinated_count": 50,
        },
        headers=researcher_headers,
    )
    germ_id = create_resp.json()["germ_id"]

    update_resp = client.put(
        f"/api/v1/germination/{germ_id}",
        json={"germinated_count": 80},
        headers=researcher_headers,
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["final_gp_pct"] == 80.0


def test_delete_germination_trial(client, admin_headers, seed_ecological_data):
    create_resp = client.post(
        "/api/v1/germination",
        json={
            "ind_id": "ind001",
            "seed_batch_qr": "BATCH-DELETE-TEST",
            "temp_regime_c": "35/25",
            "total_seeds": 50,
            "germinated_count": 25,
        },
        headers=admin_headers,
    )
    germ_id = create_resp.json()["germ_id"]

    del_resp = client.delete(f"/api/v1/germination/{germ_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
