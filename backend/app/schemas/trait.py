from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TraitMeasurementBase(BaseModel):
    ind_id: str = Field(..., max_length=36)
    trait_name_ets: str = Field(
        ...,
        max_length=100,
        description="Nom standardisé ETS v1.0 (ex: SLA, LDMC, Leaf_N, Wood_density, Leaf_area)",
    )
    trait_value: float = Field(..., description="Valeur numérique mesurée")
    unit: str = Field(..., max_length=50, description="Unité de mesure (ex: mm2/mg, mg/g, g/cm3)")
    organ_sampled: str = Field(
        ...,
        max_length=50,
        description="Organe végétal échantillonné (Feuille, Rameau, Tronc, Écorce, Racine, Fleur, Fruit, Graine)",
    )
    measurement_protocol: Optional[str] = None
    instrument_id: Optional[str] = Field(None, max_length=100)
    measurement_date: Optional[date] = None
    operator_id: Optional[str] = None


class TraitMeasurementCreate(TraitMeasurementBase):
    pass


class TraitMeasurementUpdate(BaseModel):
    trait_name_ets: Optional[str] = None
    trait_value: Optional[float] = None
    unit: Optional[str] = None
    organ_sampled: Optional[str] = None
    measurement_protocol: Optional[str] = None
    instrument_id: Optional[str] = None
    measurement_date: Optional[date] = None
    qc_flag: Optional[str] = None
    qc_notes: Optional[str] = None


class TraitMeasurementQCUpdate(BaseModel):
    qc_flag: str = Field(
        ...,
        pattern="^(VALID|SUSPECT_OUTLIER_3SIGMA|FLAGGED_MANUAL|MANUALLY_APPROVED|REJECTED)$",
        description="Statut de contrôle qualité",
    )
    qc_notes: Optional[str] = Field(None, description="Justification ou notes du chercheur")


class TraitMeasurementOut(TraitMeasurementBase):
    meas_id: str
    measurement_date: date
    qc_flag: str
    qc_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeafScanResult(BaseModel):
    success: bool
    leaf_detected: bool
    target_detected: bool
    calibration_mode: str = Field(..., description="CERTIFIED_TARGET, MANUAL_TACTILE ou DEFAULT_ESTIMATED")
    ref_type: str
    known_mm: float
    pixels_per_mm: float
    leaf_area_mm2: float
    leaf_area_cm2: float
    perimeter_mm: float
    max_length_mm: float
    max_width_mm: float
    leaf_pixel_count: int
    image_width: int
    image_height: int
    status_message: str
    contour_points: Optional[list] = None
    processed_image_base64: Optional[str] = None

