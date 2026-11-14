-- ==============================================================================
-- PROJET : THÈSE DE DOCTORAT (2027–2030) — UJKZ-ICC (BURKINA FASO)
-- COMPOSANT : SAHELTRAITS-DB — Entrepôt de données relationnel & spatial
-- MAÎTRE D'OUVRAGE : YAGO Abdoul Rachide (Doctorant)
-- CONFORMITÉ : Principes FAIR, ETS v1.0 (Ecological Trait-data Standard), Darwin Core
-- POSTGRESQL 16 + EXTENSION SPATIALE POSTGIS (SRID 4326 - WGS 84)
-- ==============================================================================

-- Activation des extensions requises
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Nettoyage conditionnel (ordre inverse des dépendances pour réinitialisation)
DROP TABLE IF EXISTS fact_surveys_ethno CASCADE;
DROP TABLE IF EXISTS fact_environment_soil CASCADE;
DROP TABLE IF EXISTS fact_seed_germination CASCADE;
DROP TABLE IF EXISTS fact_traits_measurements CASCADE;
DROP TABLE IF EXISTS fact_individuals CASCADE;
DROP TABLE IF EXISTS dim_sites_plots CASCADE;
DROP TABLE IF EXISTS dim_taxonomy CASCADE;
DROP TABLE IF EXISTS app_users CASCADE;

-- ------------------------------------------------------------------------------
-- 0. TABLE DE GESTION DES UTILISATEURS & AUTHENTIFICATION (RBAC)
-- ------------------------------------------------------------------------------
CREATE TABLE app_users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN ('Admin', 'Chercheur', 'Enquêteur', 'Lecteur public')),
    full_name VARCHAR(120) NOT NULL,
    institution VARCHAR(150) DEFAULT 'UJKZ-ICC (Ouagadougou)',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON app_users(username);
CREATE INDEX idx_users_email ON app_users(email);
CREATE INDEX idx_users_role ON app_users(role);

COMMENT ON TABLE app_users IS 'Comptes utilisateurs et rôles d accès RBAC pour les chercheurs, enquêteurs de terrain et administrateurs';

-- ------------------------------------------------------------------------------
-- 1. DIMENSION TAXONOMIE (dim_taxonomy)
-- Standardisation botanique et noms vernaculaires du Sahel burkinabè
-- ------------------------------------------------------------------------------
CREATE TABLE dim_taxonomy (
    taxon_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scientific_name VARCHAR(255) NOT NULL UNIQUE,
    accepted_name_gbif VARCHAR(255),
    gbif_usage_key INTEGER,
    gbif_confidence_score DOUBLE PRECISION,
    family VARCHAR(100) NOT NULL,
    genus VARCHAR(100) NOT NULL,
    vernacular_moore VARCHAR(150),
    vernacular_dioula VARCHAR(150),
    vernacular_fulfulde VARCHAR(150),
    functional_group VARCHAR(100), -- Ex: Fixateur azote, Épineux sahélien, Arbre fourrager
    iucn_status VARCHAR(20) DEFAULT 'LC' CHECK (iucn_status IN ('EX', 'EW', 'CR', 'EN', 'VU', 'NT', 'LC', 'DD', 'NE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_taxo_scientific_name ON dim_taxonomy(scientific_name);
CREATE INDEX idx_taxo_accepted_gbif ON dim_taxonomy(accepted_name_gbif);
CREATE INDEX idx_taxo_family_genus ON dim_taxonomy(family, genus);
CREATE INDEX idx_taxo_functional_group ON dim_taxonomy(functional_group);

COMMENT ON TABLE dim_taxonomy IS 'Dimension taxonomique standardisée avec alignement GBIF Backbone et noms vernaculaires mooré, dioula et fulfuldé';

-- ------------------------------------------------------------------------------
-- 2. DIMENSION SITES ET PLACETTES (dim_sites_plots)
-- Échelle spatiale (zones climatiques sahélienne, soudano-sahélienne, soudanienne)
-- ------------------------------------------------------------------------------
CREATE TABLE dim_sites_plots (
    plot_id VARCHAR(50) PRIMARY KEY, -- Ex: BF-NOU-01 (Site Namsiguia, Placette 01)
    site_name VARCHAR(150) NOT NULL,
    climatic_zone VARCHAR(50) NOT NULL CHECK (climatic_zone IN ('Sahélienne', 'Soudano-Sahélienne', 'Soudanienne')),
    geom GEOGRAPHY(GEOMETRY, 4326) NOT NULL, -- Point (centroïde) ou Polygone délimitant la placette (50m x 50m)
    elevation_m DOUBLE PRECISION,
    slope_deg DOUBLE PRECISION,
    protection_status VARCHAR(100), -- Ex: Forêt classée, Parc national, Terroir villageois, Réserve de biosphère
    fire_frequency_20yr DOUBLE PRECISION CHECK (fire_frequency_20yr >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index spatial GiST pour requêtes d'intersection et de voisinage rapides
CREATE INDEX idx_plots_spatial_geom ON dim_sites_plots USING GIST (geom);
CREATE INDEX idx_plots_climatic_zone ON dim_sites_plots(climatic_zone);
CREATE INDEX idx_plots_site_name ON dim_sites_plots(site_name);

COMMENT ON TABLE dim_sites_plots IS 'Dimension spatiale des placettes d échantillonnage permanentes dans le gradient bioclimatique du Burkina Faso';

-- ------------------------------------------------------------------------------
-- 3. TABLE DE FAITS : INDIVIDUS INVENTORIÉS (fact_individuals)
-- Arbres géolocalisés, tagués par QR-Code
-- ------------------------------------------------------------------------------
CREATE TABLE fact_individuals (
    ind_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id VARCHAR(50) NOT NULL REFERENCES dim_sites_plots(plot_id) ON DELETE CASCADE,
    taxon_id UUID NOT NULL REFERENCES dim_taxonomy(taxon_id) ON DELETE RESTRICT,
    qr_code_tag VARCHAR(100) NOT NULL UNIQUE,
    dbh_cm DOUBLE PRECISION CHECK (dbh_cm > 0),
    total_height_m DOUBLE PRECISION CHECK (total_height_m > 0),
    crown_diameter_m DOUBLE PRECISION CHECK (crown_diameter_m >= 0),
    canopy_position VARCHAR(50) CHECK (canopy_position IN ('Dominant', 'Codominant', 'Intermédiaire', 'Sous-étage', 'Émergent')),
    health_status_score INTEGER NOT NULL CHECK (health_status_score BETWEEN 1 AND 5), -- 1: Dépérissant / 5: Vigueur maximale
    geom_tree GEOGRAPHY(POINT, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ind_plot_id ON fact_individuals(plot_id);
CREATE INDEX idx_ind_taxon_id ON fact_individuals(taxon_id);
CREATE INDEX idx_ind_qr_code ON fact_individuals(qr_code_tag);
CREATE INDEX idx_ind_spatial_geom_tree ON fact_individuals USING GIST (geom_tree);

COMMENT ON TABLE fact_individuals IS 'Individus ligneux inventoriés avec balise QR-Code physique et géolocalisation centimétrique/métrique';

-- ------------------------------------------------------------------------------
-- 4. TABLE DE FAITS : MESURES MULTI-ORGANES DE TRAITS (fact_traits_measurements)
-- Conforme Ecological Trait-data Standard (ETS v1.0)
-- ------------------------------------------------------------------------------
CREATE TABLE fact_traits_measurements (
    meas_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ind_id UUID NOT NULL REFERENCES fact_individuals(ind_id) ON DELETE CASCADE,
    trait_name_ets VARCHAR(100) NOT NULL, -- SLA, LDMC, Leaf_N, Wood_density, Bark_thickness, Stomatal_density, Leaf_area
    trait_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50) NOT NULL, -- mm2/mg, mg/g, g/cm3, mm, n/mm2, cm2
    organ_sampled VARCHAR(50) NOT NULL CHECK (organ_sampled IN ('Feuille', 'Rameau', 'Tronc', 'Écorce', 'Racine', 'Fleur', 'Fruit', 'Graine')),
    measurement_protocol TEXT,
    instrument_id VARCHAR(100),
    measurement_date DATE NOT NULL DEFAULT CURRENT_DATE,
    operator_id UUID REFERENCES app_users(user_id) ON DELETE SET NULL,
    qc_flag VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (qc_flag IN ('PENDING', 'VALID', 'SUSPECT_OUTLIER_3SIGMA', 'FLAGGED_MANUAL', 'MANUALLY_APPROVED', 'REJECTED')),
    qc_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_traits_ind_id ON fact_traits_measurements(ind_id);
CREATE INDEX idx_traits_name_ets ON fact_traits_measurements(trait_name_ets);
CREATE INDEX idx_traits_qc_flag ON fact_traits_measurements(qc_flag);
CREATE INDEX idx_traits_date ON fact_traits_measurements(measurement_date);
CREATE INDEX idx_traits_composite ON fact_traits_measurements(trait_name_ets, qc_flag);

COMMENT ON TABLE fact_traits_measurements IS 'Mesures de traits fonctionnels multi-organes conformes ETS v1.0 avec suivi automatique QC 3-sigma';

-- ------------------------------------------------------------------------------
-- 5. TABLE DE FAITS : ESSAIS GERMINATIFS (fact_seed_germination)
-- Écophysiologie de la régénération sous stress thermique et hydrique (PEG 6000)
-- ------------------------------------------------------------------------------
CREATE TABLE fact_seed_germination (
    germ_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ind_id UUID NOT NULL REFERENCES fact_individuals(ind_id) ON DELETE CASCADE,
    seed_batch_qr VARCHAR(100) NOT NULL,
    temp_regime_c VARCHAR(50) NOT NULL, -- Ex: 25/15, 30/20, 35/25, 40/30 (thermopériode jour/nuit)
    osmotic_potential_mpa DOUBLE PRECISION NOT NULL DEFAULT 0.0 CHECK (osmotic_potential_mpa <= 0.0), -- 0.0, -0.2, -0.4, -0.8 MPa
    pretreatment_type VARCHAR(100), -- Ex: Témoin, Scarification mécanique, H2SO4 98% 15min, Eau bouillante 5min
    total_seeds INTEGER NOT NULL CHECK (total_seeds > 0),
    germinated_count INTEGER NOT NULL CHECK (germinated_count >= 0 AND germinated_count <= total_seeds),
    t50_days DOUBLE PRECISION CHECK (t50_days >= 0), -- Temps nécessaire pour atteindre 50% de la germination finale
    final_gp_pct DOUBLE PRECISION GENERATED ALWAYS AS (ROUND(((germinated_count::numeric / total_seeds::numeric) * 100.0), 2)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_germ_ind_id ON fact_seed_germination(ind_id);
CREATE INDEX idx_germ_batch_qr ON fact_seed_germination(seed_batch_qr);
CREATE INDEX idx_germ_osmotic ON fact_seed_germination(osmotic_potential_mpa);

COMMENT ON TABLE fact_seed_germination IS 'Essais germinatifs contrôlés en étuve sous contraintes combinées température x potentiel osmotique';

-- ------------------------------------------------------------------------------
-- 6. TABLE DE FAITS : ENVIRONNEMENT & SOL (fact_environment_soil)
-- Propriétés physico-chimiques du sol par tranche de profondeur
-- ------------------------------------------------------------------------------
CREATE TABLE fact_environment_soil (
    env_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plot_id VARCHAR(50) NOT NULL REFERENCES dim_sites_plots(plot_id) ON DELETE CASCADE,
    depth_cm VARCHAR(30) NOT NULL, -- Ex: 0-20, 20-40, 40-60, 60-100
    clay_pct DOUBLE PRECISION CHECK (clay_pct >= 0 AND clay_pct <= 100),
    silt_pct DOUBLE PRECISION CHECK (silt_pct >= 0 AND silt_pct <= 100),
    sand_pct DOUBLE PRECISION CHECK (sand_pct >= 0 AND sand_pct <= 100),
    ph_h2o DOUBLE PRECISION CHECK (ph_h2o >= 0 AND ph_h2o <= 14),
    organic_carbon_gkg DOUBLE PRECISION CHECK (organic_carbon_gkg >= 0),
    total_n_gkg DOUBLE PRECISION CHECK (total_n_gkg >= 0),
    avail_p_mgkg DOUBLE PRECISION CHECK (avail_p_mgkg >= 0),
    cec_cmolkg DOUBLE PRECISION CHECK (cec_cmolkg >= 0),
    dry_season_moisture_pct DOUBLE PRECISION CHECK (dry_season_moisture_pct >= 0 AND dry_season_moisture_pct <= 100),
    sampling_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_soil_plot_id ON fact_environment_soil(plot_id);
CREATE INDEX idx_soil_depth ON fact_environment_soil(depth_cm);

COMMENT ON TABLE fact_environment_soil IS 'Paramètres édaphiques et physico-chimiques stratifiés par horizon de sol';

-- ------------------------------------------------------------------------------
-- 7. TABLE DE FAITS : ENQUÊTES ETHNO-ÉCOLOGIQUES (fact_surveys_ethno)
-- Perception locale du dépérissement et résilience à la sécheresse
-- ------------------------------------------------------------------------------
CREATE TABLE fact_surveys_ethno (
    survey_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    taxon_id UUID NOT NULL REFERENCES dim_taxonomy(taxon_id) ON DELETE RESTRICT,
    respondent_type VARCHAR(50) NOT NULL CHECK (respondent_type IN ('Expert', 'Local')),
    geom_village GEOGRAPHY(POINT, 4326) NOT NULL,
    village_name VARCHAR(150),
    climatic_zone VARCHAR(50) NOT NULL CHECK (climatic_zone IN ('Sahélienne', 'Soudano-Sahélienne', 'Soudanienne')),
    perceived_decline_score INTEGER NOT NULL CHECK (perceived_decline_score BETWEEN -2 AND 2), -- -2: Très forte régression / 0: Stable / +2: Expansion
    phenology_shift_observed BOOLEAN NOT NULL DEFAULT FALSE,
    phenology_shift_details TEXT,
    drought_resilience_rank INTEGER NOT NULL CHECK (drought_resilience_rank >= 1),
    traditional_uses TEXT, -- Alimentaire, Pharmacopée, Fourrage, Énergie ligneuse
    interviewer_id UUID REFERENCES app_users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_surveys_taxon_id ON fact_surveys_ethno(taxon_id);
CREATE INDEX idx_surveys_climatic_zone ON fact_surveys_ethno(climatic_zone);
CREATE INDEX idx_surveys_respondent_type ON fact_surveys_ethno(respondent_type);
CREATE INDEX idx_surveys_spatial_village ON fact_surveys_ethno USING GIST (geom_village);

COMMENT ON TABLE fact_surveys_ethno IS 'Enquêtes ethno-écologiques sur la résilience climatique et les usages des essences sahéliennes';
