import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, engine

# Description enrichie OpenAPI pour la documentation Swagger/ReDoc
description = """
# SAHELTRAITS-DB : API REST & Entrepôt de Données Centralisé (Couche 3)

**Projet de Thèse de Doctorat :** Écologie Fonctionnelle & Bio-informatique (2027–2030)  
**Université :** Université Joseph Ki-Zerbo (Ouagadougou, Burkina Faso) — ICC (Informatique et Changement Climatique)  
**Maître d'Ouvrage :** YAGO Abdoul Rachide (Doctorant)  

---

### Conformité & Standards Internationaux :
* **FAIR Principles :** Findable, Accessible, Interoperable, Reusable.
* **ETS v1.0 :** *Ecological Trait-data Standard* pour les traits multi-organes des essences sahéliennes.
* **Darwin Core & DwC-Archive :** Interopérabilité globale avec le Système Mondial d'Information sur la Biodiversité (GBIF).
* **PostGIS & OGC Simple Features :** Référence spatiale WGS 84 (EPSG:4326) et flux normalisés GeoJSON.

### Fonctionnalités Clés :
1. **Synchronisation Taxonomique :** Résolution et validation automatique via GBIF Backbone Taxonomy.
2. **Contrôle Qualité Automatisé (QC) :** Détection instantanée des valeurs aberrantes (> 3 sigmas) sur l'espèce et la zone climatique.
3. **Synchronisation Terrain :** Endpoint `POST /api/v1/sync/field-batch` pour collecteurs mobiles avec mode déconnecté.
4. **Exportations Scientifiques :** Formats CSV, JSON et Darwin Core Archive (DwC-A) pour R et Python.
5. **Requêtes Spatiales :** GeoJSON des placettes et arbres avec filtrage par bounding box (BBox) ou rayon kilométrique.
"""

tags_metadata = [
    {
        "name": "Authentification & RBAC",
        "description": "Gestion des jetons JWT et contrôle d'accès basé sur les rôles (Admin, Chercheur, Enquêteur, Lecteur public).",
    },
    {
        "name": "Dimension Taxonomie & GBIF",
        "description": "Référentiel taxonomique botanique avec validation GBIF Backbone et dialectes vernaculaires.",
    },
    {
        "name": "Dimension Sites & Placettes",
        "description": "Placettes permanentes d'échantillonnage dans les gradients bioclimatiques (Sahélien, Soudano-Sahélien, Soudanien).",
    },
    {
        "name": "Faits Individus & QR-Tags",
        "description": "Individus ligneux inventoriés avec balisage QR-Code et coordonnées centimétriques.",
    },
    {
        "name": "Faits Traits Multi-Organes & QC 3-Sigma",
        "description": "Mesures de traits multi-organes (SLA, LDMC, Wood Density, etc.) conformes ETS v1.0 avec suivi QC.",
    },
    {
        "name": "Faits Essais Germinatifs",
        "description": "Écophysiologie de la régénération sous contraintes combinées température et potentiel osmotique.",
    },
    {
        "name": "Faits Environnement & Sols",
        "description": "Analyses physico-chimiques édaphiques par tranche de profondeur.",
    },
    {
        "name": "Faits Enquêtes Ethno-écologiques",
        "description": "Savoirs écologiques traditionnels, dépérissement perçu et résilience des espèces sahéliennes.",
    },
    {
        "name": "Synchronisation Mobile Terrain",
        "description": "Réception transactionnelle des collectes de terrain envoyées par l'application mobile.",
    },
    {
        "name": "Exportations FAIR & Darwin Core",
        "description": "Génération de flux CSV, JSON et archives Darwin Core (DwC-A) pour scripts R et Python.",
    },
    {
        "name": "Requêtes Spatiales GeoJSON",
        "description": "FeatureCollections GeoJSON des placettes et arbres avec filtres spatiaux BBox et proximité.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=description,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS
    if isinstance(settings.ALLOWED_ORIGINS, list)
    else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Mesure du temps de réponse (critère de performance < 300 ms)."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


# Initialisation des tables au démarrage de l'application
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# Enregistrement des routes de l'API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Santé du Système"])
def root():
    """Point d'entrée racine retournant les métadonnées de l'API SAHELTRAITS-DB."""
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "environment": settings.ENVIRONMENT,
        "standards": ["FAIR", "ETS v1.0", "Darwin Core", "PostGIS SRID 4326"],
        "documentation": "/docs",
        "redoc": "/redoc",
        "openapi": f"{settings.API_V1_STR}/openapi.json",
    }


@app.get("/health", tags=["Santé du Système"])
@app.get("/healthz", tags=["Santé du Système"])
@app.get("/ping", tags=["Santé du Système"])
def health_check():
    """Endpoint de monitoring pour les sondes Docker, Render et UptimeRobot."""
    return {"status": "healthy", "timestamp": time.time()}
