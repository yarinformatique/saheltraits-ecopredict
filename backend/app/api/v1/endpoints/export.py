from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.export import ExportService

router = APIRouter()


@router.get("/export")
def export_traits(
    species: Optional[str] = Query(None, description="Filtre par nom d'espèce (scientifique ou accepté GBIF)"),
    climatic_zone: Optional[str] = Query(None, description="Sahélienne, Soudano-Sahélienne, Soudanienne"),
    trait_name: Optional[str] = Query(None, description="Nom de trait standardisé ETS v1.0 (ex: SLA, LDMC, Wood_density)"),
    qc_status: Optional[str] = Query(None, description="Statut QC (VALID, MANUALLY_APPROVED, SUSPECT_OUTLIER_3SIGMA)"),
    format: str = Query("json", pattern="^(json|csv|dwca)$", description="Format d'exportation (json, csv, dwca)"),
    db: Session = Depends(get_db),
):
    """Exportation filtrée et interopérable des données de traits fonctionnels.

    Conforme aux principes FAIR, aux standards ETS v1.0 et Darwin Core Archive (DwC-A).
    Formats supportés :
    - **csv** : Fichier tabulaire standard pour import dans R/Python/Pandas.
    - **json** : Fichier hiérarchique structuré conforme ETS v1.0.
    - **dwca** : Archive ZIP Darwin Core standardisée contenant `meta.xml`, `occurrence.txt` et `measurementorfact.txt`.
    """
    dataset = ExportService.query_traits_dataset(
        db=db,
        species=species,
        climatic_zone=climatic_zone,
        trait_name=trait_name,
        qc_status=qc_status,
    )

    fmt = format.lower()

    if fmt == "csv":
        csv_content = ExportService.to_csv(dataset)
        return Response(
            content=csv_content,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=saheltraits_export.csv"},
        )
    elif fmt == "dwca":
        dwca_bytes = ExportService.to_dwca_zip(dataset)
        return Response(
            content=dwca_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=saheltraits_dwca.zip"},
        )
    else:
        json_content = ExportService.to_json(dataset)
        return Response(
            content=json_content,
            media_type="application/json; charset=utf-8",
        )
