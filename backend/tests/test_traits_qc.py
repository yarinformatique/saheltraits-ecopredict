import pytest
from fastapi import status


def test_list_trait_measurements(client, seed_ecological_data):
    response = client.get("/api/v1/traits/measurements")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 6


def test_create_normal_trait_measurement_valid(client, operator_headers, seed_ecological_data):
    # Balanites SLA historical mean ~ 10.0, std ~ 0.18. Normal value 10.05
    payload = {
        "ind_id": "ind001",
        "trait_name_ets": "SLA",
        "trait_value": 10.05,
        "unit": "mm2/mg",
        "organ_sampled": "Feuille",
        "measurement_protocol": "Standard ETS protocol",
    }
    response = client.post("/api/v1/traits/measurements", json=payload, headers=operator_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["qc_flag"] == "VALID"
    assert "Conforme" in data["qc_notes"]


def test_create_outlier_trait_measurement_flagged_3sigma(client, operator_headers, seed_ecological_data):
    # Historical mean ~ 10.0, std ~ 0.18. Value 25.0 is drastically > 3 sigmas!
    payload = {
        "ind_id": "ind001",
        "trait_name_ets": "SLA",
        "trait_value": 25.0,
        "unit": "mm2/mg",
        "organ_sampled": "Feuille",
        "measurement_protocol": "Standard ETS protocol",
    }
    response = client.post("/api/v1/traits/measurements", json=payload, headers=operator_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["qc_flag"] == "SUSPECT_OUTLIER_3SIGMA"
    assert "VALEUR ABERRANTE DETECTEE (3-SIGMA)" in data["qc_notes"]
    assert "z-score=" in data["qc_notes"]


def test_review_measurement_qc_by_researcher(client, researcher_headers, seed_ecological_data):
    # Create outlier first
    create_resp = client.post(
        "/api/v1/traits/measurements",
        json={
            "ind_id": "ind001",
            "trait_name_ets": "SLA",
            "trait_value": 28.5,
            "unit": "mm2/mg",
            "organ_sampled": "Feuille",
        },
        headers=researcher_headers,
    )
    meas_id = create_resp.json()["meas_id"]
    assert create_resp.json()["qc_flag"] == "SUSPECT_OUTLIER_3SIGMA"

    # Researcher manually approves the extreme value with scientific justification
    qc_payload = {
        "qc_flag": "MANUALLY_APPROVED",
        "qc_notes": "Feuille ombragée atypique prélevée en sommet de houppier, mesure vérifiée.",
    }
    review_resp = client.put(f"/api/v1/traits/measurements/{meas_id}/qc", json=qc_payload, headers=researcher_headers)
    assert review_resp.status_code == status.HTTP_200_OK
    reviewed_data = review_resp.json()
    assert reviewed_data["qc_flag"] == "MANUALLY_APPROVED"
    assert "[Arbitrage par Chercheur Test" in reviewed_data["qc_notes"]


def test_update_trait_measurement_triggers_qc_reevaluation(client, researcher_headers, seed_ecological_data):
    # Create valid measurement
    create_resp = client.post(
        "/api/v1/traits/measurements",
        json={
            "ind_id": "ind001",
            "trait_name_ets": "SLA",
            "trait_value": 9.95,
            "unit": "mm2/mg",
            "organ_sampled": "Feuille",
        },
        headers=researcher_headers,
    )
    meas_id = create_resp.json()["meas_id"]
    assert create_resp.json()["qc_flag"] == "VALID"

    # Update value to an outlier
    update_resp = client.put(
        f"/api/v1/traits/measurements/{meas_id}",
        json={"trait_value": 45.0},
        headers=researcher_headers,
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["qc_flag"] == "SUSPECT_OUTLIER_3SIGMA"


def test_traits_statistics(client, seed_ecological_data):
    response = client.get("/api/v1/traits/statistics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_traits_analyzed" in data
    assert len(data["statistics"]) >= 1
    stat = data["statistics"][0]
    assert stat["trait_name_ets"] == "SLA"
    assert stat["count"] >= 6
    assert 9.0 <= stat["mean"] <= 11.0
