import math
from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_roles
from app.models.individual import Individual
from app.models.taxonomy import Taxonomy
from app.models.trait import TraitMeasurement
from app.models.user import User
from app.schemas.trait import (
    TraitMeasurementCreate,
    TraitMeasurementOut,
    TraitMeasurementQCUpdate,
    TraitMeasurementUpdate,
)
from app.services.qc import QCService

router = APIRouter()


@router.get("/measurements", response_model=List[TraitMeasurementOut])
def list_measurements(
    ind_id: Optional[str] = None,
    trait_name_ets: Optional[str] = None,
    organ_sampled: Optional[str] = None,
    qc_flag: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """Liste des mesures de traits fonctionnels avec filtrage par individu, trait, organe ou statut QC."""
    query = db.query(TraitMeasurement)
    if ind_id:
        query = query.filter(TraitMeasurement.ind_id == ind_id)
    if trait_name_ets:
        query = query.filter(TraitMeasurement.trait_name_ets == trait_name_ets)
    if organ_sampled:
        query = query.filter(TraitMeasurement.organ_sampled == organ_sampled)
    if qc_flag:
        query = query.filter(TraitMeasurement.qc_flag == qc_flag)
    return query.offset(skip).limit(limit).all()


@router.post("/measurements", response_model=TraitMeasurementOut, status_code=status.HTTP_201_CREATED)
def create_measurement(
    meas_in: TraitMeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Insère une mesure de trait fonctionnel avec contrôle qualité (QC) 3-sigma automatique."""
    ind = db.query(Individual).filter(Individual.ind_id == meas_in.ind_id).first()
    if not ind:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Individu '{meas_in.ind_id}' introuvable.",
        )

    # Évaluation statistique 3-sigma en amont
    qc_flag, qc_notes = QCService.evaluate_measurement(
        db=db,
        ind_id=meas_in.ind_id,
        trait_name_ets=meas_in.trait_name_ets,
        trait_value=meas_in.trait_value,
    )

    meas = TraitMeasurement(
        ind_id=meas_in.ind_id,
        trait_name_ets=meas_in.trait_name_ets,
        trait_value=meas_in.trait_value,
        unit=meas_in.unit,
        organ_sampled=meas_in.organ_sampled,
        measurement_protocol=meas_in.measurement_protocol,
        instrument_id=meas_in.instrument_id,
        measurement_date=meas_in.measurement_date or date.today(),
        operator_id=meas_in.operator_id or current_user.user_id,
        qc_flag=qc_flag,
        qc_notes=qc_notes,
    )
    db.add(meas)
    db.commit()
    db.refresh(meas)
    return meas


@router.get("/measurements/{meas_id}", response_model=TraitMeasurementOut)
def get_measurement(
    meas_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """Récupère une mesure de trait par son identifiant UUID."""
    meas = db.query(TraitMeasurement).filter(TraitMeasurement.meas_id == meas_id).first()
    if not meas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")
    return meas


@router.put("/measurements/{meas_id}", response_model=TraitMeasurementOut)
def update_measurement(
    meas_id: str,
    meas_in: TraitMeasurementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur", "Enquêteur"])),
) -> Any:
    """Mise à jour d'une mesure de trait et réévaluation QC automatique si la valeur change."""
    meas = db.query(TraitMeasurement).filter(TraitMeasurement.meas_id == meas_id).first()
    if not meas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    update_data = meas_in.model_dump(exclude_unset=True)
    val_changed = "trait_value" in update_data and update_data["trait_value"] != meas.trait_value

    for field, value in update_data.items():
        setattr(meas, field, value)

    if val_changed:
        qc_flag, qc_notes = QCService.evaluate_measurement(
            db=db,
            ind_id=meas.ind_id,
            trait_name_ets=meas.trait_name_ets,
            trait_value=meas.trait_value,
            current_meas_id=meas.meas_id,
        )
        meas.qc_flag = qc_flag
        meas.qc_notes = qc_notes

    db.commit()
    db.refresh(meas)
    return meas


@router.put("/measurements/{meas_id}/qc", response_model=TraitMeasurementOut)
def review_measurement_qc(
    meas_id: str,
    qc_in: TraitMeasurementQCUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> Any:
    """Validation manuelle ou arbitrage scientifique d'une mesure de trait signalée (QC)."""
    meas = db.query(TraitMeasurement).filter(TraitMeasurement.meas_id == meas_id).first()
    if not meas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")

    meas.qc_flag = qc_in.qc_flag
    notes_prefix = f"[Arbitrage par {current_user.full_name} ({current_user.role})] "
    meas.qc_notes = notes_prefix + (qc_in.qc_notes or "Statut mis à jour manuellement.")

    db.commit()
    db.refresh(meas)
    return meas


@router.get("/statistics")
def get_traits_statistics(
    taxon_id: Optional[str] = None,
    trait_name_ets: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Any:
    """Synthèse statistique descriptive (moyenne, écart-type, min, max, n) des traits fonctionnels."""
    query = (
        db.query(TraitMeasurement, Individual, Taxonomy)
        .join(Individual, TraitMeasurement.ind_id == Individual.ind_id)
        .join(Taxonomy, Individual.taxon_id == Taxonomy.taxon_id)
        .filter(TraitMeasurement.qc_flag.notin_(["REJECTED"]))
    )

    if taxon_id:
        query = query.filter(Individual.taxon_id == taxon_id)
    if trait_name_ets:
        query = query.filter(TraitMeasurement.trait_name_ets == trait_name_ets)

    rows = query.all()
    grouped: Dict[str, Dict[str, Any]] = {}

    for meas, ind, taxo in rows:
        key = f"{taxo.scientific_name}::{meas.trait_name_ets}"
        if key not in grouped:
            grouped[key] = {
                "scientific_name": taxo.scientific_name,
                "taxon_id": taxo.taxon_id,
                "trait_name_ets": meas.trait_name_ets,
                "unit": meas.unit,
                "values": [],
            }
        grouped[key]["values"].append(meas.trait_value)

    stats = []
    for k, data in grouped.items():
        vals = data["values"]
        n = len(vals)
        mean_v = sum(vals) / n
        var_v = sum((x - mean_v) ** 2 for x in vals) / (n - 1 if n > 1 else 1)
        std_v = math.sqrt(var_v)
        stats.append({
            "scientific_name": data["scientific_name"],
            "taxon_id": data["taxon_id"],
            "trait_name_ets": data["trait_name_ets"],
            "unit": data["unit"],
            "count": n,
            "mean": round(mean_v, 4),
            "stddev": round(std_v, 4),
            "min": round(min(vals), 4),
            "max": round(max(vals), 4),
        })

    return {"total_traits_analyzed": len(stats), "statistics": stats}


@router.delete("/measurements/{meas_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(
    meas_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Chercheur"])),
) -> None:
    """Suppression d'une mesure de trait."""
    meas = db.query(TraitMeasurement).filter(TraitMeasurement.meas_id == meas_id).first()
    if not meas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesure introuvable.")
    db.delete(meas)
    db.commit()
