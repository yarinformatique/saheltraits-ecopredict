import pytest
from fastapi import status


def test_list_taxa(client, seed_ecological_data):
    response = client.get("/api/v1/taxonomy")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    assert any("Balanites" in item["scientific_name"] for item in data)


def test_filter_taxa_by_family(client, seed_ecological_data):
    response = client.get("/api/v1/taxonomy?family=Fabaceae")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["family"] == "Fabaceae"


def test_search_taxa_vernacular(client, seed_ecological_data):
    # Search by Moore name 'Kieglga'
    response = client.get("/api/v1/taxonomy?search=Kieglga")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["vernacular_moore"] == "Kieglga"


def test_get_taxon_by_id(client, seed_ecological_data):
    response = client.get("/api/v1/taxonomy/tax001")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["taxon_id"] == "tax001"
    assert data["genus"] == "Balanites"


def test_get_taxon_not_found(client):
    response = client.get("/api/v1/taxonomy/non_existent_id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_taxon_with_admin(client, admin_headers):
    payload = {
        "scientific_name": "Adansonia digitata L.",
        "family": "Malvaceae",
        "genus": "Adansonia",
        "vernacular_moore": "Toèga",
        "vernacular_dioula": "Sira",
        "vernacular_fulfulde": "Boki",
        "functional_group": "Méga-arbre réserve hydrique",
        "iucn_status": "LC",
    }
    response = client.post("/api/v1/taxonomy", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["scientific_name"] == "Adansonia digitata L."
    assert data["genus"] == "Adansonia"


def test_create_taxon_forbidden_for_public(client, public_headers):
    payload = {
        "scientific_name": "Ziziphus mauritiana Lam.",
        "family": "Rhamnaceae",
        "genus": "Ziziphus",
    }
    response = client.post("/api/v1/taxonomy", json=payload, headers=public_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_taxon(client, admin_headers, seed_ecological_data):
    payload = {"vernacular_moore": "Kieglga Modifié"}
    response = client.put("/api/v1/taxonomy/tax001", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["vernacular_moore"] == "Kieglga Modifié"


def test_delete_taxon(client, admin_headers):
    # Create temporary taxon to delete
    create_resp = client.post(
        "/api/v1/taxonomy",
        json={"scientific_name": "Temp delete taxon", "family": "TempFam", "genus": "TempGen"},
        headers=admin_headers,
    )
    temp_id = create_resp.json()["taxon_id"]

    del_resp = client.delete(f"/api/v1/taxonomy/{temp_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT


def test_verify_gbif_taxonomy_endpoint(client):
    response = client.get("/api/v1/taxonomy/gbif/verify?scientific_name=Balanites%20aegyptiaca")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "scientific_name" in data
