"""
Speed benchmark test for Leaf & Seed Morpho-Analyzer.
Acceptance Criterion: Processing speed < 2 seconds per scan.
"""

from pathlib import Path
import time
import pytest

from morpho_vision.pipeline import MorphoVisionPipeline


def test_speed_benchmark_leaf_scan():
    """Validates that a full leaf scan executes in under 2.0 seconds."""
    pipe = MorphoVisionPipeline()
    img_path = Path(__file__).parent.parent / "data" / "samples" / "sample_leaf_scan.png"
    assert img_path.exists()

    # Warmup
    pipe.process_leaf_scan(img_path, save_qc_overlay=False)

    # Measured run with QC overlay rendering and disk write
    t0 = time.perf_counter()
    res, qc_path, elapsed = pipe.process_leaf_scan(img_path, save_qc_overlay=True)
    total_time = time.perf_counter() - t0

    print(f"\n[BENCHMARK] Leaf scan completed in {total_time:.3f}s (pipeline reports {elapsed:.3f}s)")
    assert total_time < 2.0, f"Processing time {total_time:.3f}s exceeds the 2.0s acceptance threshold!"


def test_speed_benchmark_seed_scan():
    """Validates that a seed scan executes in under 2.0 seconds."""
    pipe = MorphoVisionPipeline()
    img_path = Path(__file__).parent.parent / "data" / "samples" / "sample_seed_scan.png"
    assert img_path.exists()

    # Warmup
    pipe.process_seed_scan(img_path, save_qc_overlay=False)

    t0 = time.perf_counter()
    res, qc_path, elapsed = pipe.process_seed_scan(img_path, save_qc_overlay=True)
    total_time = time.perf_counter() - t0

    print(f"\n[BENCHMARK] Seed scan completed in {total_time:.3f}s (pipeline reports {elapsed:.3f}s)")
    assert total_time < 2.0, f"Processing time {total_time:.3f}s exceeds the 2.0s acceptance threshold!"
