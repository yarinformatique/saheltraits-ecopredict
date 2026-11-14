from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.individual import Individual
from app.models.site import SitePlot
from app.models.taxonomy import Taxonomy
from app.models.user import User
from app.schemas.individual import IndividualCreate, IndividualOut, IndividualUpdate

router = APIRouter()


@router.get("", response_model=List[IndividualOut])
def list_individuals(
    plot_id: Optional[str] = None,
    taxon_id: Optional[str] = None,
    qr_code_tag: Optional[str] = None,
    min_health: Optional[int] = Query(None, ge=1, le=5),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des individus/arbres inventoriés avec filtres par placette, taxon ou tag QR-code."""
    query = db.query(Individual)
    if plot_id:
        query = query.filter(Individual.plot_id == plot_id)
    if taxon_id:
        query = query.filter(Individual.taxon_id == taxon_id)
    if qr_code_tag:
        query = query.filter(Individual.qr_code_tag == qr_code_tag)
    if min_health:
        query = query.filter(Individual.health_status_score >= min_health)
    return query.offset(skip).limit(limit).all()


@router.get("/qr/{qr_code}", response_model=IndividualOut)
def get_individual_by_qr(
    qr_code: str,
    db: Session = Depends(get_db),
) -> Any:
    """Recherche instantanée d'un arbre à partir du tag QR-code scanné sur le terrain."""
    ind = db.query(Individual).filter(Individual.qr_code_tag == qr_code).first()
    if not ind:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun individu répertorié avec le tag QR '{qr_code}'.",
        )
    return ind


@router.post("", response_model=IndividualOut, status_code=status.HTTP_201_CREATED)
def create_individual(
    ind_in: IndividualCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Enregistre un nouvel individu inventorié avec son QR-code et ses coordonnées géographiques."""
    # Vérification plot_id et taxon_id
    if not db.query(SitePlot).filter(SitePlot.plot_id == ind_in.plot_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Placette spécifiée introuvable.")
    if not db.query(Taxonomy).filter(Taxonomy.taxon_id == ind_in.taxon_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Taxon spécifié introuvable.")

    existing_qr = db.query(Individual).filter(Individual.qr_code_tag == ind_in.qr_code_tag).first()
    if existing_qr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le QR-Code tag '{ind_in.qr_code_tag}' est déjà assigné à un autre individu.",
        )

    ind = Individual(
        plot_id=ind_in.plot_id,
        taxon_id=ind_in.taxon_id,
        qr_code_tag=ind_in.qr_code_tag,
        dbh_cm=ind_in.dbh_cm,
        total_height_m=ind_in.total_height_m,
        crown_diameter_m=ind_in.crown_diameter_m,
        canopy_position=ind_in.canopy_position,
        health_status_score=ind_in.health_status_score,
        geom_tree=ind_in.geom_tree,
    )
    db.add(ind)
    db.commit()
    db.refresh(ind)
    return ind


@router.get("/{ind_id}", response_model=IndividualOut)
def get_individual(
    ind_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère un individu par son identifiant unique UUID."""
    ind = db.query(Individual).filter(Individual.ind_id == ind_id).first()
    if not ind:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Individu introuvable.")
    return ind


@router.put("/{ind_id}", response_model=IndividualOut)
def update_individual(
    ind_id: str,
    ind_in: IndividualUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Mise à jour des dendrométries ou du statut sanitaire d'un individu."""
    ind = db.query(Individual).filter(Individual.ind_id == ind_id).first()
    if not ind:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Individu introuvable.")

    update_data = ind_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ind, field, value)

    db.commit()
    db.refresh(ind)
    return ind


@router.delete("/{ind_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_individual(
    ind_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
) -> None:
    """Suppression d'un individu inventorié (Administrateur uniquement)."""
    ind = db.query(Individual).filter(Individual.ind_id == ind_id).first()
    if not ind:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Individu introuvable.")
    db.delete(ind)
    db.commit()
