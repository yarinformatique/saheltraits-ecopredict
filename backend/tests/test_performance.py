import time
import pytest
from fastapi import status


def test_spatial_query_performance(client, seed_ecological_data):
    """Vérifie que le temps moyen des requêtes spatiales est strictement inférieur à 300 ms."""
    iterations = 10
    total_duration = 0.0

    for _ in range(iterations):
        t0 = time.perf_counter()
        resp = client.get("/api/v1/spatial/plots")
        duration = (time.perf_counter() - t0) * 1000.0  # in ms
        total_duration += duration
        assert resp.status_code == status.HTTP_200_OK

    avg_latency = total_duration / iterations
    print(f"\n[Performance] Temps moyen spatial plots : {avg_latency:.2f} ms (< 300 ms)")
    assert avg_latency < 300.0, f"Latence spatiale trop élevée : {avg_latency:.2f} ms"


def test_export_performance_dwca(client, seed_ecological_data):
    """Vérifie que le temps moyen d'exportation Darwin Core Archive (DwC-A) est inférieur à 300 ms."""
    iterations = 10
    total_duration = 0.0

    for _ in range(iterations):
        t0 = time.perf_counter()
        resp = client.get("/api/v1/traits/export?format=dwca")
        duration = (time.perf_counter() - t0) * 1000.0  # in ms
        total_duration += duration
        assert resp.status_code == status.HTTP_200_OK

    avg_latency = total_duration / iterations
    print(f"\n[Performance] Temps moyen export DwC-A zip : {avg_latency:.2f} ms (< 300 ms)")
    assert avg_latency < 300.0, f"Latence export DwC-A trop élevée : {avg_latency:.2f} ms"


def test_export_performance_csv(client, seed_ecological_data):
    """Vérifie que le temps moyen d'exportation CSV est inférieur à 300 ms."""
    iterations = 10
    total_duration = 0.0

    for _ in range(iterations):
        t0 = time.perf_counter()
        resp = client.get("/api/v1/traits/export?format=csv")
        duration = (time.perf_counter() - t0) * 1000.0  # in ms
        total_duration += duration
        assert resp.status_code == status.HTTP_200_OK

    avg_latency = total_duration / iterations
    print(f"\n[Performance] Temps moyen export CSV : {avg_latency:.2f} ms (< 300 ms)")
    assert avg_latency < 300.0, f"Latence export CSV trop élevée : {avg_latency:.2f} ms"
