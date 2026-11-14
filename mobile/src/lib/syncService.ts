// SahelField - Service de synchronisation intelligente hors-ligne avec SahelTraits-DB

import { db, SyncLogEntry } from './db';
import {
  SyncBatchRequestPayload,
  SyncBatchResponsePayload,
} from '@/types';
import { speechService } from './speechFeedback';

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

export class SyncService {
  private apiBaseUrl: string;
  private token: string | null = null;
  private deviceId: string;

  constructor() {
    this.apiBaseUrl = DEFAULT_API_BASE_URL;
    this.deviceId = 'SAHELFIELD-TAB-DEFAULT';

    if (typeof window !== 'undefined') {
      const savedUrl = localStorage.getItem('sahelfield_api_url');
      if (savedUrl) this.apiBaseUrl = savedUrl;

      const savedToken = localStorage.getItem('sahelfield_jwt_token');
      if (savedToken) this.token = savedToken;

      let devId = localStorage.getItem('sahelfield_device_id');
      if (!devId) {
        devId = `DEVICE-BF-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
        localStorage.setItem('sahelfield_device_id', devId);
      }
      this.deviceId = devId;
    }
  }

  public setApiBaseUrl(url: string) {
    this.apiBaseUrl = url.replace(/\/+$/, '');
    if (typeof window !== 'undefined') {
      localStorage.setItem('sahelfield_api_url', this.apiBaseUrl);
    }
  }

  public getApiBaseUrl(): string {
    return this.apiBaseUrl;
  }

  public setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('sahelfield_jwt_token', token);
    }
  }

  public getToken(): string | null {
    return this.token;
  }

  public getDeviceId(): string {
    return this.deviceId;
  }

  // Authenticate against /api/v1/auth/login
  public async login(username: string, password: string): Promise<{ success: boolean; message: string; role?: string }> {
    try {
      const res = await fetch(`${this.apiBaseUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        return {
          success: false,
          message: errorData.detail || `Échec de connexion (${res.status})`,
        };
      }

      const data = await res.json();
      this.setToken(data.access_token);
      return {
        success: true,
        message: 'Authentification réussie.',
        role: data.role,
      };
    } catch (e: any) {
      return {
        success: false,
        message: `Erreur réseau : ${e.message || 'Serveur backend inaccessible'}`,
      };
    }
  }

  // Count pending un-synced items
  public async countPendingItems(): Promise<{
    plots: number;
    individuals: number;
    traits: number;
    seedTrials: number;
    soils: number;
    surveys: number;
    total: number;
  }> {
    const plots = await db.plots.where('sync_status').equals('PENDING').count();
    const individuals = await db.individuals.where('sync_status').equals('PENDING').count();
    const traits = await db.traits.where('sync_status').equals('PENDING').count();
    const seedTrials = await db.seed_trials.where('sync_status').equals('PENDING').count();
    const soils = await db.soil_records.where('sync_status').equals('PENDING').count();
    const surveys = await db.surveys.where('sync_status').equals('PENDING').count();

    return {
      plots,
      individuals,
      traits,
      seedTrials,
      soils,
      surveys,
      total: plots + individuals + traits + seedTrials + soils + surveys,
    };
  }

  // Main synchronization pipeline: POST /api/v1/sync/field-batch
  public async syncPendingBatch(): Promise<SyncBatchResponsePayload> {
    const pendingPlots = await db.plots.where('sync_status').equals('PENDING').toArray();
    const pendingInds = await db.individuals.where('sync_status').equals('PENDING').toArray();
    const pendingTraits = await db.traits.where('sync_status').equals('PENDING').toArray();
    const pendingSeeds = await db.seed_trials.where('sync_status').equals('PENDING').toArray();
    const pendingSoils = await db.soil_records.where('sync_status').equals('PENDING').toArray();
    const pendingSurveys = await db.surveys.where('sync_status').equals('PENDING').toArray();

    const totalToSync =
      pendingPlots.length +
      pendingInds.length +
      pendingTraits.length +
      pendingSeeds.length +
      pendingSoils.length +
      pendingSurveys.length;

    if (totalToSync === 0) {
      return {
        batch_id: 'EMPTY',
        status: 'SUCCESS',
        message: 'Aucune donnée en attente de synchronisation.',
        synced_at: new Date().toISOString(),
        plots_synced: 0,
        individuals_synced: 0,
        traits_synced: 0,
        seed_trials_synced: 0,
        soil_records_synced: 0,
        surveys_synced: 0,
        flagged_outliers_count: 0,
        errors: [],
      };
    }

    const batchId = `BATCH-${Date.now()}-${Math.random().toString(36).substring(2, 7).toUpperCase()}`;

    // Format payload to strictly conform to backend SyncBatchRequest schema
    const payload: SyncBatchRequestPayload = {
      batch_id: batchId,
      device_id: this.deviceId,
      collected_at: new Date().toISOString(),
      plots: pendingPlots.map((p) => ({
        plot_id: p.plot_id,
        site_name: p.site_name,
        climatic_zone: p.climatic_zone,
        geom: p.geom || {
          type: 'Point',
          coordinates: [p.longitude, p.latitude],
        },
        elevation_m: p.elevation_m,
        slope_deg: p.slope_deg,
        protection_status: p.protection_status,
        fire_frequency_20yr: p.fire_frequency_20yr,
      })),
      individuals: pendingInds.map((i) => ({
        plot_id: i.plot_id,
        taxon_id: i.taxon_id,
        qr_code_tag: i.qr_code_tag,
        dbh_cm: Number(i.dbh_cm),
        total_height_m: Number(i.total_height_m),
        crown_diameter_m: Number(i.crown_diameter_m),
        canopy_position: i.canopy_position,
        health_status_score: Number(i.health_status_score),
        geom_tree: i.geom_tree || {
          type: 'Point',
          coordinates: [i.longitude, i.latitude],
        },
      })),
      traits: pendingTraits.map((t) => ({
        ind_id: t.ind_id,
        trait_name_ets: t.trait_name_ets,
        trait_value: Number(t.trait_value),
        unit: t.unit,
        organ_sampled: t.organ_sampled,
        measurement_protocol: t.measurement_protocol,
        instrument_id: t.instrument_id,
        measurement_date: t.measurement_date,
        operator_id: t.operator_id,
      })),
      seed_trials: pendingSeeds.map((s) => ({
        ind_id: s.ind_id,
        seed_batch_qr: s.seed_batch_qr,
        temp_regime_c: s.temp_regime_c,
        osmotic_potential_mpa: Number(s.osmotic_potential_mpa),
        pretreatment_type: s.pretreatment_type,
        total_seeds: Number(s.total_seeds),
        germinated_count: Number(s.germinated_count),
        t50_days: s.t50_days ? Number(s.t50_days) : undefined,
      })),
      soil_records: pendingSoils.map((s) => ({
        plot_id: s.plot_id,
        depth_cm: s.depth_cm,
        clay_pct: Number(s.clay_pct),
        silt_pct: Number(s.silt_pct),
        sand_pct: Number(s.sand_pct),
        ph_h2o: s.ph_h2o ? Number(s.ph_h2o) : undefined,
        organic_carbon_gkg: s.organic_carbon_gkg ? Number(s.organic_carbon_gkg) : undefined,
        total_n_gkg: s.total_n_gkg ? Number(s.total_n_gkg) : undefined,
        avail_p_mgkg: s.avail_p_mgkg ? Number(s.avail_p_mgkg) : undefined,
        cec_cmolkg: s.cec_cmolkg ? Number(s.cec_cmolkg) : undefined,
        dry_season_moisture_pct: s.dry_season_moisture_pct ? Number(s.dry_season_moisture_pct) : undefined,
        sampling_date: s.sampling_date,
      })),
      surveys: pendingSurveys.map((sv) => ({
        taxon_id: sv.taxon_id,
        respondent_type: sv.respondent_type,
        geom_village: sv.geom_village || {
          type: 'Point',
          coordinates: [sv.longitude, sv.latitude],
        },
        village_name: sv.village_name,
        climatic_zone: sv.climatic_zone,
        perceived_decline_score: Number(sv.perceived_decline_score),
        phenology_shift_observed: Boolean(sv.phenology_shift_observed),
        phenology_shift_details: sv.phenology_shift_details,
        drought_resilience_rank: Number(sv.drought_resilience_rank),
        traditional_uses: sv.traditional_uses,
        interviewer_id: sv.interviewer_id,
      })),
    };

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/v1/sync/field-batch`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        const errorLog: SyncLogEntry = {
          batch_id: batchId,
          timestamp: new Date().toISOString(),
          status: 'ERROR',
          plots_synced: 0,
          individuals_synced: 0,
          traits_synced: 0,
          surveys_synced: 0,
          flagged_outliers_count: 0,
          message: `Erreur HTTP ${response.status}: ${errorText.substring(0, 150)}`,
          errors: [errorText],
        };
        await db.sync_logs.add(errorLog);
        speechService.notifyWarning(`Échec de transmission. Code HTTP ${response.status}.`);

        return {
          batch_id: batchId,
          status: 'ERROR',
          message: `Échec de synchronisation (${response.status}): ${errorText}`,
          synced_at: new Date().toISOString(),
          plots_synced: 0,
          individuals_synced: 0,
          traits_synced: 0,
          seed_trials_synced: 0,
          soil_records_synced: 0,
          surveys_synced: 0,
          flagged_outliers_count: 0,
          errors: [errorText],
        };
      }

      const resData: SyncBatchResponsePayload = await response.json();

      // On successful ingestion, update local IndexedDB records
      if (resData.status === 'SUCCESS' || resData.status === 'PARTIAL') {
        const now = new Date().toISOString();

        // Update plots
        for (const p of pendingPlots) {
          if (p.id) await db.plots.update(p.id, { sync_status: 'SYNCED' });
        }
        // Update individuals
        for (const ind of pendingInds) {
          if (ind.id) await db.individuals.update(ind.id, { sync_status: 'SYNCED' });
        }
        // Update traits
        for (const tr of pendingTraits) {
          if (tr.id) await db.traits.update(tr.id, { sync_status: 'SYNCED' });
        }
        // Update seed trials
        for (const sd of pendingSeeds) {
          if (sd.id) await db.seed_trials.update(sd.id, { sync_status: 'SYNCED' });
        }
        // Update soil records
        for (const sl of pendingSoils) {
          if (sl.id) await db.soil_records.update(sl.id, { sync_status: 'SYNCED' });
        }
        // Update surveys
        for (const sv of pendingSurveys) {
          if (sv.id) await db.surveys.update(sv.id, { sync_status: 'SYNCED' });
        }

        // Save log
        const logEntry: SyncLogEntry = {
          batch_id: resData.batch_id,
          timestamp: now,
          status: resData.status,
          plots_synced: resData.plots_synced,
          individuals_synced: resData.individuals_synced,
          traits_synced: resData.traits_synced,
          surveys_synced: resData.surveys_synced,
          flagged_outliers_count: resData.flagged_outliers_count,
          message: resData.message,
          errors: resData.errors,
        };
        await db.sync_logs.add(logEntry);

        const syncedTotal =
          resData.plots_synced +
          resData.individuals_synced +
          resData.traits_synced +
          resData.surveys_synced;

        speechService.notifySyncComplete(syncedTotal);
      }

      return resData;
    } catch (networkErr: any) {
      const errorMsg = networkErr.message || 'Serveur injoignable (hors-ligne). Les données restent sécurisées localement.';
      const logEntry: SyncLogEntry = {
        batch_id: batchId,
        timestamp: new Date().toISOString(),
        status: 'ERROR',
        plots_synced: 0,
        individuals_synced: 0,
        traits_synced: 0,
        surveys_synced: 0,
        flagged_outliers_count: 0,
        message: errorMsg,
        errors: [errorMsg],
      };
      await db.sync_logs.add(logEntry);

      return {
        batch_id: batchId,
        status: 'ERROR',
        message: errorMsg,
        synced_at: new Date().toISOString(),
        plots_synced: 0,
        individuals_synced: 0,
        traits_synced: 0,
        seed_trials_synced: 0,
        soil_records_synced: 0,
        surveys_synced: 0,
        flagged_outliers_count: 0,
        errors: [errorMsg],
      };
    }
  }
}

export const syncService = new SyncService();
