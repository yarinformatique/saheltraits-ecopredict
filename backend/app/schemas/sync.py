from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.germination import SeedGerminationCreate
from app.schemas.individual import IndividualCreate
from app.schemas.site import SitePlotCreate
from app.schemas.soil import EnvironmentSoilCreate
from app.schemas.survey import EthnoSurveyCreate
from app.schemas.trait import TraitMeasurementCreate


class SyncBatchRequest(BaseModel):
    batch_id: str = Field(..., description="UUID ou identifiant unique du lot de synchronisation mobile")
    device_id: Optional[str] = Field(None, description="Identifiant matériel ou nom de l'appareil mobile terrain")
    collected_at: Optional[datetime] = None
    plots: List[SitePlotCreate] = Field(default_factory=list, description="Placettes nouvellement créées ou mises à jour")
    individuals: List[IndividualCreate] = Field(default_factory=list, description="Arbres/individus inventoriés")
    traits: List[TraitMeasurementCreate] = Field(default_factory=list, description="Mesures de traits multi-organes")
    seed_trials: List[SeedGerminationCreate] = Field(default_factory=list, description="Essais de germination")
    soil_records: List[EnvironmentSoilCreate] = Field(default_factory=list, description="Mesures physico-chimiques de sol")
    surveys: List[EthnoSurveyCreate] = Field(default_factory=list, description="Enquêtes ethno-écologiques")


class SyncBatchResponse(BaseModel):
    batch_id: str
    status: str  # 'SUCCESS', 'PARTIAL', 'ERROR'
    message: str
    synced_at: datetime
    plots_synced: int = 0
    individuals_synced: int = 0
    traits_synced: int = 0
    seed_trials_synced: int = 0
    soil_records_synced: int = 0
    surveys_synced: int = 0
    flagged_outliers_count: int = 0
    errors: List[str] = Field(default_factory=list)
