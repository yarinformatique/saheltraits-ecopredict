# SAHELTRAITS-DB & ECOPREDICT : SYNTHÈSE ANALYTIQUE MULTI-COUCHES

**Projet de Recherche :** Thèse de Doctorat en Écologie Fonctionnelle & Bio-informatique (2026–2029)  
**Auteur / Doctorant :** YAGO Abdoul Rachide (UJKZ - École Doctorale Sciences & Technologies / ICC)  
**Directeur de Thèse & Encadrement :** Université Joseph Ki-Zerbo (Ouagadougou, Burkina Faso)  
**Partenaires :** MEEA • MESRI • Agence Nationale de la Grande Muraille Verte  

---

## 1. Architecture Analytique de la Plateforme

| Couche | Composant | Rôle Opérationnel & Analytique | Technologies & Frameworks | Statut de Déploiement |
| :--- | :--- | :--- | :--- | :---: |
| **Couche 1** | **`mobile/`** (SahelField) | Collecte mobile terrain PWA offline, géolocalisation GPS, traçabilité QR-Codes, enquêtes XLSForm (450 fiches) | Next.js 14, PWA, Dexie.js (IndexedDB), HTML5 QR-Code | **Déployé & Opérationnel** |
| **Couche 2** | **`vision/`** (Morpho-Vision) | Analyse biométrique foliaire et séminale assistée par vision par ordinateur (surfaces, longueurs, rugosité, SLA) | FastAPI, OpenCV, NumPy, SciPy | **Déployé & Opérationnel** |
| **Couche 3** | **`backend/`** (SahelTraits-DB) | Entrepôt centralisé PostGIS/PostgreSQL, API REST FAIR & ETS v1.0, synchronisation différentielle | FastAPI, PostgreSQL/PostGIS, SQLAlchemy, Alembic, Docker | **Déployé & Opérationnel** |
| **Couche 4a** | **`pipeline/`** (EcoPredict Core) | Chaîne bio-statistique de pointe : IndVal, glmmTMB/lme4, DHARMa, RLQ/Fourth-Corner, Hmsc JSDM, biomod2 CMIP6 | Python 3.12, R 4.4, Hmsc, biomod2, ade4, FactoMineR | **Déployé & Reproductible** |
| **Couche 4b** | **`web/`** (EcoPredict Dashboard) | Portail SIG interactif d'aide à la décision, simulations CMIP6 2050/2080, catalogue ouvert | Next.js 14, Tailwind CSS, Leaflet, Lucide Icons | **Déployé & En Ligne** |
| **Synthèse** | **`analytics/`** | Consolidation des métriques transversales, indicateurs de performance, pipelines d'évaluation croisée | Python, Pandas, JSON, CSV | **Consolidé & Validé** |

---

## 2. Indicateurs Clés de Performance Analytique (KPIs)

* **Occurrences nettoyées (Module 1) :** 1 951 occurrences géoréférencées rigoureusement validées via `CoordinateCleaner`.
* **Convergence MCMC Hmsc (Module 4) :** $\text{PSRF} < 1.025$ (< 1.05) et $\text{ESS} > 1\,452$ (> 1 000).
* **Performance biomod2 (Module 4) :** $\text{AUC} > 0.89$ et $\text{TSS} > 0.75$ sur les 5 algorithmes d'ensemble (RF, GBM, MaxEnt, GAM, GLM).
* **Précision Vision (Morpho-Vision) :** Détection foliaire et séminale avec erreur relative $< 1.8\%$ par rapport aux mires millimétriques de calibration.
* **Résilience PWA Mobile (SahelField) :** Synchronisation transactionnelle garantie même après coupure réseau 4G / redémarrage hors-ligne.
