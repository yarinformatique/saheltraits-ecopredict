import io
import zipfile
import pytest
from fastapi import status


def test_export_traits_json(client, seed_ecological_data):
    response = client.get("/api/v1/traits/export?format=json")
    assert response.status_code == status.HTTP_200_OK
    assert "application/json" in response.headers["content-type"]
    data = response.json()
    assert "standard" in data
    assert data["standard"] == "Ecological Trait-data Standard (ETS v1.0)"
    assert data["total_records"] >= 6
    assert "data" in data


def test_export_traits_csv(client, seed_ecological_data):
    response = client.get("/api/v1/traits/export?format=csv")
    assert response.status_code == status.HTTP_200_OK
    assert "text/csv" in response.headers["content-type"]
    assert "attachment; filename=saheltraits_export.csv" in response.headers["content-disposition"]
    csv_text = response.text
    assert "meas_id" in csv_text
    assert "scientific_name" in csv_text
    assert "trait_name_ets" in csv_text
    assert "trait_value" in csv_text


def test_export_traits_dwca_zip(client, seed_ecological_data):
    response = client.get("/api/v1/traits/export?format=dwca")
    assert response.status_code == status.HTTP_200_OK
    assert "application/zip" in response.headers["content-type"]
    assert "saheltraits_dwca.zip" in response.headers["content-disposition"]

    # Verify zip content
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes, "r") as z:
        file_list = z.namelist()
        assert "meta.xml" in file_list
        assert "occurrence.txt" in file_list
        assert "measurementorfact.txt" in file_list

        # Verify meta.xml content
        meta_content = z.read("meta.xml").decode("utf-8")
        assert "http://rs.tdwg.org/dwc/terms/Occurrence" in meta_content
        assert "http://rs.tdwg.org/dwc/terms/MeasurementOrFact" in meta_content

        # Verify occurrence.txt content
        occ_content = z.read("occurrence.txt").decode("utf-8")
        assert "LivingSpecimen" in occ_content
        assert "Balanites aegyptiaca" in occ_content


def test_export_traits_with_filters(client, seed_ecological_data):
    # Filter by species Balanites
    response = client.get("/api/v1/traits/export?species=Balanites&format=json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for row in data["data"]:
        assert "Balanites" in row["scientific_name"]

    # Filter by climatic zone
    response_zone = client.get("/api/v1/traits/export?climatic_zone=Sahélienne&format=json")
    assert response_zone.status_code == status.HTTP_200_OK
    data_zone = response_zone.json()
    for row in data_zone["data"]:
        assert row["climatic_zone"] == "Sahélienne"
