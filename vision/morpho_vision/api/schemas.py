"""
Pydantic V2 schemas for the Morpho-Analyzer FastAPI microservice.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalibrationResponse(BaseModel):
    pixels_per_cm: float
    pixels_per_mm: float
    cm2_per_pixel: float
    mm2_per_pixel: float
    marker_detected: bool
    method: str
    dpi_equivalent: float
    marker_box: Optional[List[int]] = None


class HerbivoryDetail(BaseModel):
    herbivory_percentage: float
    consumed_area_cm2: float
    reconstructed_intact_area_cm2: float
    internal_hole_count: int
    internal_holes_area_cm2: float
    marginal_damage_area_cm2: float


class SingleLeafOut(BaseModel):
    leaf_id: int
    area_cm2: float
    perimeter_cm: float
    length_cm: float
    width_cm: float
    circularity: float
    aspect_ratio: float
    centroid_x: float
    centroid_y: float
    herbivory: HerbivoryDetail


class LeafAnalysisResponse(BaseModel):
    success: bool = True
    qr_code_tag: Optional[str] = None
    total_leaf_area_cm2: float
    mean_leaf_area_cm2: float
    std_leaf_area_cm2: float
    leaf_count: int
    mean_length_cm: float
    mean_width_cm: float
    mean_circularity: float
    mean_herbivory_pct: float
    is_compound: bool
    rachis_detected: bool
    scale: CalibrationResponse
    leaves: List[SingleLeafOut]
    qc_overlay_path: Optional[str] = None
    processing_time_sec: float


class SingleSeedOut(BaseModel):
    seed_id: int
    length_mm: float
    width_mm: float
    projected_area_mm2: float
    perimeter_mm: float
    circularity: float
    eccentricity: float
    aspect_ratio: float
    bruchid_attacked: bool
    bruchid_hole_count: int


class SeedAnalysisResponse(BaseModel):
    success: bool = True
    qr_code_tag: Optional[str] = None
    total_seed_count: int
    mean_area_mm2: float
    std_area_mm2: float
    mean_length_mm: float
    std_length_mm: float
    mean_width_mm: float
    std_width_mm: float
    mean_eccentricity: float
    mean_circularity: float
    attacked_seed_count: int
    bruchid_attack_rate_pct: float
    scale: CalibrationResponse
    seeds: List[SingleSeedOut]
    qc_overlay_path: Optional[str] = None
    processing_time_sec: float


class BatchProcessRequest(BaseModel):
    input_directory: str
    output_directory: Optional[str] = None
    scan_type: str = "leaf"  # "leaf" or "seed"
    is_compound: bool = False
    sync_to_saheltraits: bool = False


class BatchItemSummary(BaseModel):
    filename: str
    qr_code_tag: Optional[str]
    organ_count: int
    main_metric: float  # total_area for leaf, mean_area for seed
    processing_time_sec: float
    status: str
    error: Optional[str] = None


class BatchProcessResponse(BaseModel):
    success: bool = True
    total_files: int
    successful_files: int
    failed_files: int
    total_elapsed_time_sec: float
    average_speed_per_scan_sec: float
    items: List[BatchItemSummary]


class SahelTraitsSyncRequest(BaseModel):
    qr_code_tag: str
    results_json_path: str
    auth_token: Optional[str] = None


class SahelTraitsSyncResponse(BaseModel):
    success: bool
    individual_id: Optional[str] = None
    measurements_created: int
    traits_synced: List[str]
    details: Optional[str] = None
