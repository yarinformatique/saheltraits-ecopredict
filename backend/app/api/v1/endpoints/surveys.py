from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.survey import EthnoSurvey
from app.models.taxonomy import Taxonomy
from app.models.user import User
from app.schemas.survey import EthnoSurveyCreate, EthnoSurveyOut, EthnoSurveyUpdate

router = APIRouter()


@router.get("", response_model=List[EthnoSurveyOut])
def list_ethno_surveys(
    taxon_id: Optional[str] = None,
    climatic_zone: Optional[str] = None,
    respondent_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des enquêtes ethno-écologiques sur la résilience et le dépérissement perçu des espèces."""
    query = db.query(EthnoSurvey)
    if taxon_id:
        query = query.filter(EthnoSurvey.taxon_id == taxon_id)
    if climatic_zone:
        query = query.filter(EthnoSurvey.climatic_zone == climatic_zone)
    if respondent_type:
        query = query.filter(EthnoSurvey.respondent_type == respondent_type)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=EthnoSurveyOut, status_code=status.HTTP_201_CREATED)
def create_ethno_survey(
    survey_in: EthnoSurveyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Enregistre une enquête ethno-écologique auprès des populations locales ou des experts."""
    taxon = db.query(Taxonomy).filter(Taxonomy.taxon_id == survey_in.taxon_id).first()
    if not taxon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Taxon '{survey_in.taxon_id}' introuvable.",
        )

    survey = EthnoSurvey(
        taxon_id=survey_in.taxon_id,
        respondent_type=survey_in.respondent_type,
        geom_village=survey_in.geom_village,
        village_name=survey_in.village_name,
        climatic_zone=survey_in.climatic_zone,
        perceived_decline_score=survey_in.perceived_decline_score,
        phenology_shift_observed=survey_in.phenology_shift_observed,
        phenology_shift_details=survey_in.phenology_shift_details,
        drought_resilience_rank=survey_in.drought_resilience_rank,
        traditional_uses=survey_in.traditional_uses,
        interviewer_id=survey_in.interviewer_id or current_user.user_id,
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


@router.get("/{survey_id}", response_model=EthnoSurveyOut)
def get_ethno_survey(
    survey_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère une enquête ethno-écologique par son identifiant unique UUID."""
    survey = db.query(EthnoSurvey).filter(EthnoSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquête introuvable.")
    return survey


@router.put("/{survey_id}", response_model=EthnoSurveyOut)
def update_ethno_survey(
    survey_id: str,
    survey_in: EthnoSurveyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Mise à jour d'une enquête ethno-écologique."""
    survey = db.query(EthnoSurvey).filter(EthnoSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquête introuvable.")

    update_data = survey_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(survey, field, value)

    db.commit()
    db.refresh(survey)
    return survey


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ethno_survey(
    survey_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> None:
    """Suppression d'une enquête ethno-écologique."""
    survey = db.query(EthnoSurvey).filter(EthnoSurvey.survey_id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquête introuvable.")
    db.delete(survey)
    db.commit()
