from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.germination import SeedGermination
from app.models.individual import Individual
from app.models.user import User
from app.schemas.germination import SeedGerminationCreate, SeedGerminationOut, SeedGerminationUpdate

router = APIRouter()


@router.get("", response_model=List[SeedGerminationOut])
def list_germination_trials(
    ind_id: Optional[str] = None,
    seed_batch_qr: Optional[str] = None,
    osmotic_potential_mpa: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des essais germinatifs sous contrainte hydrique et thermique."""
    query = db.query(SeedGermination)
    if ind_id:
        query = query.filter(SeedGermination.ind_id == ind_id)
    if seed_batch_qr:
        query = query.filter(SeedGermination.seed_batch_qr == seed_batch_qr)
    if osmotic_potential_mpa is not None:
        query = query.filter(SeedGermination.osmotic_potential_mpa == osmotic_potential_mpa)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=SeedGerminationOut, status_code=status.HTTP_201_CREATED)
def create_germination_trial(
    trial_in: SeedGerminationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Enregistre un essai germinatif en étuve (avec calcul automatique du pourcentage final de germination GP%)."""
    ind = db.query(Individual).filter(Individual.ind_id == trial_in.ind_id).first()
    if not ind:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Individu '{trial_in.ind_id}' introuvable.",
        )

    if trial_in.germinated_count > trial_in.total_seeds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nombre de graines germées ne peut excéder le nombre total de graines semées.",
        )

    gp_pct = (trial_in.germinated_count / trial_in.total_seeds) * 100.0 if trial_in.total_seeds > 0 else 0.0

    trial = SeedGermination(
        ind_id=trial_in.ind_id,
        seed_batch_qr=trial_in.seed_batch_qr,
        temp_regime_c=trial_in.temp_regime_c,
        osmotic_potential_mpa=trial_in.osmotic_potential_mpa,
        pretreatment_type=trial_in.pretreatment_type,
        total_seeds=trial_in.total_seeds,
        germinated_count=trial_in.germinated_count,
        t50_days=trial_in.t50_days,
        final_gp_pct=round(gp_pct, 2),
    )
    db.add(trial)
    db.commit()
    db.refresh(trial)
    return trial


@router.get("/{germ_id}", response_model=SeedGerminationOut)
def get_germination_trial(
    germ_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère un essai de germination par son identifiant unique UUID."""
    trial = db.query(SeedGermination).filter(SeedGermination.germ_id == germ_id).first()
    if not trial:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essai germinatif introuvable.")
    return trial


@router.put("/{germ_id}", response_model=SeedGerminationOut)
def update_germination_trial(
    germ_id: str,
    trial_in: SeedGerminationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Mise à jour des comptages ou conditions d'un essai germinatif."""
    trial = db.query(SeedGermination).filter(SeedGermination.germ_id == germ_id).first()
    if not trial:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essai germinatif introuvable.")

    update_data = trial_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trial, field, value)

    if trial.total_seeds > 0:
        trial.final_gp_pct = round((trial.germinated_count / trial.total_seeds) * 100.0, 2)

    db.commit()
    db.refresh(trial)
    return trial


@router.delete("/{germ_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_germination_trial(
    germ_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> None:
    """Suppression d'un essai germinatif."""
    trial = db.query(SeedGermination).filter(SeedGermination.germ_id == germ_id).first()
    if not trial:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Essai germinatif introuvable.")
    db.delete(trial)
    db.commit()
