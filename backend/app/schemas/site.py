from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator
from app.models.spatial_types import wkt_to_geojson


class SitePlotBase(BaseModel):
    plot_id: str = Field(..., max_length=50, description="Identifiant unique de la placette (ex: BF-DOR-01)")
    site_name: str = Field(..., max_length=150)
    climatic_zone: str = Field(
        ...,
        pattern="^(Sahélienne|Soudano-Sahélienne|Soudanienne)$",
        description="Zone bioclimatique au Burkina Faso",
    )
    geom: Union[Dict[str, Any], str] = Field(..., description="Géométrie GeoJSON ou WKT (Point ou Polygone, SRID 4326)")
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    protection_status: Optional[str] = Field(None, max_length=100)
    fire_frequency_20yr: Optional[float] = None


class SitePlotCreate(SitePlotBase):
    pass


class SitePlotUpdate(BaseModel):
    site_name: Optional[str] = None
    climatic_zone: Optional[str] = None
    geom: Optional[Union[Dict[str, Any], str]] = None
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    protection_status: Optional[str] = None
    fire_frequency_20yr: Optional[float] = None


class SitePlotOut(BaseModel):
    plot_id: str
    site_name: str
    climatic_zone: str
    geom: Optional[Dict[str, Any]] = None
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    protection_status: Optional[str] = None
    fire_frequency_20yr: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("geom", mode="before")
    def format_geom(cls, v):
        if isinstance(v, dict):
            return v
        return wkt_to_geojson(v)

    class Config:
        from_attributes = True
