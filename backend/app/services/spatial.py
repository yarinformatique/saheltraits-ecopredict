import math
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.individual import Individual
from app.models.site import SitePlot
from app.models.spatial_types import wkt_to_geojson
from app.models.taxonomy import Taxonomy


def haversine_distance_km(
    lon1: float, lat1: float, lon2: float, lat2: float
) -> float:
    """Calcul de la distance géodésique du grand cercle en kilomètres."""
    r = 6371.0  # Rayon terrestre moyen en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def get_centroid_coordinates(
    geom_dict: Optional[Dict[str, Any]],
) -> Optional[List[float]]:
    """Extrait ou calcule le centroïde [lon, lat] à partir d'un dict GeoJSON."""
    if not geom_dict:
        return None
    gtype = geom_dict.get("type")
    coords = geom_dict.get("coordinates")
    if not coords:
        return None

    if gtype == "Point":
        return [float(coords[0]), float(coords[1])]
    elif gtype == "Polygon" and len(coords) > 0:
        ring = coords[0]
        if not ring:
            return None
        lons = [pt[0] for pt in ring]
        lats = [pt[1] for pt in ring]
        return [sum(lons) / len(lons), sum(lats) / len(lats)]
    return None


class SpatialService:
    """Service de requêtes spatiales et de génération de flux GeoJSON (SRID 4326)."""

    @staticmethod
    def get_plots_geojson(
        db: Session,
        climatic_zone: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        near_lon: Optional[float] = None,
        near_lat: Optional[float] = None,
        radius_km: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Génère une FeatureCollection GeoJSON des placettes d'échantillonnage."""
        query = db.query(SitePlot)
        if climatic_zone:
            query = query.filter(SitePlot.climatic_zone == climatic_zone)

        plots = query.all()
        features = []

        for p in plots:
            geom_dict = wkt_to_geojson(p.geom)
            centroid = get_centroid_coordinates(geom_dict)

            # Filtre Bounding Box : [min_lon, min_lat, max_lon, max_lat]
            if bbox and len(bbox) == 4 and centroid:
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (
                    min_lon <= centroid[0] <= max_lon
                    and min_lat <= centroid[1] <= max_lat
                ):
                    continue

            # Filtre Radial de proximité (Haversine)
            if (
                near_lon is not None
                and near_lat is not None
                and radius_km is not None
                and centroid
            ):
                dist = haversine_distance_km(
                    near_lon, near_lat, centroid[0], centroid[1]
                )
                if dist > radius_km:
                    continue

            tree_count = (
                db.query(Individual)
                .filter(Individual.plot_id == p.plot_id)
                .count()
            )

            feature = {
                "type": "Feature",
                "id": p.plot_id,
                "geometry": geom_dict
                if geom_dict
                else {"type": "Point", "coordinates": [0, 0]},
                "properties": {
                    "plot_id": p.plot_id,
                    "site_name": p.site_name,
                    "climatic_zone": p.climatic_zone,
                    "elevation_m": p.elevation_m,
                    "slope_deg": p.slope_deg,
                    "protection_status": p.protection_status,
                    "fire_frequency_20yr": p.fire_frequency_20yr,
                    "tree_count": tree_count,
                    "created_at": p.created_at.isoformat()
                    if p.created_at
                    else None,
                },
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "total_features": len(features),
            "features": features,
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
        }

    @staticmethod
    def get_trees_geojson(
        db: Session,
        plot_id: Optional[str] = None,
        taxon_id: Optional[str] = None,
        min_health: Optional[int] = None,
        bbox: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Génère une FeatureCollection GeoJSON des arbres/individus inventoriés."""
        query = db.query(Individual, Taxonomy).join(
            Taxonomy, Individual.taxon_id == Taxonomy.taxon_id
        )

        if plot_id:
            query = query.filter(Individual.plot_id == plot_id)
        if taxon_id:
            query = query.filter(Individual.taxon_id == taxon_id)
        if min_health:
            query = query.filter(Individual.health_status_score >= min_health)

        results = query.all()
        features = []

        for ind, taxo in results:
            geom_dict = wkt_to_geojson(ind.geom_tree)
            centroid = get_centroid_coordinates(geom_dict)

            if bbox and len(bbox) == 4 and centroid:
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (
                    min_lon <= centroid[0] <= max_lon
                    and min_lat <= centroid[1] <= max_lat
                ):
                    continue

            feature = {
                "type": "Feature",
                "id": ind.ind_id,
                "geometry": geom_dict
                if geom_dict
                else {"type": "Point", "coordinates": [0, 0]},
                "properties": {
                    "ind_id": ind.ind_id,
                    "plot_id": ind.plot_id,
                    "taxon_id": ind.taxon_id,
                    "scientific_name": taxo.scientific_name,
                    "family": taxo.family,
                    "vernacular_moore": taxo.vernacular_moore,
                    "qr_code_tag": ind.qr_code_tag,
                    "dbh_cm": ind.dbh_cm,
                    "total_height_m": ind.total_height_m,
                    "crown_diameter_m": ind.crown_diameter_m,
                    "canopy_position": ind.canopy_position,
                    "health_status_score": ind.health_status_score,
                },
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "total_features": len(features),
            "features": features,
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
        }
