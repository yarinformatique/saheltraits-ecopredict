from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator
from app.models.spatial_types import wkt_to_geojson


class EthnoSurveyBase(BaseModel):
    taxon_id: str = Field(..., max_length=36)
    respondent_type: str = Field(..., pattern="^(Expert|Local)$", description="Type de répondant")
    geom_village: Union[Dict[str, Any], str] = Field(..., description="Localisation GPS du village (Point SRID 4326)")
    village_name: Optional[str] = Field(None, max_length=150)
    climatic_zone: str = Field(..., pattern="^(Sahélienne|Soudano-Sahélienne|Soudanienne)$")
    perceived_decline_score: int = Field(
        ...,
        ge=-2,
        le=2,
        description="Score de perception du déclin (-2: régression forte, 0: stable, +2: expansion)",
    )
    phenology_shift_observed: bool = Field(False, description="Observation d'un décalage phénologique")
    phenology_shift_details: Optional[str] = None
    drought_resilience_rank: int = Field(..., ge=1, description="Rang de résilience à la sécheresse (1 = plus résilient)")
    traditional_uses: Optional[str] = None
    interviewer_id: Optional[str] = None


class EthnoSurveyCreate(EthnoSurveyBase):
    pass


class EthnoSurveyUpdate(BaseModel):
    taxon_id: Optional[str] = None
    respondent_type: Optional[str] = None
    geom_village: Optional[Union[Dict[str, Any], str]] = None
    village_name: Optional[str] = None
    climatic_zone: Optional[str] = None
    perceived_decline_score: Optional[int] = None
    phenology_shift_observed: Optional[bool] = None
    phenology_shift_details: Optional[str] = None
    drought_resilience_rank: Optional[int] = None
    traditional_uses: Optional[str] = None


class EthnoSurveyOut(BaseModel):
    survey_id: str
    taxon_id: str
    respondent_type: str
    geom_village: Optional[Dict[str, Any]] = None
    village_name: Optional[str] = None
    climatic_zone: str
    perceived_decline_score: int
    phenology_shift_observed: bool
    phenology_shift_details: Optional[str] = None
    drought_resilience_rank: int
    traditional_uses: Optional[str] = None
    interviewer_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator("geom_village", mode="before")
    def format_geom(cls, v):
        if isinstance(v, dict):
            return v
        return wkt_to_geojson(v)

    class Config:
        from_attributes = True
