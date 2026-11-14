from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.spatial import SpatialService

router = APIRouter()


@router.get("/plots")
def get_spatial_plots(
    climatic_zone: Optional[str] = Query(None, description="Filtre par zone bioclimatique (Sahélienne, Soudano-Sahélienne, Soudanienne)"),
    min_lon: Optional[float] = Query(None, description="Bounding Box Xmin (longitude min)"),
    min_lat: Optional[float] = Query(None, description="Bounding Box Ymin (latitude min)"),
    max_lon: Optional[float] = Query(None, description="Bounding Box Xmax (longitude max)"),
    max_lat: Optional[float] = Query(None, description="Bounding Box Ymax (latitude max)"),
    near_lon: Optional[float] = Query(None, description="Longitude du point central pour recherche de proximité"),
    near_lat: Optional[float] = Query(None, description="Latitude du point central pour recherche de proximité"),
    radius_km: Optional[float] = Query(None, gt=0, description="Rayon de recherche en kilomètres"),
    db: Session = Depends(get_db),
) -> Any:
    """Requêtes spatiales GeoJSON (FeatureCollection) des placettes permanentes avec filtres spatiaux (BBox ou radial)."""
    bbox = None
    if all(v is not None for v in [min_lon, min_lat, max_lon, max_lat]):
        bbox = [min_lon, min_lat, max_lon, max_lat]

    return SpatialService.get_plots_geojson(
        db=db,
        climatic_zone=climatic_zone,
        bbox=bbox,
        near_lon=near_lon,
        near_lat=near_lat,
        radius_km=radius_km,
    )


@router.get("/trees")
def get_spatial_trees(
    plot_id: Optional[str] = Query(None, description="Filtrer par identifiant de placette"),
    taxon_id: Optional[str] = Query(None, description="Filtrer par taxon UUID"),
    min_health: Optional[int] = Query(None, ge=1, le=5, description="Score sanitaire minimal (1-5)"),
    min_lon: Optional[float] = Query(None, description="Bounding Box Xmin"),
    min_lat: Optional[float] = Query(None, description="Bounding Box Ymin"),
    max_lon: Optional[float] = Query(None, description="Bounding Box Xmax"),
    max_lat: Optional[float] = Query(None, description="Bounding Box Ymax"),
    db: Session = Depends(get_db),
) -> Any:
    """Requêtes spatiales GeoJSON (FeatureCollection) des arbres géolocalisés et tagués par QR-code."""
    bbox = None
    if all(v is not None for v in [min_lon, min_lat, max_lon, max_lat]):
        bbox = [min_lon, min_lat, max_lon, max_lat]

    return SpatialService.get_trees_geojson(
        db=db,
        plot_id=plot_id,
        taxon_id=taxon_id,
        min_health=min_health,
        bbox=bbox,
    )
