-- ==============================================================================
-- SAHELTRAITS-DB : JEU DE DONNÉES INITIAL (SEED DATA)
-- Écosystèmes sahéliens et soudano-sahéliens du Burkina Faso
-- Espèces végétales majeures pour l'adaptation au changement climatique
-- ==============================================================================

-- 1. UTILISATEURS DU SYSTÈME (Mots de passe hachés bcrypt avec 'Doctorat2027!')
-- Hash généré par bcrypt: $2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq
INSERT INTO app_users (user_id, username, email, hashed_password, role, full_name, institution) VALUES
('a0000000-0000-0000-0000-000000000001', 'yago_rachide', 'rachide.yago@ujkz.bf', '$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq', 'Admin', 'YAGO Abdoul Rachide', 'UJKZ - École Doctorale Sciences & Technologies / ICC'),
('a0000000-0000-0000-0000-000000000002', 'dr_ouedraogo', 'a.ouedraogo@ujkz.bf', '$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq', 'Chercheur', 'Dr. Amadé OUÉDRAOGO', 'UJKZ - Laboratoire de Biologie et Écologie Végétales'),
('a0000000-0000-0000-0000-000000000003', 'enqueteur_terrain', 'terrain.sahel@ujkz.bf', '$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq', 'Enquêteur', 'Moussa SAWADOGO', 'UJKZ - Mission Écologie de Terrain Dori/Gorom'),
('a0000000-0000-0000-0000-000000000004', 'lecteur_public', 'visiteur@cirad.fr', '$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq', 'Lecteur public', 'Dr. Jean DUPONT', 'CIRAD - Écologie Fonctionnelle');

-- 2. DIMENSION TAXONOMIE (6 essences clés de la zone sahélienne & soudano-sahélienne)
INSERT INTO dim_taxonomy (taxon_id, scientific_name, accepted_name_gbif, gbif_usage_key, gbif_confidence_score, family, genus, vernacular_moore, vernacular_dioula, vernacular_fulfulde, functional_group, iucn_status) VALUES
('b0000000-0000-0000-0000-000000000001', 'Balanites aegyptiaca (L.) Delile', 'Balanites aegyptiaca (L.) Delile', 3152865, 98.0, 'Zygophyllaceae', 'Balanites', 'Kieglga', 'Ségéné', 'Murtooki', 'Épineux xérophyte persistant', 'LC'),
('b0000000-0000-0000-0000-000000000002', 'Adansonia digitata L.', 'Adansonia digitata L.', 3152220, 99.0, 'Malvaceae', 'Adansonia', 'Toèga', 'Sira', 'Boki', 'Méga-arbre réserve hydrique', 'LC'),
('b0000000-0000-0000-0000-000000000003', 'Faidherbia albida (Delile) A.Chev.', 'Faidherbia albida (Delile) A.Chev.', 2977465, 98.0, 'Fabaceae', 'Faidherbia', 'Zaanga', 'Balanzan', 'Caski', 'Fixateur azote phénologie inversée', 'LC'),
('b0000000-0000-0000-0000-000000000004', 'Vachellia tortilis (Forssk.) Galasso & Banfi', 'Vachellia tortilis (Forssk.) Galasso & Banfi', 2978712, 97.0, 'Fabaceae', 'Vachellia', 'Gom-peelga', 'Danba', 'Cilluki', 'Épineux sahélien hyper-xérique', 'LC'),
('b0000000-0000-0000-0000-000000000005', 'Combretum glutinosum Perr. ex DC.', 'Combretum glutinosum Perr. ex DC.', 3188540, 98.0, 'Combretaceae', 'Combretum', 'Rambolga', 'Doki', 'Dooki', 'Arbuste pyrophyle résilient', 'LC'),
('b0000000-0000-0000-0000-000000000006', 'Ziziphus mauritiana Lam.', 'Ziziphus mauritiana Lam.', 3039423, 99.0, 'Rhamnaceae', 'Ziziphus', 'Moug-noaga', 'Tomboron', 'Jaabi', 'Arbuste fruitier résistant', 'LC');

-- 3. DIMENSION PLACETTES (3 gradients bioclimatiques : Dori, Kaya, Pô)
INSERT INTO dim_sites_plots (plot_id, site_name, climatic_zone, geom, elevation_m, slope_deg, protection_status, fire_frequency_20yr) VALUES
('BF-DOR-01', 'Dori - Mare de Yakouta', 'Sahélienne', ST_GeogFromText('SRID=4326;POLYGON((-0.095 14.030, -0.090 14.030, -0.090 14.035, -0.095 14.035, -0.095 14.030))'), 285.0, 1.2, 'Zone Pastorale Communale', 1.5),
('BF-KAY-01', 'Kaya - Forêt Classée de Dem', 'Soudano-Sahélienne', ST_GeogFromText('SRID=4326;POLYGON((-1.130 13.080, -1.125 13.080, -1.125 13.085, -1.130 13.085, -1.130 13.080))'), 312.0, 2.5, 'Forêt Classée', 4.8),
('BF-PO-01', 'Pô - Parc National Kaboré Tambi', 'Soudanienne', ST_GeogFromText('SRID=4326;POLYGON((-1.160 11.240, -1.155 11.240, -1.155 11.245, -1.160 11.245, -1.160 11.240))'), 290.0, 3.1, 'Parc National', 12.4);

-- 4. TABLE DE FAITS : INDIVIDUS INVENTORIÉS
INSERT INTO fact_individuals (ind_id, plot_id, taxon_id, qr_code_tag, dbh_cm, total_height_m, crown_diameter_m, canopy_position, health_status_score, geom_tree) VALUES
('c0000000-0000-0000-0000-000000000001', 'BF-DOR-01', 'b0000000-0000-0000-0000-000000000001', 'TAG-BF-DOR-BAL-001', 32.5, 7.8, 5.4, 'Dominant', 5, ST_GeogFromText('SRID=4326;POINT(-0.0925 14.0325)')),
('c0000000-0000-0000-0000-000000000002', 'BF-DOR-01', 'b0000000-0000-0000-0000-000000000004', 'TAG-BF-DOR-VAC-002', 24.1, 5.2, 4.2, 'Codominant', 4, ST_GeogFromText('SRID=4326;POINT(-0.0928 14.0328)')),
('c0000000-0000-0000-0000-000000000003', 'BF-KAY-01', 'b0000000-0000-0000-0000-000000000002', 'TAG-BF-KAY-ADA-001', 145.0, 14.5, 12.8, 'Émergent', 4, ST_GeogFromText('SRID=4326;POINT(-1.1275 13.0825)')),
('c0000000-0000-0000-0000-000000000004', 'BF-KAY-01', 'b0000000-0000-0000-0000-000000000003', 'TAG-BF-KAY-FAI-002', 48.0, 11.2, 8.5, 'Dominant', 5, ST_GeogFromText('SRID=4326;POINT(-1.1280 13.0830)')),
('c0000000-0000-0000-0000-000000000005', 'BF-PO-01', 'b0000000-0000-0000-0000-000000000005', 'TAG-BF-PO-COM-001', 18.2, 6.4, 3.8, 'Sous-étage', 4, ST_GeogFromText('SRID=4326;POINT(-1.1575 11.2425)'));

-- 5. TABLE DE FAITS : MESURES MULTI-ORGANES DE TRAITS (ETS v1.0)
INSERT INTO fact_traits_measurements (meas_id, ind_id, trait_name_ets, trait_value, unit, organ_sampled, measurement_protocol, instrument_id, measurement_date, operator_id, qc_flag, qc_notes) VALUES
('d0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'SLA', 9.85, 'mm2/mg', 'Feuille', 'Cornelissen et al. (2003) - Leaf scanner 600dpi', 'SCAN-EPSR-01', '2026-10-15', 'a0000000-0000-0000-0000-000000000001', 'VALID', 'Calibration normale'),
('d0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000001', 'LDMC', 425.4, 'mg/g', 'Feuille', 'Poids frais réhydraté 24h / Poids sec 72h à 60°C', 'BAL-SART-04', '2026-10-15', 'a0000000-0000-0000-0000-000000000001', 'VALID', 'Conforme standard'),
('d0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000001', 'Wood_density', 0.72, 'g/cm3', 'Rameau', 'Méthode déplacement eau (Archimède)', 'BAL-OHAUS-02', '2026-10-16', 'a0000000-0000-0000-0000-000000000002', 'VALID', 'Bois dense xérophyte'),
('d0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000003', 'SLA', 14.20, 'mm2/mg', 'Feuille', 'Cornelissen et al. (2003)', 'SCAN-EPSR-01', '2026-10-18', 'a0000000-0000-0000-0000-000000000001', 'VALID', 'Feuille baobab'),
('d0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000004', 'SLA', 16.50, 'mm2/mg', 'Feuille', 'Cornelissen et al. (2003)', 'SCAN-EPSR-01', '2026-10-19', 'a0000000-0000-0000-0000-000000000003', 'VALID', 'Folioles Faidherbia');

-- 6. TABLE DE FAITS : ESSAIS GERMINATIFS
INSERT INTO fact_seed_germination (germ_id, ind_id, seed_batch_qr, temp_regime_c, osmotic_potential_mpa, pretreatment_type, total_seeds, germinated_count, t50_days) VALUES
('e0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'LOT-BAL-DOR-2026-A', '30/20', 0.0, 'Scarification mécanique', 100, 88, 4.2),
('e0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000001', 'LOT-BAL-DOR-2026-B', '35/25', -0.4, 'Scarification mécanique', 100, 64, 7.8),
('e0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000004', 'LOT-FAI-KAY-2026-A', '30/20', 0.0, 'H2SO4 98% 15min', 100, 92, 3.5),
('e0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000004', 'LOT-FAI-KAY-2026-C', '40/30', -0.8, 'H2SO4 98% 15min', 100, 41, 11.2);

-- 7. TABLE DE FAITS : ENVIRONNEMENT & SOL
INSERT INTO fact_environment_soil (env_id, plot_id, depth_cm, clay_pct, silt_pct, sand_pct, ph_h2o, organic_carbon_gkg, total_n_gkg, avail_p_mgkg, cec_cmolkg, dry_season_moisture_pct, sampling_date) VALUES
('f0000000-0000-0000-0000-000000000001', 'BF-DOR-01', '0-20', 12.5, 18.0, 69.5, 6.8, 4.2, 0.35, 6.5, 5.2, 2.1, '2026-09-20'),
('f0000000-0000-0000-0000-000000000002', 'BF-DOR-01', '20-40', 15.0, 19.5, 65.5, 7.1, 2.8, 0.22, 4.1, 6.0, 1.8, '2026-09-20'),
('f0000000-0000-0000-0000-000000000003', 'BF-KAY-01', '0-20', 18.2, 24.5, 57.3, 6.2, 8.5, 0.65, 9.2, 8.4, 4.5, '2026-09-22'),
('f0000000-0000-0000-0000-000000000004', 'BF-PO-01', '0-20', 25.4, 28.1, 46.5, 5.8, 14.2, 1.15, 14.8, 12.6, 8.9, '2026-09-25');

-- 8. TABLE DE FAITS : ENQUÊTES ETHNO-ÉCOLOGIQUES
INSERT INTO fact_surveys_ethno (survey_id, taxon_id, respondent_type, geom_village, village_name, climatic_zone, perceived_decline_score, phenology_shift_observed, phenology_shift_details, drought_resilience_rank, traditional_uses, interviewer_id) VALUES
('10000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 'Expert', ST_GeogFromText('SRID=4326;POINT(-0.0880 14.0250)'), 'Yakouta (Dori)', 'Sahélienne', 0, TRUE, 'Floraison décalée de 3 semaines après premières pluies', 1, 'Fruits consommés (soumbala de Balanites), huile cosmétique et médicinale, bois d oeuvre imputrescible', 'a0000000-0000-0000-0000-000000000003'),
('10000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000003', 'Local', ST_GeogFromText('SRID=4326;POINT(-1.1210 13.0780)'), 'Dem (Kaya)', 'Soudano-Sahélienne', -1, TRUE, 'Perte précoce du feuillage en saison des pluies écourtée', 2, 'Agroforesterie de parc, fertilisation azotée des champs de mil/sorgho, fourrage aérien gousses', 'a0000000-0000-0000-0000-000000000003');
