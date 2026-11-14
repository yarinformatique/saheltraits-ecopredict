from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User
from app.schemas.sync import SyncBatchRequest, SyncBatchResponse
from app.services.sync import SyncService

router = APIRouter()


@router.post("/field-batch", response_model=SyncBatchResponse, status_code=status.HTTP_200_OK)
def sync_field_batch(
    batch_data: SyncBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Réception et ingestion asynchrone / transactionnelle des lots de collecte mobile de terrain.

    Permet la synchronisation hors-ligne des placettes, arbres tagués par QR-code,
    mesures multi-organes de traits fonctionnels (avec détection automatique des 3-sigmas),
    essais de germination, paramètres pédologiques et enquêtes ethno-écologiques.
    """
    response = SyncService.process_field_batch(
        db=db,
        batch_data=batch_data,
        operator_id=current_user.user_id,
    )
    return response
