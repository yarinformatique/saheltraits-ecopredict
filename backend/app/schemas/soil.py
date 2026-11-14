from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class EnvironmentSoilBase(BaseModel):
    plot_id: str = Field(..., max_length=50)
    depth_cm: str = Field(..., max_length=30, description="Horizon de profondeur (ex: 0-20, 20-40, 40-60)")
    clay_pct: Optional[float] = Field(None, ge=0, le=100)
    silt_pct: Optional[float] = Field(None, ge=0, le=100)
    sand_pct: Optional[float] = Field(None, ge=0, le=100)
    ph_h2o: Optional[float] = Field(None, ge=0, le=14)
    organic_carbon_gkg: Optional[float] = Field(None, ge=0)
    total_n_gkg: Optional[float] = Field(None, ge=0)
    avail_p_mgkg: Optional[float] = Field(None, ge=0)
    cec_cmolkg: Optional[float] = Field(None, ge=0)
    dry_season_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    sampling_date: Optional[date] = None


class EnvironmentSoilCreate(EnvironmentSoilBase):
    pass


class EnvironmentSoilUpdate(BaseModel):
    depth_cm: Optional[str] = None
    clay_pct: Optional[float] = None
    silt_pct: Optional[float] = None
    sand_pct: Optional[float] = None
    ph_h2o: Optional[float] = None
    organic_carbon_gkg: Optional[float] = None
    total_n_gkg: Optional[float] = None
    avail_p_mgkg: Optional[float] = None
    cec_cmolkg: Optional[float] = None
    dry_season_moisture_pct: Optional[float] = None
    sampling_date: Optional[date] = None


class EnvironmentSoilOut(EnvironmentSoilBase):
    env_id: str
    sampling_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
