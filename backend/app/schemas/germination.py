from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SeedGerminationBase(BaseModel):
    ind_id: str = Field(..., max_length=36)
    seed_batch_qr: str = Field(..., max_length=100)
    temp_regime_c: str = Field(..., max_length=50, description="Régime de température (ex: 25/15, 30/20, 35/25)")
    osmotic_potential_mpa: float = Field(0.0, le=0.0, description="Potentiel osmotique (0.0, -0.2, -0.4, -0.8 MPa)")
    pretreatment_type: Optional[str] = Field(None, max_length=100)
    total_seeds: int = Field(..., gt=0)
    germinated_count: int = Field(..., ge=0)
    t50_days: Optional[float] = Field(None, ge=0)


class SeedGerminationCreate(SeedGerminationBase):
    pass


class SeedGerminationUpdate(BaseModel):
    seed_batch_qr: Optional[str] = None
    temp_regime_c: Optional[str] = None
    osmotic_potential_mpa: Optional[float] = None
    pretreatment_type: Optional[str] = None
    total_seeds: Optional[int] = None
    germinated_count: Optional[int] = None
    t50_days: Optional[float] = None


class SeedGerminationOut(SeedGerminationBase):
    germ_id: str
    final_gp_pct: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
