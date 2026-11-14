"""
Unit tests for Leaf Morphometrics & Herbivory Extraction.
"""

from pathlib import Path
import pytest

from morpho_vision.pipeline import MorphoVisionPipeline


@pytest.fixture
def sample_leaf_scan_path():
    p = Path(__file__).parent.parent / "data" / "samples" / "sample_leaf_scan.png"
    assert p.exists()
    return p


def test_leaf_morphometrics_extraction(sample_leaf_scan_path):
    """Verifies leaf count, area, length, width, and circularity."""
    pipe = MorphoVisionPipeline()
    res, qc_path, elapsed = pipe.process_leaf_scan(
        image_input=sample_leaf_scan_path,
        save_qc_overlay=True,
    )

    # Scanned image has 3 leaves
    assert res.leaf_count == 3
    assert res.total_leaf_area_cm2 > 50.0
    assert res.mean_length_cm > 5.0
    assert res.mean_width_cm > 2.0
    assert 0.4 <= res.mean_circularity <= 0.9

    # Herbivory damage: Leaf 2 has caterpillar notch + shot hole
    assert res.mean_herbivory_pct > 10.0

    # Verification of QR tag
    assert res.qr_code_tag == "BF-KDG-ACARAD-001"

    # Verification of QC image generation
    assert qc_path is not None
    assert qc_path.exists()

    # Speed threshold: < 2.0s
    assert elapsed < 2.0, f"Processing time {elapsed}s exceeds 2s limit"
