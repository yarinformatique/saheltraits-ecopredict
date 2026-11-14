"""
Unit tests for Compound Leaf Leaflet Separation (Parkia biglobosa, Vachellia tortilis).
"""

from pathlib import Path
import pytest

from morpho_vision.pipeline import MorphoVisionPipeline


@pytest.fixture
def sample_compound_leaf_path():
    p = Path(__file__).parent.parent / "data" / "samples" / "sample_compound_leaf.png"
    assert p.exists()
    return p


def test_compound_leaflet_separation(sample_compound_leaf_path):
    """Verifies that compound leaves are separated into individual leaflets and rachis."""
    pipe = MorphoVisionPipeline()
    res, qc_path, elapsed = pipe.process_leaf_scan(
        image_input=sample_compound_leaf_path,
        is_compound=True,
        save_qc_overlay=True,
    )

    # 40 leaflets were synthesized along the rachis
    assert res.leaf_count == 40
    assert res.is_compound is True
    assert res.total_leaf_area_cm2 > 5.0
    assert 0.15 <= res.mean_leaf_area_cm2 <= 0.40
