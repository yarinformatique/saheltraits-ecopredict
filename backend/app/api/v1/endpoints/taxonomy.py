from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.taxonomy import Taxonomy
from app.models.user import User
from app.schemas.taxonomy import GBIFMatchResult, TaxonomyCreate, TaxonomyOut, TaxonomyUpdate
from app.services.gbif import GBIFService

router = APIRouter()


@router.get("", response_model=List[TaxonomyOut])
def list_taxa(
    family: Optional[str] = None,
    functional_group: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des taxons enregistrés avec filtres par famille, groupe fonctionnel ou recherche textuelle."""
    query = db.query(Taxonomy)
    if family:
        query = query.filter(Taxonomy.family.ilike(f"%{family}%"))
    if functional_group:
        query = query.filter(Taxonomy.functional_group.ilike(f"%{functional_group}%"))
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Taxonomy.scientific_name.ilike(pattern))
            | (Taxonomy.vernacular_moore.ilike(pattern))
            | (Taxonomy.vernacular_dioula.ilike(pattern))
            | (Taxonomy.vernacular_fulfulde.ilike(pattern))
        )
    return query.offset(skip).limit(limit).all()


@router.get("/gbif/verify", response_model=GBIFMatchResult)
async def verify_gbif_taxonomy(
    scientific_name: str = Query(..., min_length=2, description="Nom scientifique à vérifier sur l'API GBIF"),
) -> Any:
    """Interrogation directe de l'API GBIF Backbone Taxonomy sans enregistrement en base."""
    match_data = await GBIFService.match_species(scientific_name)
    return GBIFMatchResult(**match_data)


@router.post("", response_model=TaxonomyOut, status_code=status.HTTP_201_CREATED)
async def create_taxon(
    taxon_in: TaxonomyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> Any:
    """Enregistre un nouveau taxon en interrogeant automatiquement GBIF Backbone Taxonomy

    pour la standardisation de la nomenclature botanique.
    """
    existing = db.query(Taxonomy).filter(Taxonomy.scientific_name == taxon_in.scientific_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le taxon '{taxon_in.scientific_name}' est déjà répertorié.",
        )

    # Interrogation GBIF automatique
    gbif_data = await GBIFService.match_species(taxon_in.scientific_name)
    accepted_gbif = taxon_in.accepted_name_gbif or gbif_data.get("accepted_name_gbif")
    usage_key = taxon_in.gbif_usage_key or gbif_data.get("usage_key")
    conf_score = taxon_in.gbif_confidence_score or gbif_data.get("confidence")

    taxon = Taxonomy(
        scientific_name=taxon_in.scientific_name,
        accepted_name_gbif=accepted_gbif,
        gbif_usage_key=usage_key,
        gbif_confidence_score=conf_score,
        family=taxon_in.family or gbif_data.get("family") or "Inconnue",
        genus=taxon_in.genus or gbif_data.get("genus") or taxon_in.scientific_name.split()[0],
        vernacular_moore=taxon_in.vernacular_moore,
        vernacular_dioula=taxon_in.vernacular_dioula,
        vernacular_fulfulde=taxon_in.vernacular_fulfulde,
        functional_group=taxon_in.functional_group,
        iucn_status=taxon_in.iucn_status or "LC",
    )
    db.add(taxon)
    db.commit()
    db.refresh(taxon)
    return taxon


@router.get("/{taxon_id}", response_model=TaxonomyOut)
def get_taxon(
    taxon_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère un taxon par son identifiant UUID."""
    taxon = db.query(Taxonomy).filter(Taxonomy.taxon_id == taxon_id).first()
    if not taxon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taxon introuvable.")
    return taxon


@router.put("/{taxon_id}", response_model=TaxonomyOut)
def update_taxon(
    taxon_id: str,
    taxon_in: TaxonomyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> Any:
    """Mise à jour des métadonnées d'un taxon."""
    taxon = db.query(Taxonomy).filter(Taxonomy.taxon_id == taxon_id).first()
    if not taxon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taxon introuvable.")

    update_data = taxon_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(taxon, field, value)

    db.commit()
    db.refresh(taxon)
    return taxon


@router.delete("/{taxon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_taxon(
    taxon_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"])),
) -> None:
    """Suppression d'un taxon (Administrateur uniquement)."""
    taxon = db.query(Taxonomy).filter(Taxonomy.taxon_id == taxon_id).first()
    if not taxon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taxon introuvable.")
    db.delete(taxon)
    db.commit()
