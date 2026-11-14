from datetime import date
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.site import SitePlot
from app.models.soil import EnvironmentSoil
from app.models.user import User
from app.schemas.soil import EnvironmentSoilCreate, EnvironmentSoilOut, EnvironmentSoilUpdate

router = APIRouter()


@router.get("", response_model=List[EnvironmentSoilOut])
def list_soil_records(
    plot_id: Optional[str] = None,
    depth_cm: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des analyses de sols physico-chimiques stratifiées par profondeur."""
    query = db.query(EnvironmentSoil)
    if plot_id:
        query = query.filter(EnvironmentSoil.plot_id == plot_id)
    if depth_cm:
        query = query.filter(EnvironmentSoil.depth_cm == depth_cm)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=EnvironmentSoilOut, status_code=status.HTTP_201_CREATED)
def create_soil_record(
    soil_in: EnvironmentSoilCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Enregistre une nouvelle analyse physico-chimique de sol pour une placette."""
    plot = db.query(SitePlot).filter(SitePlot.plot_id == soil_in.plot_id).first()
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Placette '{soil_in.plot_id}' introuvable.",
        )

    soil = EnvironmentSoil(
        plot_id=soil_in.plot_id,
        depth_cm=soil_in.depth_cm,
        clay_pct=soil_in.clay_pct,
        silt_pct=soil_in.silt_pct,
        sand_pct=soil_in.sand_pct,
        ph_h2o=soil_in.ph_h2o,
        organic_carbon_gkg=soil_in.organic_carbon_gkg,
        total_n_gkg=soil_in.total_n_gkg,
        avail_p_mgkg=soil_in.avail_p_mgkg,
        cec_cmolkg=soil_in.cec_cmolkg,
        dry_season_moisture_pct=soil_in.dry_season_moisture_pct,
        sampling_date=soil_in.sampling_date or date.today(),
    )
    db.add(soil)
    db.commit()
    db.refresh(soil)
    return soil


@router.get("/{env_id}", response_model=EnvironmentSoilOut)
def get_soil_record(
    env_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère une analyse de sol par son identifiant unique UUID."""
    soil = db.query(EnvironmentSoil).filter(EnvironmentSoil.env_id == env_id).first()
    if not soil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse de sol introuvable.")
    return soil


@router.put("/{env_id}", response_model=EnvironmentSoilOut)
def update_soil_record(
    env_id: str,
    soil_in: EnvironmentSoilUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Mise à jour des paramètres édaphiques d'une analyse de sol."""
    soil = db.query(EnvironmentSoil).filter(EnvironmentSoil.env_id == env_id).first()
    if not soil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse de sol introuvable.")

    update_data = soil_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(soil, field, value)

    db.commit()
    db.refresh(soil)
    return soil


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_soil_record(
    env_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> None:
    """Suppression d'une analyse de sol."""
    soil = db.query(EnvironmentSoil).filter(EnvironmentSoil.env_id == env_id).first()
    if not soil:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyse de sol introuvable.")
    db.delete(soil)
    db.commit()
