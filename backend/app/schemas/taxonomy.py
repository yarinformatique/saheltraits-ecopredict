from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaxonomyBase(BaseModel):
    scientific_name: str = Field(..., max_length=255)
    accepted_name_gbif: Optional[str] = Field(None, max_length=255)
    gbif_usage_key: Optional[int] = None
    gbif_confidence_score: Optional[float] = None
    family: str = Field(..., max_length=100)
    genus: str = Field(..., max_length=100)
    vernacular_moore: Optional[str] = Field(None, max_length=150)
    vernacular_dioula: Optional[str] = Field(None, max_length=150)
    vernacular_fulfulde: Optional[str] = Field(None, max_length=150)
    functional_group: Optional[str] = Field(None, max_length=100)
    iucn_status: Optional[str] = Field("LC", max_length=20)


class TaxonomyCreate(TaxonomyBase):
    pass


class TaxonomyUpdate(BaseModel):
    scientific_name: Optional[str] = None
    accepted_name_gbif: Optional[str] = None
    gbif_usage_key: Optional[int] = None
    gbif_confidence_score: Optional[float] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    vernacular_moore: Optional[str] = None
    vernacular_dioula: Optional[str] = None
    vernacular_fulfulde: Optional[str] = None
    functional_group: Optional[str] = None
    iucn_status: Optional[str] = None


class TaxonomyOut(TaxonomyBase):
    taxon_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GBIFMatchResult(BaseModel):
    usage_key: Optional[int] = None
    scientific_name: Optional[str] = None
    accepted_usage_key: Optional[int] = None
    accepted_scientific_name: Optional[str] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    status: Optional[str] = None
    confidence: Optional[float] = None
    match_type: Optional[str] = None
