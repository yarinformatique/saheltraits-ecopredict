// SahelField - Dexie IndexedDB Store pour persistance 100% hors-ligne (Offline-First)

import Dexie, { Table } from 'dexie';
import {
  SitePlot,
  RegenerationSubplot,
  Individual,
  TraitMeasurement,
  SeedTrial,
  SoilRecord,
  EthnoSurvey,
} from '@/types';

export interface SyncLogEntry {
  id?: number;
  batch_id: string;
  timestamp: string;
  status: 'SUCCESS' | 'PARTIAL' | 'ERROR';
  plots_synced: number;
  individuals_synced: number;
  traits_synced: number;
  surveys_synced: number;
  flagged_outliers_count: number;
  message: string;
  errors?: string[];
}

export class SahelFieldDatabase extends Dexie {
  plots!: Table<SitePlot, number>;
  regeneration!: Table<RegenerationSubplot, number>;
  individuals!: Table<Individual, number>;
  traits!: Table<TraitMeasurement, number>;
  seed_trials!: Table<SeedTrial, number>;
  soil_records!: Table<SoilRecord, number>;
  surveys!: Table<EthnoSurvey, number>;
  sync_logs!: Table<SyncLogEntry, number>;

  constructor() {
    super('SahelFieldDB');
    this.version(1).stores({
      plots: '++id, &plot_id, site_name, climatic_zone, sync_status, created_at',
      regeneration: '++id, sub_id, plot_id, subplot_code, taxon_id, sync_status',
      individuals: '++id, &ind_id, plot_id, taxon_id, &qr_code_tag, sync_status, created_at',
      traits: '++id, &meas_id, ind_id, qr_code_tag, trait_name_ets, qc_flag, sync_status, created_at',
      seed_trials: '++id, &germ_id, ind_id, seed_batch_qr, sync_status, created_at',
      soil_records: '++id, &env_id, plot_id, depth_cm, sync_status, created_at',
      surveys: '++id, &survey_id, taxon_id, respondent_type, village_name, climatic_zone, sync_status, created_at',
      sync_logs: '++id, batch_id, timestamp, status',
    });
  }

  // Prepopulate seed data if database is empty so field agents can start immediately
  async seedInitialDemoData() {
    const plotCount = await this.plots.count();
    if (plotCount === 0) {
      await this.plots.bulkAdd([
        {
          plot_id: 'BF-DOR-01',
          site_name: 'Dori - Mare de Yakouta',
          climatic_zone: 'Sahélienne',
          geom: {
            type: 'Point',
            coordinates: [-0.0925, 14.0325],
          },
          latitude: 14.0325,
          longitude: -0.0925,
          elevation_m: 285.0,
          slope_deg: 1.2,
          protection_status: 'Zone Pastorale Communale',
          fire_frequency_20yr: 1.5,
          notes: 'Placette sahélienne de référence, sol sableux limoneux.',
          created_at: new Date().toISOString(),
          sync_status: 'SYNCED',
        },
        {
          plot_id: 'BF-KAY-01',
          site_name: 'Kaya - Forêt Classée de Dem',
          climatic_zone: 'Soudano-Sahélienne',
          geom: {
            type: 'Point',
            coordinates: [-1.1275, 13.0825],
          },
          latitude: 13.0825,
          longitude: -1.1275,
          elevation_m: 312.0,
          slope_deg: 2.5,
          protection_status: 'Forêt Classée',
          fire_frequency_20yr: 4.8,
          notes: 'Parc agroforestier à Faidherbia et Combretaceae.',
          created_at: new Date().toISOString(),
          sync_status: 'SYNCED',
        },
      ]);

      await this.individuals.bulkAdd([
        {
          ind_id: 'c0000000-0000-0000-0000-000000000001',
          plot_id: 'BF-DOR-01',
          taxon_id: 'b0000000-0000-0000-0000-000000000001',
          scientific_name: 'Balanites aegyptiaca (L.) Delile',
          vernacular_name: 'Kieglga / Murtooki',
          qr_code_tag: 'TAG-BF-DOR-BAL-001',
          dbh_cm: 32.5,
          total_height_m: 7.8,
          crown_diameter_m: 5.4,
          canopy_position: 'Dominant',
          health_status_score: 5,
          geom_tree: { type: 'Point', coordinates: [-0.0925, 14.0325] },
          latitude: 14.0325,
          longitude: -0.0925,
          gps_accuracy_m: 2.8,
          created_at: new Date().toISOString(),
          sync_status: 'SYNCED',
        },
        {
          ind_id: 'c0000000-0000-0000-0000-000000000002',
          plot_id: 'BF-DOR-01',
          taxon_id: 'b0000000-0000-0000-0000-000000000004',
          scientific_name: 'Vachellia tortilis (Forssk.) Galasso & Banfi',
          vernacular_name: 'Gom-peelga / Cilluki',
          qr_code_tag: 'TAG-BF-DOR-VAC-002',
          dbh_cm: 24.1,
          total_height_m: 5.2,
          crown_diameter_m: 4.2,
          canopy_position: 'Codominant',
          health_status_score: 4,
          geom_tree: { type: 'Point', coordinates: [-0.0928, 14.0328] },
          latitude: 14.0328,
          longitude: -0.0928,
          gps_accuracy_m: 3.1,
          created_at: new Date().toISOString(),
          sync_status: 'SYNCED',
        },
      ]);
    }
  }
}

export const db = new SahelFieldDatabase();

// Auto-seed demo baseline in browser
if (typeof window !== 'undefined') {
  db.seedInitialDemoData().catch((err) => console.warn('IndexedDB initial seed error:', err));
}
