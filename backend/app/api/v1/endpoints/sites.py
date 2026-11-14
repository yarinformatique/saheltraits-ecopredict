from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.site import SitePlot
from app.models.user import User
from app.schemas.site import SitePlotCreate, SitePlotOut, SitePlotUpdate

router = APIRouter()


@router.get("", response_model=List[SitePlotOut])
def list_plots(
    climatic_zone: Optional[str] = Query(None, description="Sahélienne, Soudano-Sahélienne, Soudanienne"),
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des placettes d'échantillonnage permanentes."""
    query = db.query(SitePlot)
    if climatic_zone:
        query = query.filter(SitePlot.climatic_zone == climatic_zone)
    if search:
        query = query.filter(
            (SitePlot.site_name.ilike(f"%{search}%"))
            | (SitePlot.plot_id.ilike(f"%{search}%"))
            | (SitePlot.protection_status.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=SitePlotOut, status_code=status.HTTP_201_CREATED)
def create_plot(
    plot_in: SitePlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> Any:
    """Enregistre une nouvelle placette permanente."""
    existing = db.query(SitePlot).filter(SitePlot.plot_id == plot_in.plot_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La placette '{plot_in.plot_id}' existe déjà.",
        )

    plot = SitePlot(
        plot_id=plot_in.plot_id,
        site_name=plot_in.site_name,
        climatic_zone=plot_in.climatic_zone,
        geom=plot_in.geom,
        elevation_m=plot_in.elevation_m,
        slope_deg=plot_in.slope_deg,
        protection_status=plot_in.protection_status,
        fire_frequency_20yr=plot_in.fire_frequency_20yr,
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return plot


@router.get("/{plot_id}", response_model=SitePlotOut)
def get_plot(
    plot_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère une placette par son identifiant unique."""
    plot = db.query(SitePlot).filter(SitePlot.plot_id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Placette introuvable.")
    return plot


@router.put("/{plot_id}", response_model=SitePlotOut)
def update_plot(
    plot_id: str,
    plot_in: SitePlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> Any:
    """Mise à jour des paramètres d'une placette."""
    plot = db.query(SitePlot).filter(SitePlot.plot_id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Placette introuvable.")

    update_data = plot_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plot, field, value)

    db.commit()
    db.refresh(plot)
    return plot


@router.delete("/{plot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plot(
    plot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
) -> None:
    """Suppression d'une placette (Administrateur uniquement)."""
    plot = db.query(SitePlot).filter(SitePlot.plot_id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Placette introuvable.")
    db.delete(plot)
    db.commit()
