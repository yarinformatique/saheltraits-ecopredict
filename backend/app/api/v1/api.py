from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    ecopredict,
    export,
    germination,
    individuals,
    sites,
    soil,
    spatial,
    surveys,
    sync,
    taxonomy,
    traits,
)

api_router = APIRouter()

# Enregistrement des sous-routeurs thématiques
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification & RBAC"])
api_router.include_router(taxonomy.router, prefix="/taxonomy", tags=["Dimension Taxonomie & GBIF"])
api_router.include_router(sites.router, prefix="/sites", tags=["Dimension Sites & Placettes"])
api_router.include_router(individuals.router, prefix="/individuals", tags=["Faits Individus & QR-Tags"])
api_router.include_router(traits.router, prefix="/traits", tags=["Faits Traits Multi-Organes & QC 3-Sigma"])
api_router.include_router(germination.router, prefix="/germination", tags=["Faits Essais Germinatifs"])
api_router.include_router(soil.router, prefix="/environment/soil", tags=["Faits Environnement & Sols"])
api_router.include_router(surveys.router, prefix="/surveys/ethno", tags=["Faits Enquêtes Ethno-écologiques"])
api_router.include_router(sync.router, prefix="/sync", tags=["Synchronisation Mobile Terrain"])
api_router.include_router(export.router, prefix="/traits", tags=["Exportations FAIR & Darwin Core"])
api_router.include_router(spatial.router, prefix="/spatial", tags=["Requêtes Spatiales GeoJSON"])
api_router.include_router(ecopredict.router, prefix="/ecopredict", tags=["Simulateur EcoPredict & CMIP6"])
