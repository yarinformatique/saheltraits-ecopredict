// SahelField - Types de données pour collecte terrain et synchronisation SahelTraits-DB

export type ClimaticZone = 'Sahélienne' | 'Soudano-Sahélienne' | 'Soudanienne';
export type SyncStatus = 'PENDING' | 'SYNCED' | 'ERROR';
export type CanopyPosition = 'Dominant' | 'Codominant' | 'Intermédiaire' | 'Sous-étage' | 'Émergent';
export type RespondentType = 'Expert' | 'Local';
export type OrganSampled = 'Feuille' | 'Rameau' | 'Tronc' | 'Écorce' | 'Racine' | 'Fleur' | 'Fruit' | 'Graine';

export interface GeoPoint {
  type: 'Point';
  coordinates: [number, number]; // [lng, lat]
}

export interface GeoPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export type GeoJSONGeometry = GeoPoint | GeoPolygon;

// 1. Placette (50m x 20m)
export interface SitePlot {
  id?: number;
  plot_id: string; // Ex: BF-DOR-01
  site_name: string;
  climatic_zone: ClimaticZone;
  geom: GeoJSONGeometry;
  latitude: number;
  longitude: number;
  elevation_m?: number;
  slope_deg?: number;
  protection_status?: string;
  fire_frequency_20yr?: number;
  notes?: string;
  created_at: string;
  sync_status: SyncStatus;
}

// 2. Sous-placette de régénération (5m x 5m)
export interface RegenerationSubplot {
  id?: number;
  sub_id: string;
  plot_id: string;
  subplot_code: 'A' | 'B' | 'C' | 'D'; // 4 sous-placettes par placette 50x20m
  dimension_m: string; // '5x5'
  taxon_id: string;
  scientific_name: string;
  height_class: '<50cm' | '50-150cm' | '>150cm';
  count_individuals: number;
  health_notes?: string;
  created_at: string;
  sync_status: SyncStatus;
}

// 3. Arbre / Individu dendrométrique (DHP >= 5 cm)
export interface Individual {
  id?: number;
  ind_id: string; // UUID
  plot_id: string;
  taxon_id: string;
  scientific_name?: string;
  vernacular_name?: string;
  qr_code_tag: string; // Ex: TAG-BF-DOR-BAL-001
  dbh_cm: number; // DHP >= 5 cm
  total_height_m: number;
  crown_diameter_m: number;
  canopy_position: CanopyPosition;
  health_status_score: number; // 1-5 (1=agonisant/mort, 5=excellent)
  geom_tree: GeoPoint;
  latitude: number;
  longitude: number;
  gps_accuracy_m?: number;
  photo_base64?: string;
  notes?: string;
  created_at: string;
  sync_status: SyncStatus;
}

// 4. Mesures de traits fonctionnels multi-organes (ETS v1.0)
export interface TraitMeasurement {
  id?: number;
  meas_id: string;
  ind_id: string;
  qr_code_tag?: string;
  trait_name_ets: string; // 'SLA', 'LDMC', 'Wood_density', 'Leaf_area', 'Leaf_fresh_mass', 'Leaf_dry_mass'
  trait_value: number;
  unit: string; // 'mm2/mg', 'mg/g', 'g/cm3', 'cm2', 'mg'
  organ_sampled: OrganSampled;
  measurement_protocol?: string;
  instrument_id?: string;
  fresh_mass_mg?: number;
  dry_mass_mg?: number;
  leaf_area_mm2?: number;
  measurement_date: string;
  operator_id?: string;
  qc_flag?: 'VALID' | 'SUSPECT_OUTLIER_3SIGMA' | 'FLAGGED_MANUAL';
  qc_notes?: string;
  created_at: string;
  sync_status: SyncStatus;
}

// 5. Essais de germination (semences associées au QR-code)
export interface SeedTrial {
  id?: number;
  germ_id: string;
  ind_id: string;
  seed_batch_qr: string; // Ex: LOT-BAL-DOR-2026-A
  temp_regime_c: string; // '30/20'
  osmotic_potential_mpa: number; // 0.0, -0.4, -0.8
  pretreatment_type: string; // 'Scarification mécanique', 'H2SO4', etc.
  total_seeds: number;
  germinated_count: number;
  t50_days?: number;
  final_gp_pct?: number;
  created_at: string;
  sync_status: SyncStatus;
}

// 6. Paramètres de sol & environnement
export interface SoilRecord {
  id?: number;
  env_id: string;
  plot_id: string;
  depth_cm: string; // '0-20', '20-40'
  clay_pct: number;
  silt_pct: number;
  sand_pct: number;
  ph_h2o?: number;
  organic_carbon_gkg?: number;
  total_n_gkg?: number;
  avail_p_mgkg?: number;
  cec_cmolkg?: number;
  dry_season_moisture_pct?: number;
  sampling_date: string;
  created_at: string;
  sync_status: SyncStatus;
}

// 7. Enquêtes ethno-écologiques (Modules M1 à M5)
export interface EthnoSurvey {
  id?: number;
  survey_id: string;
  taxon_id: string;
  scientific_name?: string;
  vernacular_name?: string;
  respondent_type: RespondentType;
  respondent_profile?: string; // Agriculteur, Éleveur, etc.
  respondent_age?: string;
  respondent_seniority_years?: number;
  village_name: string;
  geom_village: GeoPoint;
  latitude: number;
  longitude: number;
  climatic_zone: ClimaticZone;
  perceived_decline_score: number; // -2 to +2
  phenology_shift_observed: boolean;
  phenology_shift_details?: string;
  phenology_flowering_shift?: number; // -2 to +2
  phenology_fruiting_shift?: number; // -2 to +2
  drought_resilience_rank: number; // 1 = le plus résilient
  traditional_uses?: string;
  lopping_intensity?: number; // 0-4
  fire_frequency?: string;
  rna_practiced?: boolean;
  rna_techniques?: string;
  smith_saliency_rank?: number; // Rang 1..10
  interviewer_id?: string;
  created_at: string;
  sync_status: SyncStatus;
}

// 8. Espèces de référence du Sahel & Soudano-Sahel
export interface TaxonRef {
  taxon_id: string;
  scientific_name: string;
  family: string;
  genus: string;
  vernacular_moore: string;
  vernacular_dioula: string;
  vernacular_fulfulde: string;
  functional_group: string;
  iucn_status: string;
  typical_sla_mean: number;
  typical_sla_sd: number;
  typical_wood_density_mean: number;
}

// 9. Synchronisation Batch Payload
export interface SyncBatchRequestPayload {
  batch_id: string;
  device_id: string;
  collected_at: string;
  plots: Array<{
    plot_id: string;
    site_name: string;
    climatic_zone: ClimaticZone;
    geom: GeoJSONGeometry;
    elevation_m?: number;
    slope_deg?: number;
    protection_status?: string;
    fire_frequency_20yr?: number;
  }>;
  individuals: Array<{
    plot_id: string;
    taxon_id: string;
    qr_code_tag: string;
    dbh_cm: number;
    total_height_m: number;
    crown_diameter_m: number;
    canopy_position: CanopyPosition;
    health_status_score: number;
    geom_tree: GeoPoint;
  }>;
  traits: Array<{
    ind_id: string;
    trait_name_ets: string;
    trait_value: number;
    unit: string;
    organ_sampled: OrganSampled;
    measurement_protocol?: string;
    instrument_id?: string;
    measurement_date?: string;
    operator_id?: string;
  }>;
  seed_trials: Array<{
    ind_id: string;
    seed_batch_qr: string;
    temp_regime_c: string;
    osmotic_potential_mpa: number;
    pretreatment_type: string;
    total_seeds: number;
    germinated_count: number;
    t50_days?: number;
  }>;
  soil_records: Array<{
    plot_id: string;
    depth_cm: string;
    clay_pct: number;
    silt_pct: number;
    sand_pct: number;
    ph_h2o?: number;
    organic_carbon_gkg?: number;
    total_n_gkg?: number;
    avail_p_mgkg?: number;
    cec_cmolkg?: number;
    dry_season_moisture_pct?: number;
    sampling_date?: string;
  }>;
  surveys: Array<{
    taxon_id: string;
    respondent_type: RespondentType;
    geom_village: GeoPoint;
    village_name?: string;
    climatic_zone: ClimaticZone;
    perceived_decline_score: number;
    phenology_shift_observed: boolean;
    phenology_shift_details?: string;
    drought_resilience_rank: number;
    traditional_uses?: string;
    interviewer_id?: string;
  }>;
}

export interface SyncBatchResponsePayload {
  batch_id: string;
  status: 'SUCCESS' | 'PARTIAL' | 'ERROR';
  message: string;
  synced_at: string;
  plots_synced: number;
  individuals_synced: number;
  traits_synced: number;
  seed_trials_synced: number;
  soil_records_synced: number;
  surveys_synced: number;
  flagged_outliers_count: number;
  errors: string[];
}
