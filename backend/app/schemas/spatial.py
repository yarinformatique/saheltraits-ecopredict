from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: Optional[str] = None
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature] = Field(default_factory=list)
    total_features: int = 0
    metadata: Optional[Dict[str, Any]] = None
