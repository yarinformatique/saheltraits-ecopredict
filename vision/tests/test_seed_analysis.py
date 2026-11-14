"""
Unit tests for Seed Morphometrics & Bruchid Predation Detection.
"""

from pathlib import Path
import pytest

from morpho_vision.pipeline import MorphoVisionPipeline


@pytest.fixture
def sample_seed_scan_path():
    p = Path(__file__).parent.parent / "data" / "samples" / "sample_seed_scan.png"
    assert p.exists()
    return p


def test_seed_counting_and_bruchid_detection(sample_seed_scan_path):
    """Verifies seed lot count, length, width, projected area, and bruchid attack rate."""
    pipe = MorphoVisionPipeline()
    res, qc_path, elapsed = pipe.process_seed_scan(
        image_input=sample_seed_scan_path,
        save_qc_overlay=True,
    )

    # Scanned image has 30 seeds
    assert res.total_seed_count == 30

    # Ground truth: every 5th seed has an emergence hole = 6 attacked seeds = 20%
    assert res.attacked_seed_count == 6
    assert abs(res.bruchid_attack_rate_pct - 20.0) < 1.0

    # Biometric dimensions
    assert 12.0 <= res.mean_length_mm <= 17.0
    assert 8.0 <= res.mean_width_mm <= 12.0
    assert res.mean_eccentricity > 0.5

    # QR Code Tag
    assert res.qr_code_tag == "BF-KDG-ACARAD-001"

    # QC Image
    assert qc_path is not None
    assert qc_path.exists()
