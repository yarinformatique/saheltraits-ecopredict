# SAHELTRAITS-DB & ECOPREDICT 2050-2080

[![Doctorate Thesis](https://img.shields.io/badge/Doctorat-UJKZ%20(2026--2029)-1B5E20.svg)](https://ujkz.bf)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4%20%2B%20PostgreSQL%2016-336791.svg)](https://postgis.net/)
[![FAIR ETS v1.0](https://img.shields.io/badge/FAIR-ETS%20v1.0%20Standard-brightgreen.svg)](https://terminologies.gfbio.org/)
[![CMIP6 Ready](https://img.shields.io/badge/CMIP6-SSP2--4.5%20%26%20SSP5--8.5-blue.svg)](https://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6)

---

## 1. Présentation de la Plateforme Doctorale

Plateforme intégrée d'écologie fonctionnelle et bio-informatique pour la modélisation de la résilience et de la vulnérabilité des essences ligneuses emblématiques du Sahel burkinabè sous projections climatiques CMIP6 (horizons 2050 et 2080).

* **Auteur / Doctorant :** **YAGO Abdoul Rachide**  
* **Institution de rattachement :** Université Joseph Ki-Zerbo (Ouagadougou, Burkina Faso)  
* **École Doctorale :** EDST / ICC (Informatique et Changement Climatique)  
* **Partenaires Institutionnels :** Ministère de l'Environnement, de l'Eau et de l'Assainissement (MEEA) • Ministère de l'Enseignement Supérieur, de la Recherche et de l'Innovation (MESRI) • Agence Nationale de la Grande Muraille Verte (ANGMV)

---

## 2. Structure Monorepo des Composants

| Dossier | Composant | Description | Technologies Clés |
| :--- | :--- | :--- | :--- |
| **[`web/`](./web)** | **Portail Décisionnel (Couche 4b)** | Tableau de bord interactif SIG, simulation de reboisement CMIP6, catalogue ouvert des 28 essences ligneuses. | Next.js 14, React, Leaflet, Tailwind CSS |
| **[`mobile/`](./mobile)** | **SahelField PWA (Couche 1)** | Application mobile hors-ligne de terrain : placettes dendrométriques, traçabilité QR-Codes (organes/lots), enquêtes socio-écologiques XLSForm (450 fiches). | Next.js 14 PWA, Dexie IndexedDB, HTML5 QR-Code |
| **[`backend/`](./backend)** | **API SahelTraits-DB (Couche 3)** | Entrepôt de données centralisé PostGIS/PostgreSQL, API REST FAIR & ETS v1.0, synchronisation différentielle batch. | FastAPI, PostgreSQL/PostGIS, SQLAlchemy, Alembic, Docker |
| **[`pipeline/`](./pipeline)** | **Moteur Statistique (Couche 4a)** | Chaîne analytique reproductible : IndVal, glmmTMB/lme4, DHARMa, RLQ/Fourth-Corner (49 999 perm), Hmsc JSDM, biomod2 (AUC>0.89). | Python 3.12, R 4.4, Hmsc, biomod2, ade4, FactoMineR |
| **[`vision/`](./vision)** | **Morpho-Vision (Couche 2)** | Biométriseur automatique foliaire et séminale assisté par vision par ordinateur (surfaces foliaires, SLA, dimensions graines). | FastAPI, OpenCV, NumPy, SciPy |
| **[`analytics/`](./analytics)** | **Synthèse Analytique** | Synthèse des métriques d'évaluation, KPIs de convergence et tables d'exportation pour la thèse. | Python, Pandas, JSON |

---

## 3. Déploiement Cloud & Accès Immédiat

* **Dépôt GitHub Officiel :** [https://github.com/yarinformatique/saheltraits-ecopredict](https://github.com/yarinformatique/saheltraits-ecopredict)
* **Portail Web Décisionnel (EcoPredict Dashboard) :** Déployable en 1-clic sur Vercel.
* **Application Mobile PWA (SahelField) :** Accessible directement depuis navigateur et installable sur smartphone (*Ajouter à l'écran d'accueil*).
* **Serveur Backend REST & PostGIS :** Prêt pour Render / Supabase / VPS via Dockerfile et docker-compose.
