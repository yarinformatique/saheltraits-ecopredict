import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import Text, TypeDecorator


def point_to_wkt(lon: float, lat: float) -> str:
    """Format longitude and latitude as WKT Point with SRID 4326."""
    return f"SRID=4326;POINT({lon} {lat})"


def wkt_to_geojson(wkt_str: Optional[str]) -> Optional[Dict[str, Any]]:
    """Convert WKT or internal geom representation to GeoJSON geometry dictionary."""
    if not wkt_str:
        return None

    # Handle SRID prefix e.g. "SRID=4326;POINT(-1.5 12.3)" or "POINT(-1.5 12.3)"
    clean_wkt = re.sub(r"^SRID=\d+;", "", str(wkt_str).strip())

    # Point parsing
    point_match = re.match(
        r"^POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)$", clean_wkt, re.IGNORECASE
    )
    if point_match:
        lon, lat = float(point_match.group(1)), float(point_match.group(2))
        return {"type": "Point", "coordinates": [lon, lat]}

    # Polygon parsing
    poly_match = re.match(
        r"^POLYGON\s*\(\(\s*(.+)\s*\)\)$", clean_wkt, re.IGNORECASE
    )
    if poly_match:
        pairs = poly_match.group(1).split(",")
        coords = []
        for pair in pairs:
            parts = pair.strip().split()
            if len(parts) >= 2:
                coords.append([float(parts[0]), float(parts[1])])
        return {"type": "Polygon", "coordinates": [coords]}

    # If it's already JSON string
    try:
        data = json.loads(wkt_str)
        if isinstance(data, dict) and "type" in data:
            return data
    except Exception:
        pass

    return {"type": "Geometry", "raw": wkt_str}


class SpatialPoint(TypeDecorator):
    """SQLAlchemy TypeDecorator for Spatial Point (SRID 4326).

    Uses GeoAlchemy2 Geometry('POINT', 4326) on PostgreSQL/PostGIS,
    and Text WKT storage on SQLite/in-memory test databases.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from geoalchemy2 import Geometry

                return dialect.type_descriptor(
                    Geometry(geometry_type="POINT", srid=4326)
                )
            except ImportError:
                return dialect.type_descriptor(Text())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            # If GeoJSON dict passed
            coords = value.get("coordinates")
            if coords and len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                return f"POINT({lon} {lat})"
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


class SpatialGeometry(TypeDecorator):
    """SQLAlchemy TypeDecorator for Spatial Geometry / Polygon (SRID 4326).

    Uses GeoAlchemy2 Geometry('GEOMETRY', 4326) on PostgreSQL/PostGIS,
    and Text WKT storage on SQLite.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from geoalchemy2 import Geometry

                return dialect.type_descriptor(
                    Geometry(geometry_type="GEOMETRY", srid=4326)
                )
            except ImportError:
                return dialect.type_descriptor(Text())
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            # GeoJSON dict
            if value.get("type") == "Point":
                coords = value.get("coordinates", [])
                return f"POINT({coords[0]} {coords[1]})"
            elif value.get("type") == "Polygon":
                rings = value.get("coordinates", [])
                if rings:
                    ring_str = ", ".join(
                        f"{pt[0]} {pt[1]}" for pt in rings[0]
                    )
                    return f"POLYGON(({ring_str}))"
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)
