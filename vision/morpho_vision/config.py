"""
Configuration module for LEAF & SEED MORPHO-ANALYZER.
PhD Thesis Project — Functional Ecology & Bioinformatics (2026-2029)
SahelTraits-DB & EcoPredict Integration
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class CalibrationConfig:
    """Settings for automatic calibration target detection & DPI conversion."""
    # Known area of the reference marker in cm² (default: 4.0 cm² = 2.0 cm x 2.0 cm red square)
    known_area_cm2: float = 4.0
    known_side_cm: float = 2.0
    
    # Target color: "red", "blue", "green"
    marker_color: str = "red"
    
    # Target geometry filters
    min_solidity: float = 0.88
    min_aspect_ratio: float = 0.80
    max_aspect_ratio: float = 1.25
    
    # Default fallback DPI if no marker is found (600 DPI standard flatbed scan)
    fallback_dpi: float = 600.0
    
    # Acceptance criteria: maximum allowed relative error (%)
    max_relative_error_pct: float = 1.5


@dataclass
class SegmentationConfig:
    """Colorimetric and thresholding configuration for image cleaning."""
    # Color spaces: "HSV", "LAB", "OTSU_GRAY", "HYBRID"
    method: str = "HYBRID"
    
    # Minimum area (in mm²) to be considered an organ and not glass dust or scanner debris
    min_organ_area_mm2: float = 1.5
    
    # Background type: "white" (default scanner plate), "blue" (high-contrast tray for seeds/pale leaves)
    background_type: str = "white"
    
    # Morphological kernel sizes (in mm equivalent)
    closing_radius_mm: float = 0.3
    opening_radius_mm: float = 0.2
    
    # Petiole handling
    include_petiole: bool = True
    petiole_thinning_threshold_mm: float = 1.2


@dataclass
class LeafAnalysisConfig:
    """Leaf morphometrics and herbivory estimation parameters."""
    # Compound leaf leaflet separation (e.g. Parkia biglobosa, Vachellia tortilis)
    is_compound_leaf: bool = False
    watershed_min_distance_mm: float = 1.5
    
    # Herbivory damage calculation
    enable_herbivory_estimation: bool = True
    convex_hull_gap_closing_mm: float = 2.0
    detect_internal_holes: bool = True
    min_hole_area_mm2: float = 0.5


@dataclass
class SeedAnalysisConfig:
    """Seed counting, morphometrics, and bruchid attack detection parameters."""
    # Target seed lot size (standard protocol: 100 seeds per tree)
    expected_lot_size: int = 100
    
    # Separation of clustered/touching seeds
    enable_watershed_separation: bool = True
    seed_distance_peak_min_mm: float = 3.5
    
    # Bruchid beetle emergence hole detection (Bruchidius / Caryedon serratus)
    enable_bruchid_detection: bool = True
    min_bruchid_hole_diameter_mm: float = 0.8
    max_bruchid_hole_diameter_mm: float = 3.5
    hole_circularity_min: float = 0.60


@dataclass
class TraceabilityConfig:
    """QR code reading, QC overlays, and SahelTraits-DB sync."""
    # QR reading engine preference: "dual" (pyzbar + cv2.QRCodeDetector), "pyzbar", "cv2"
    qr_engine: str = "dual"
    
    # QC Overlay output directory
    qc_output_dir: Path = Path("data/output/qc_overlays")
    
    # SahelTraits-DB backend API
    saheltraits_base_url: str = "http://localhost:8000/api/v1"
    saheltraits_timeout_sec: float = 10.0


@dataclass
class MorphoVisionConfig:
    """Global configuration wrapper."""
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    leaf: LeafAnalysisConfig = field(default_factory=LeafAnalysisConfig)
    seed: SeedAnalysisConfig = field(default_factory=SeedAnalysisConfig)
    traceability: TraceabilityConfig = field(default_factory=TraceabilityConfig)
    
    # Root paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    output_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "output")


# Default global instance
DEFAULT_CONFIG = MorphoVisionConfig()
