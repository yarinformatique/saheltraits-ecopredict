import pytest
from fastapi import status


def test_spatial_plots_geojson(client, seed_ecological_data):
    response = client.get("/api/v1/spatial/plots")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["total_features"] >= 2
    feature = data["features"][0]
    assert feature["type"] == "Feature"
    assert "geometry" in feature
    assert "properties" in feature
    assert "plot_id" in feature["properties"]
    assert "climatic_zone" in feature["properties"]


def test_spatial_plots_bbox_filter(client, seed_ecological_data):
    # Bbox around Dori: lon [-0.2, 0.0], lat [13.9, 14.2]
    url = "/api/v1/spatial/plots?min_lon=-0.2&min_lat=13.9&max_lon=0.0&max_lat=14.2"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_features"] == 1
    assert data["features"][0]["properties"]["plot_id"] == "BF-DOR-01"


def test_spatial_plots_radial_proximity_filter(client, seed_ecological_data):
    # Proximity near Dori point (-0.09, 14.03), radius 10 km
    url = "/api/v1/spatial/plots?near_lon=-0.09&near_lat=14.03&radius_km=10.0"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_features"] == 1
    assert data["features"][0]["properties"]["plot_id"] == "BF-DOR-01"


def test_spatial_trees_geojson(client, seed_ecological_data):
    response = client.get("/api/v1/spatial/trees")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["total_features"] >= 2
    tree_feat = data["features"][0]
    assert tree_feat["type"] == "Feature"
    assert "geometry" in tree_feat
    assert "qr_code_tag" in tree_feat["properties"]
    assert "scientific_name" in tree_feat["properties"]


def test_spatial_trees_plot_filter(client, seed_ecological_data):
    response = client.get("/api/v1/spatial/trees?plot_id=BF-DOR-01")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_features"] == 1
    assert data["features"][0]["properties"]["plot_id"] == "BF-DOR-01"
