import pytest
from fastapi import status


def test_create_and_list_ethno_survey(client, operator_headers, seed_ecological_data):
    payload = {
        "taxon_id": "tax001",
        "respondent_type": "Expert",
        "geom_village": {"type": "Point", "coordinates": [-0.088, 14.025]},
        "village_name": "Yakouta",
        "climatic_zone": "Sahélienne",
        "perceived_decline_score": 0,
        "phenology_shift_observed": True,
        "phenology_shift_details": "Retard de feuillaison",
        "drought_resilience_rank": 1,
        "traditional_uses": "Pharmacopée, fourrage, savon traditionnel",
    }
    response = client.post("/api/v1/surveys/ethno", json=payload, headers=operator_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["village_name"] == "Yakouta"
    assert data["perceived_decline_score"] == 0

    # List
    list_resp = client.get("/api/v1/surveys/ethno?climatic_zone=Sahélienne")
    assert list_resp.status_code == status.HTTP_200_OK
    assert len(list_resp.json()) >= 1


def test_update_ethno_survey(client, operator_headers, seed_ecological_data):
    create_resp = client.post(
        "/api/v1/surveys/ethno",
        json={
            "taxon_id": "tax001",
            "respondent_type": "Local",
            "geom_village": "POINT(-0.09 14.02)",
            "village_name": "Dori Centre",
            "climatic_zone": "Sahélienne",
            "perceived_decline_score": -1,
            "drought_resilience_rank": 2,
        },
        headers=operator_headers,
    )
    survey_id = create_resp.json()["survey_id"]

    update_resp = client.put(
        f"/api/v1/surveys/ethno/{survey_id}",
        json={"perceived_decline_score": -2},
        headers=operator_headers,
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["perceived_decline_score"] == -2


def test_delete_ethno_survey(client, admin_headers, seed_ecological_data):
    create_resp = client.post(
        "/api/v1/surveys/ethno",
        json={
            "taxon_id": "tax001",
            "respondent_type": "Local",
            "geom_village": "POINT(0 0)",
            "climatic_zone": "Sahélienne",
            "perceived_decline_score": 0,
            "drought_resilience_rank": 3,
        },
        headers=admin_headers,
    )
    survey_id = create_resp.json()["survey_id"]

    del_resp = client.delete(f"/api/v1/surveys/ethno/{survey_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT
