from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator
from app.models.spatial_types import wkt_to_geojson


class IndividualBase(BaseModel):
    plot_id: str = Field(..., max_length=50)
    taxon_id: str = Field(..., max_length=36)
    qr_code_tag: str = Field(..., max_length=100)
    dbh_cm: Optional[float] = Field(None, ge=0)
    total_height_m: Optional[float] = Field(None, ge=0)
    crown_diameter_m: Optional[float] = Field(None, ge=0)
    canopy_position: Optional[str] = Field(
        None,
        description="Position dans la canopée (Dominant, Codominant, Intermédiaire, Sous-étage, Émergent)",
    )
    health_status_score: int = Field(..., ge=1, le=5, description="Score sanitaire de 1 à 5")
    geom_tree: Union[Dict[str, Any], str] = Field(..., description="Position GPS de l'arbre (Point SRID 4326)")


class IndividualCreate(IndividualBase):
    pass


class IndividualUpdate(BaseModel):
    plot_id: Optional[str] = None
    taxon_id: Optional[str] = None
    qr_code_tag: Optional[str] = None
    dbh_cm: Optional[float] = None
    total_height_m: Optional[float] = None
    crown_diameter_m: Optional[float] = None
    canopy_position: Optional[str] = None
    health_status_score: Optional[int] = None
    geom_tree: Optional[Union[Dict[str, Any], str]] = None


class IndividualOut(BaseModel):
    ind_id: str
    plot_id: str
    taxon_id: str
    qr_code_tag: str
    dbh_cm: Optional[float] = None
    total_height_m: Optional[float] = None
    crown_diameter_m: Optional[float] = None
    canopy_position: Optional[str] = None
    health_status_score: int
    geom_tree: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("geom_tree", mode="before")
    def format_geom(cls, v):
        if isinstance(v, dict):
            return v
        return wkt_to_geojson(v)

    class Config:
        from_attributes = True
