"""
Module EcoPredict 2050–2080 : Simulateur Climatique et Outil d'Aide à la Décision
Intègre les données CMIP6 (SSP2-4.5 et SSP5-8.5), les modèles SDM / biomod2,
et le diagnostic par coordonnées GPS ou polygone de site de reboisement.
"""

import math
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.taxonomy import Taxonomy

router = APIRouter()

# Données synthétiques et calibrations issues du Pipeline (Module 4)
SPECIES_CLIMATE_ENVELOPES = {
    "Balanites aegyptiaca (L.) Delile": {
        "opt_rain": (200, 750),
        "opt_temp": (27.0, 32.5),
        "drought_tolerance": 0.95,
        "salinity_tolerance": 0.85,
        "fire_tolerance": 0.70,
        "ssp245_2050": {"change_pct": 3.8, "vuln_idx": 0.0, "risk": "Résiliente / Stable"},
        "ssp245_2080": {"change_pct": -4.8, "vuln_idx": 4.8, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -10.6, "vuln_idx": 10.6, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": 2.2, "vuln_idx": 0.0, "risk": "Résiliente / Stable"},
        "rationale": "Système racinaire pivotant hyper-profond (> 15m), feuilles coriaces à cuticule cireuse et épines photosynthétiques réduisant l'évapotranspiration."
    },
    "Adansonia digitata L.": {
        "opt_rain": (400, 950),
        "opt_temp": (25.5, 30.5),
        "drought_tolerance": 0.80,
        "salinity_tolerance": 0.40,
        "fire_tolerance": 0.85,
        "ssp245_2050": {"change_pct": -13.2, "vuln_idx": 13.2, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -16.0, "vuln_idx": 16.0, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -23.6, "vuln_idx": 23.6, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -34.7, "vuln_idx": 34.7, "risk": "Modérément Vulnérable"},
        "rationale": "Trunk parenchyma stockant d'immenses réserves d'eau (pachycaulie) mais sensible aux sécheresses pluriannuelles extrêmes affaiblissant les méga-arbres."
    },
    "Faidherbia albida (Delile) A.Chev.": {
        "opt_rain": (350, 900),
        "opt_temp": (26.0, 31.0),
        "drought_tolerance": 0.85,
        "salinity_tolerance": 0.65,
        "fire_tolerance": 0.60,
        "ssp245_2050": {"change_pct": -13.1, "vuln_idx": 13.1, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -13.4, "vuln_idx": 13.4, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -25.3, "vuln_idx": 25.3, "risk": "Modérément Vulnérable"},
        "ssp585_2080": {"change_pct": -47.0, "vuln_idx": 47.0, "risk": "Modérément Vulnérable"},
        "rationale": "Phénologie inversée bénéfique pour l'agroforesterie; nécessite cependant une nappe phréatique accessible (< 20m) menacée par l'aridification."
    },
    "Vachellia tortilis (Forssk.) Galasso & Banfi": {
        "opt_rain": (150, 600),
        "opt_temp": (27.5, 33.0),
        "drought_tolerance": 0.98,
        "salinity_tolerance": 0.90,
        "fire_tolerance": 0.50,
        "ssp245_2050": {"change_pct": -3.3, "vuln_idx": 3.3, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": 3.6, "vuln_idx": 0.0, "risk": "Résiliente / Stable"},
        "ssp585_2050": {"change_pct": -4.2, "vuln_idx": 4.2, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -3.6, "vuln_idx": 3.6, "risk": "Faiblement Vulnérable"},
        "rationale": "Espèce pionnière hyper-xérique du Sahel strict; taux de survie très élevé même sous chute pluviométrique drastique."
    },
    "Combretum glutinosum Perr. ex DC.": {
        "opt_rain": (400, 1000),
        "opt_temp": (26.0, 31.0),
        "drought_tolerance": 0.78,
        "salinity_tolerance": 0.45,
        "fire_tolerance": 0.92,
        "ssp245_2050": {"change_pct": -11.2, "vuln_idx": 11.2, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -9.0, "vuln_idx": 9.0, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -18.9, "vuln_idx": 18.9, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -43.8, "vuln_idx": 43.8, "risk": "Modérément Vulnérable"},
        "rationale": "Capacité remarquable de rejet de souche après passage des feux de brousse répétitifs; bois dense et feuillage glutineux."
    },
    "Ziziphus mauritiana Lam.": {
        "opt_rain": (250, 850),
        "opt_temp": (26.5, 32.0),
        "drought_tolerance": 0.90,
        "salinity_tolerance": 0.75,
        "fire_tolerance": 0.65,
        "ssp245_2050": {"change_pct": -10.0, "vuln_idx": 10.0, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -15.3, "vuln_idx": 15.3, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -16.5, "vuln_idx": 16.5, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -40.2, "vuln_idx": 40.2, "risk": "Modérément Vulnérable"},
        "rationale": "Arbuste xérophyte épineux à forte germination sous contrainte osmotique (PEG 6000); ressource vivrière stratégique."
    },
    "Sclerocarya birrea (A.Rich.) Hochst.": {
        "opt_rain": (450, 1100),
        "opt_temp": (25.0, 30.0),
        "drought_tolerance": 0.75,
        "salinity_tolerance": 0.35,
        "fire_tolerance": 0.70,
        "ssp245_2050": {"change_pct": -10.6, "vuln_idx": 10.6, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -8.3, "vuln_idx": 8.3, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -23.6, "vuln_idx": 23.6, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -35.9, "vuln_idx": 35.9, "risk": "Modérément Vulnérable"},
        "rationale": "Arbre fruitier de savane résistant mais avec régression marquée sur les sols superficiels latéritiques en zone nord."
    },
    "Tamarindus indica L.": {
        "opt_rain": (400, 1200),
        "opt_temp": (25.0, 31.0),
        "drought_tolerance": 0.82,
        "salinity_tolerance": 0.70,
        "fire_tolerance": 0.75,
        "ssp245_2050": {"change_pct": -14.8, "vuln_idx": 14.8, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -10.5, "vuln_idx": 10.5, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -24.1, "vuln_idx": 24.1, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -37.8, "vuln_idx": 37.8, "risk": "Modérément Vulnérable"},
        "rationale": "Feuillage sempervirent protecteur et bois à haute densité (0.75 g/cm³); bonne plasticité phénotypique."
    },
    "Senegalia senegal (L.) Britton": {
        "opt_rain": (200, 700),
        "opt_temp": (27.0, 33.0),
        "drought_tolerance": 0.94,
        "salinity_tolerance": 0.60,
        "fire_tolerance": 0.55,
        "ssp245_2050": {"change_pct": -12.2, "vuln_idx": 12.2, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -10.0, "vuln_idx": 10.0, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -15.4, "vuln_idx": 15.4, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -36.9, "vuln_idx": 36.9, "risk": "Modérément Vulnérable"},
        "rationale": "Producteur de gomme arabique; pilier de la Grande Muraille Verte pour la stabilisation des dunes et cordons pierreux."
    },
    "Parkia biglobosa (Jacq.) R.Br. ex G.Don": {
        "opt_rain": (550, 1300),
        "opt_temp": (25.0, 30.0),
        "drought_tolerance": 0.68,
        "salinity_tolerance": 0.30,
        "fire_tolerance": 0.65,
        "ssp245_2050": {"change_pct": -10.9, "vuln_idx": 10.9, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -17.7, "vuln_idx": 17.7, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -23.6, "vuln_idx": 23.6, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -32.3, "vuln_idx": 32.3, "risk": "Modérément Vulnérable"},
        "rationale": "Arbre agroforestier clé (Néré); vulnérabilité accrue aux hausses thermiques au-dessus du 13ème parallèle nord."
    },
    "Pterocarpus erinaceus Poir.": {
        "opt_rain": (600, 1400),
        "opt_temp": (24.0, 29.5),
        "drought_tolerance": 0.50,
        "salinity_tolerance": 0.20,
        "fire_tolerance": 0.70,
        "ssp245_2050": {"change_pct": -21.1, "vuln_idx": 21.1, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -21.3, "vuln_idx": 21.3, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -33.2, "vuln_idx": 33.2, "risk": "Modérément Vulnérable"},
        "ssp585_2080": {"change_pct": -50.5, "vuln_idx": 50.5, "risk": "Extrêmement Vulnérable"},
        "rationale": "Essence soudanienne menacée (UICN EN); régression thermique sévère prévue (> 50% de perte d'aire sous SSP5-8.5)."
    },
    "Anogeissus leiocarpa (DC.) Guill. & Perr.": {
        "opt_rain": (500, 1250),
        "opt_temp": (25.5, 30.5),
        "drought_tolerance": 0.76,
        "salinity_tolerance": 0.40,
        "fire_tolerance": 0.60,
        "ssp245_2050": {"change_pct": -9.0, "vuln_idx": 9.0, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -8.5, "vuln_idx": 8.5, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -19.4, "vuln_idx": 19.4, "risk": "Faiblement Vulnérable"},
        "ssp585_2080": {"change_pct": -39.8, "vuln_idx": 39.8, "risk": "Modérément Vulnérable"},
        "rationale": "Bois lourd résistant mais très sensible au dépérissement hydrique en bordure septentrionale de son aire."
    },
    "Boscia senegalensis (Pers.) Lam.": {
        "opt_rain": (100, 500),
        "opt_temp": (28.0, 34.0),
        "drought_tolerance": 0.99,
        "salinity_tolerance": 0.85,
        "fire_tolerance": 0.75,
        "ssp245_2050": {"change_pct": 5.2, "vuln_idx": 0.0, "risk": "Résiliente / Stable"},
        "ssp245_2080": {"change_pct": 8.1, "vuln_idx": 0.0, "risk": "Expansion d'aire"},
        "ssp585_2050": {"change_pct": 4.6, "vuln_idx": 0.0, "risk": "Résiliente / Stable"},
        "ssp585_2080": {"change_pct": 12.4, "vuln_idx": 0.0, "risk": "Expansion d'aire"},
        "rationale": "Championne absolue d'adaptation à l'aridité extrême; SLA minimal (7.9 mm²/mg) et LDMC très élevé (480 mg/g)."
    },
    "Vitellaria paradoxa C.F.Gaertn.": {
        "opt_rain": (600, 1300),
        "opt_temp": (24.5, 30.0),
        "drought_tolerance": 0.65,
        "salinity_tolerance": 0.25,
        "fire_tolerance": 0.80,
        "ssp245_2050": {"change_pct": -15.4, "vuln_idx": 15.4, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -19.8, "vuln_idx": 19.8, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -28.6, "vuln_idx": 28.6, "risk": "Modérément Vulnérable"},
        "ssp585_2080": {"change_pct": -46.2, "vuln_idx": 46.2, "risk": "Modérément Vulnérable"},
        "rationale": "Arbre du Karité; repli vers le sud-ouest en raison des déficits pluviométriques et hausses des températures maximales."
    },
    "Khaya senegalensis (Desr.) A.Juss.": {
        "opt_rain": (650, 1400),
        "opt_temp": (24.0, 29.5),
        "drought_tolerance": 0.52,
        "salinity_tolerance": 0.20,
        "fire_tolerance": 0.60,
        "ssp245_2050": {"change_pct": -18.5, "vuln_idx": 18.5, "risk": "Faiblement Vulnérable"},
        "ssp245_2080": {"change_pct": -22.0, "vuln_idx": 22.0, "risk": "Faiblement Vulnérable"},
        "ssp585_2050": {"change_pct": -34.8, "vuln_idx": 34.8, "risk": "Modérément Vulnérable"},
        "ssp585_2080": {"change_pct": -52.4, "vuln_idx": 52.4, "risk": "Extrêmement Vulnérable"},
        "rationale": "Cailcédrat riparien; risque très élevé de mortalité en cas d'assèchement des galeries forestières."
    }
}


def estimate_climate_at_coord(lat: float, lon: float, horizon: str, scenario: str) -> Dict[str, Any]:
    """
    Modèle d'interpolation bioclimatique simplifié pour le Burkina Faso (grille CMIP6).
    Latitude: 9.4°N à 15.1°N
    Longitude: -5.5°W à 2.4°E
    """
    # Gradient pluviométrique nord-sud typique du Burkina Faso (350mm à Dori, 1150mm à Banfora)
    # Lat 15.0 -> ~380 mm, Lat 10.0 -> ~1050 mm
    lat_factor = max(0.0, min(1.0, (15.2 - lat) / 5.2))
    base_precip = 350.0 + (lat_factor * 750.0) - (abs(lon + 1.5) * 15.0)
    base_temp = 30.5 - (lat_factor * 3.5)

    if lat >= 13.8:
        zone = "Sahélienne"
    elif lat >= 11.8:
        zone = "Soudano-Sahélienne"
    else:
        zone = "Soudanienne"

    # Changements climatiques CMIP6 selon scénario et horizon
    if horizon == "actuel":
        delta_t = 0.0
        delta_p_pct = 0.0
    elif horizon == "2050":
        if scenario == "ssp245":
            delta_t = 1.6
            delta_p_pct = -4.5
        else: # ssp585
            delta_t = 2.4
            delta_p_pct = -9.2
    else: # 2080
        if scenario == "ssp245":
            delta_t = 2.2
            delta_p_pct = -7.0
        else: # ssp585
            delta_t = 4.3
            delta_p_pct = -18.5

    fut_temp = round(base_temp + delta_t, 2)
    fut_precip = round(base_precip * (1.0 + delta_p_pct / 100.0), 1)

    # Indice d'aridité de Thornthwaite / UNEP simplifié (P / PET)
    # PET approchée par formule de Thornthwaite simplifiée
    pet_mm = max(1200.0, 1400.0 + (fut_temp - 26.0) * 85.0)
    aridity_index = round(fut_precip / pet_mm, 3)

    return {
        "zone": zone,
        "base_temp_c": round(base_temp, 2),
        "base_precip_mm": round(base_precip, 1),
        "future_temp_c": fut_temp,
        "future_precip_mm": fut_precip,
        "delta_temp_c": delta_t,
        "delta_precip_pct": delta_p_pct,
        "pet_mm": round(pet_mm, 1),
        "aridity_index": aridity_index,
    }


def compute_suitability_score(species_name: str, climate: Dict[str, Any], horizon: str, scenario: str) -> Dict[str, Any]:
    envelope = SPECIES_CLIMATE_ENVELOPES.get(species_name)
    if not envelope:
        # Fallback générique
        return {
            "survival_score": 65.0,
            "category": "Modéré / Surveillance",
            "recommendation": "Surveillance",
            "rationale": "Espèce sahélienne à tolérance thermique intermédiaire."
        }

    opt_p_min, opt_p_max = envelope["opt_rain"]
    opt_t_min, opt_t_max = envelope["opt_temp"]
    fut_p = climate["future_precip_mm"]
    fut_t = climate["future_temp_c"]

    # Distance normalisée à l'optimum
    p_penalty = 0.0
    if fut_p < opt_p_min:
        p_penalty = min(50.0, ((opt_p_min - fut_p) / opt_p_min) * 70.0 * (1.0 - envelope["drought_tolerance"]))
    elif fut_p > opt_p_max:
        p_penalty = min(25.0, ((fut_p - opt_p_max) / opt_p_max) * 30.0)

    t_penalty = 0.0
    if fut_t > opt_t_max:
        t_penalty = min(40.0, ((fut_t - opt_t_max) / 3.0) * 50.0 * (1.0 - envelope["drought_tolerance"]))

    # Score de survie entre 0 et 100
    base_score = 100.0 - p_penalty - t_penalty

    # Intégrer les projections CMIP6 si horizon futur
    if horizon != "actuel":
        scen_key = f"{scenario}_{horizon}"
        cmip_data = envelope.get(scen_key, {})
        vuln = cmip_data.get("vuln_idx", 15.0)
        base_score = base_score * (1.0 - (vuln / 200.0))

    score = round(max(5.0, min(99.0, base_score)), 1)

    if score >= 75.0:
        cat = "Hautement Recommandée"
        rec = "Prioritaire pour reboisement"
    elif score >= 50.0:
        cat = "Favorable / Tolérante"
        rec = "Adaptée sous suivi hydrique initial"
    elif score >= 35.0:
        cat = "Vigilance / Risque Modéré"
        rec = "À associer en petites proportions ou micro-refuges"
    else:
        cat = "À Haut Risque / Maladaptée"
        rec = "Non recommandée dans cette zone sous ce scénario"

    return {
        "survival_score": score,
        "category": cat,
        "recommendation": rec,
        "rationale": envelope["rationale"],
        "drought_tolerance": envelope["drought_tolerance"],
        "fire_tolerance": envelope["fire_tolerance"],
    }


class PointDiagnosisRequest(BaseModel):
    latitude: float = Field(..., ge=9.0, le=15.5, description="Latitude WGS84 du point au Burkina Faso")
    longitude: float = Field(..., ge=-6.0, le=3.0, description="Longitude WGS84 du point au Burkina Faso")
    horizon: str = Field("2050", description="actuel, 2050 ou 2080")
    scenario: str = Field("ssp245", description="ssp245 ou ssp585")


class PolygonDiagnosisRequest(BaseModel):
    coordinates: List[List[float]] = Field(..., description="Liste de coordonnées [lon, lat] fermant le polygone")
    site_name: Optional[str] = Field("Site de Reboisement", description="Nom du périmètre")
    horizon: str = Field("2050", description="actuel, 2050 ou 2080")
    scenario: str = Field("ssp245", description="ssp245 ou ssp585")


@router.get("/projections")
def get_vulnerability_projections(
    scenario: Optional[str] = Query(None, description="ssp245 ou ssp585"),
    horizon: Optional[str] = Query(None, description="2050 ou 2080"),
    db: Session = Depends(get_db),
) -> Any:
    """Retourne la synthèse des projections de vulnérabilité CMIP6 par espèce."""
    results = []
    taxa = db.query(Taxonomy).all()
    taxa_map = {t.scientific_name: t for t in taxa}

    for sp_name, data in SPECIES_CLIMATE_ENVELOPES.items():
        taxo = taxa_map.get(sp_name)
        scenarios_to_check = [("ssp245", "2050"), ("ssp245", "2080"), ("ssp585", "2050"), ("ssp585", "2080")]
        for sc, hz in scenarios_to_check:
            if scenario and sc != scenario:
                continue
            if horizon and hz != str(horizon):
                continue

            k = f"{sc}_{hz}"
            cmip = data.get(k, {})
            results.append({
                "species": sp_name,
                "family": taxo.family if taxo else "Inconnue",
                "vernacular_moore": taxo.vernacular_moore if taxo else None,
                "vernacular_dioula": taxo.vernacular_dioula if taxo else None,
                "vernacular_fulfulde": taxo.vernacular_fulfulde if taxo else None,
                "functional_group": taxo.functional_group if taxo else None,
                "scenario": sc,
                "horizon": hz,
                "range_change_pct": cmip.get("change_pct", 0.0),
                "vulnerability_index": cmip.get("vuln_idx", 0.0),
                "risk_category": cmip.get("risk", "Stable"),
                "rationale": data.get("rationale", "")
            })

    return {"total": len(results), "projections": results}


@router.post("/diagnose-point")
def diagnose_point(req: PointDiagnosisRequest, db: Session = Depends(get_db)) -> Any:
    """Diagnostic climatique et recommandations d'espèces pour des coordonnées GPS précises."""
    climate = estimate_climate_at_coord(req.latitude, req.longitude, req.horizon, req.scenario)
    taxa = db.query(Taxonomy).all()
    taxa_names = [t.scientific_name for t in taxa]

    # Pour chaque espèce connue ou dans SPECIES_CLIMATE_ENVELOPES
    all_species = list(set(taxa_names + list(SPECIES_CLIMATE_ENVELOPES.keys())))
    species_rankings = []

    for sp_name in all_species:
        taxo = next((t for t in taxa if t.scientific_name == sp_name), None)
        diag = compute_suitability_score(sp_name, climate, req.horizon, req.scenario)
        species_rankings.append({
            "taxon_id": taxo.taxon_id if taxo else None,
            "scientific_name": sp_name,
            "family": taxo.family if taxo else "Inconnue",
            "vernacular_moore": taxo.vernacular_moore if taxo else None,
            "vernacular_dioula": taxo.vernacular_dioula if taxo else None,
            "vernacular_fulfulde": taxo.vernacular_fulfulde if taxo else None,
            "functional_group": taxo.functional_group if taxo else None,
            "survival_score": diag["survival_score"],
            "category": diag["category"],
            "recommendation": diag["recommendation"],
            "rationale": diag["rationale"],
            "drought_tolerance": diag.get("drought_tolerance", 0.7),
            "fire_tolerance": diag.get("fire_tolerance", 0.6),
        })

    # Tri par score de survie décroissant
    species_rankings.sort(key=lambda x: x["survival_score"], reverse=True)

    recommended = [s for s in species_rankings if s["survival_score"] >= 75.0]
    moderate = [s for s in species_rankings if 50.0 <= s["survival_score"] < 75.0]
    at_risk = [s for s in species_rankings if s["survival_score"] < 50.0]

    return {
        "query": {
            "latitude": req.latitude,
            "longitude": req.longitude,
            "horizon": req.horizon,
            "scenario": req.scenario,
        },
        "climate_diagnostic": climate,
        "species_ranking": species_rankings,
        "summary": {
            "total_evaluated": len(species_rankings),
            "recommended_count": len(recommended),
            "moderate_count": len(moderate),
            "at_risk_count": len(at_risk),
            "top_choice": recommended[0]["scientific_name"] if recommended else None,
        }
    }


@router.post("/diagnose-polygon")
def diagnose_polygon(req: PolygonDiagnosisRequest, db: Session = Depends(get_db)) -> Any:
    """Diagnostic pour un polygone ou périmètre de reboisement (calcul du centroïde et agrégation)."""
    coords = req.coordinates
    if not coords or len(coords) < 3:
        raise HTTPException(status_code=400, detail="Un polygone valide requiert au moins 3 points de coordonnées.")

    # Calcul du centroïde [lon, lat]
    lons = [pt[0] for pt in coords]
    lats = [pt[1] for pt in coords]
    c_lon = sum(lons) / len(lons)
    c_lat = sum(lats) / len(lats)

    point_req = PointDiagnosisRequest(
        latitude=c_lat,
        longitude=c_lon,
        horizon=req.horizon,
        scenario=req.scenario
    )
    res = diagnose_point(point_req, db)
    res["site_name"] = req.site_name
    res["polygon_centroid"] = {"latitude": round(c_lat, 5), "longitude": round(c_lon, 5)}
    res["vertices_count"] = len(coords)
    return res


@router.get("/raster-metadata")
def get_raster_metadata() -> Any:
    """Informations sur les couches GeoTIFF CMIP6 disponibles pour l'affichage cartographique."""
    return {
        "bounding_box": {
            "min_lon": -5.5,
            "min_lat": 9.0,
            "max_lon": 2.5,
            "max_lat": 15.5,
        },
        "resolution_deg": 0.05,
        "grid_size": {"width": 160, "height": 130},
        "available_variables": [
            {"id": "bio1", "name": "Température Moyenne Annuelle (°C)", "unit": "°C"},
            {"id": "bio12", "name": "Précipitations Annuelles Cumulées (mm)", "unit": "mm"},
            {"id": "bio4", "name": "Saisonnalité Thermique", "unit": "indice"},
            {"id": "bio15", "name": "Saisonnalité Pluviométrique", "unit": "CV%"},
            {"id": "suitability", "name": "Aptitude Climatique Globale", "unit": "Score 0-100"},
            {"id": "erosion", "name": "Indice d'Érosion Fonctionnelle (FEI)", "unit": "FEI 0-1"},
        ],
        "scenarios": ["actuel", "ssp245", "ssp585"],
        "horizons": ["actuel", "2050", "2080"],
    }
