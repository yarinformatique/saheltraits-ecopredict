"""
Package 02_morpho_vision — Automated Computer Vision Component.
PhD Thesis — Functional Ecology & Bioinformatics (2026-2029)
Author: YAGO Abdoul Rachide
"""

import sys
from pathlib import Path

# Ensure root path is in sys.path
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from morpho_vision import DEFAULT_CONFIG, MorphoVisionConfig
from morpho_vision.pipeline import MorphoVisionPipeline

__all__ = ["DEFAULT_CONFIG", "MorphoVisionConfig", "MorphoVisionPipeline"]
