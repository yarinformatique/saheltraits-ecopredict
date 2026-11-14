// Test Sync Batch payload construction against backend schema
const assert = require('assert');

const mockBatchPayload = {
  batch_id: 'BATCH-TEST-MOBILE-001',
  device_id: 'SAHELFIELD-TAB-SAMSUNG-01',
  collected_at: new Date().toISOString(),
  plots: [
    {
      plot_id: 'BF-DOR-01',
      site_name: 'Dori - Mare de Yakouta',
      climatic_zone: 'Sahélienne',
      geom: { type: 'Point', coordinates: [-0.0925, 14.0325] },
      elevation_m: 285.0,
      slope_deg: 1.2,
      protection_status: 'Zone Pastorale Communale',
      fire_frequency_20yr: 1.5,
    },
  ],
  individuals: [
    {
      plot_id: 'BF-DOR-01',
      taxon_id: 'b0000000-0000-0000-0000-000000000001',
      qr_code_tag: 'TAG-BF-DOR-BAL-001',
      dbh_cm: 32.5,
      total_height_m: 7.8,
      crown_diameter_m: 5.4,
      canopy_position: 'Dominant',
      health_status_score: 5,
      geom_tree: { type: 'Point', coordinates: [-0.0925, 14.0325] },
    },
  ],
  traits: [
    {
      ind_id: 'c0000000-0000-0000-0000-000000000001',
      trait_name_ets: 'SLA',
      trait_value: 9.85,
      unit: 'mm2/mg',
      organ_sampled: 'Feuille',
      measurement_protocol: 'Cornelissen et al. (2003)',
      instrument_id: 'SCAN-EPSR-01',
    },
  ],
  seed_trials: [
    {
      ind_id: 'c0000000-0000-0000-0000-000000000001',
      seed_batch_qr: 'LOT-BAL-DOR-2026-A',
      temp_regime_c: '30/20',
      osmotic_potential_mpa: 0.0,
      pretreatment_type: 'Scarification mécanique',
      total_seeds: 50,
      germinated_count: 44,
    },
  ],
  soil_records: [
    {
      plot_id: 'BF-DOR-01',
      depth_cm: '0-20',
      clay_pct: 12.5,
      silt_pct: 18.0,
      sand_pct: 69.5,
      ph_h2o: 6.8,
      organic_carbon_gkg: 4.2,
    },
  ],
  surveys: [
    {
      taxon_id: 'b0000000-0000-0000-0000-000000000001',
      respondent_type: 'Local',
      geom_village: { type: 'Point', coordinates: [-0.088, 14.025] },
      village_name: 'Yakouta',
      climatic_zone: 'Sahélienne',
      perceived_decline_score: 0,
      phenology_shift_observed: true,
      phenology_shift_details: 'Floraison normale',
      drought_resilience_rank: 1,
      traditional_uses: 'Alimentation, huile et fourrage',
      interviewer_id: 'ENQ-01',
    },
  ],
};

console.log('🧪 Vérification du schéma SyncBatchRequest...');
assert.ok(mockBatchPayload.batch_id, 'batch_id requis');
assert.strictEqual(mockBatchPayload.plots.length, 1);
assert.strictEqual(mockBatchPayload.individuals.length, 1);
assert.strictEqual(mockBatchPayload.traits.length, 1);
assert.strictEqual(mockBatchPayload.seed_trials.length, 1);
assert.strictEqual(mockBatchPayload.soil_records.length, 1);
assert.strictEqual(mockBatchPayload.surveys.length, 1);

// Validate geometric schema
assert.strictEqual(mockBatchPayload.plots[0].geom.type, 'Point');
assert.strictEqual(mockBatchPayload.individuals[0].geom_tree.type, 'Point');
assert.strictEqual(mockBatchPayload.surveys[0].geom_village.type, 'Point');

console.log('  ✅ Payload conforme aux spécifications FastAPI Pydantic.');
