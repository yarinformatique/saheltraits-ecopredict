import pytest
from fastapi import status


def test_sync_field_batch_full_payload(client, operator_headers, seed_ecological_data):
    batch_payload = {
        "batch_id": "BATCH-MOBILE-TEST-001",
        "device_id": "SAMSUNG-GALAXY-TAB-ACTIVE3",
        "collected_at": "2026-11-14T09:00:00Z",
        "plots": [
            {
                "plot_id": "BF-SYNC-01",
                "site_name": "Site Test Sync",
                "climatic_zone": "Sahélienne",
                "geom": {"type": "Point", "coordinates": [-0.15, 14.2]},
                "elevation_m": 300.0,
            }
        ],
        "individuals": [
            {
                "plot_id": "BF-SYNC-01",
                "taxon_id": "tax001",
                "qr_code_tag": "QR-SYNC-BAL-001",
                "dbh_cm": 28.4,
                "total_height_m": 6.5,
                "crown_diameter_m": 4.8,
                "canopy_position": "Dominant",
                "health_status_score": 5,
                "geom_tree": {"type": "Point", "coordinates": [-0.1501, 14.2001]},
            }
        ],
        "traits": [
            {
                "ind_id": "ind001",
                "trait_name_ets": "SLA",
                "trait_value": 10.02,
                "unit": "mm2/mg",
                "organ_sampled": "Feuille",
            },
            {
                # Outlier measurement
                "ind_id": "ind001",
                "trait_name_ets": "SLA",
                "trait_value": 35.0,
                "unit": "mm2/mg",
                "organ_sampled": "Feuille",
            },
        ],
        "seed_trials": [
            {
                "ind_id": "ind001",
                "seed_batch_qr": "BATCH-SYNC-SEED-01",
                "temp_regime_c": "30/20",
                "osmotic_potential_mpa": 0.0,
                "total_seeds": 50,
                "germinated_count": 40,
            }
        ],
        "soil_records": [
            {
                "plot_id": "BF-SYNC-01",
                "depth_cm": "0-20",
                "clay_pct": 12.0,
                "ph_h2o": 6.5,
            }
        ],
        "surveys": [
            {
                "taxon_id": "tax001",
                "respondent_type": "Expert",
                "geom_village": {"type": "Point", "coordinates": [-0.15, 14.2]},
                "village_name": "Village Sync",
                "climatic_zone": "Sahélienne",
                "perceived_decline_score": 1,
                "drought_resilience_rank": 1,
            }
        ],
    }

    response = client.post("/api/v1/sync/field-batch", json=batch_payload, headers=operator_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["batch_id"] == "BATCH-MOBILE-TEST-001"
    assert data["status"] == "SUCCESS"
    assert data["plots_synced"] == 1
    assert data["individuals_synced"] == 1
    assert data["traits_synced"] == 2
    assert data["flagged_outliers_count"] == 1
    assert data["seed_trials_synced"] == 1
    assert data["soil_records_synced"] == 1
    assert data["surveys_synced"] == 1
    assert len(data["errors"]) == 0


def test_sync_field_batch_unauthorized_for_public(client, public_headers):
    batch_payload = {
        "batch_id": "BATCH-UNAUTH",
        "plots": [],
        "individuals": [],
        "traits": [],
    }
    response = client.post("/api/v1/sync/field-batch", json=batch_payload, headers=public_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
