'use client';

import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import { TraitMeasurement, SeedTrial, SoilRecord } from '@/types';
import QRScannerModal from '@/components/QRScannerModal';
import { SAHEL_TAXA, findTaxonById } from '@/lib/taxaData';
import { validateLeafMasses, validateTraitOutlier3Sigma, validateSoilTexture } from '@/lib/validation';
import { speechService } from '@/lib/speechFeedback';
import {
  FlaskConical,
  QrCode,
  CheckCircle2,
  AlertTriangle,
  Leaf,
  Layers,
  Sprout,
  Droplets,
  Plus,
  Scale,
} from 'lucide-react';

export default function TraitsPage() {
  const [activeTab, setActiveTab] = useState<'leaf' | 'wood' | 'seeds' | 'soil'>('leaf');
  const [isScannerOpen, setIsScannerOpen] = useState<boolean>(false);

  // Foliaire (SLA & LDMC)
  const [leafQrTag, setLeafQrTag] = useState<string>('TAG-BF-DOR-BAL-001');
  const [leafAreaMm2, setLeafAreaMm2] = useState<string>('985.0');
  const [freshMassMg, setFreshMassMg] = useState<string>('235.0');
  const [dryMassMg, setDryMassMg] = useState<string>('99.5');
  const [instrumentId, setInstrumentId] = useState<string>('SCAN-EPSR-01');

  // Bois
  const [woodQrTag, setWoodQrTag] = useState<string>('TAG-BF-DOR-BAL-001');
  const [woodVolumeCm3, setWoodVolumeCm3] = useState<string>('15.4');
  const [woodDryMassG, setWoodDryMassG] = useState<string>('11.1');

  // Graines
  const [seedQrTag, setSeedQrTag] = useState<string>('LOT-BAL-DOR-2026-A');
  const [tempRegime, setTempRegime] = useState<string>('30/20');
  const [osmoticMpa, setOsmoticMpa] = useState<string>('0.0');
  const [pretreatment, setPretreatment] = useState<string>('Scarification mécanique');
  const [totalSeeds, setTotalSeeds] = useState<string>('50');
  const [germinatedCount, setGerminatedCount] = useState<string>('44');
  const [t50Days, setT50Days] = useState<string>('4.2');

  // Sol
  const [soilPlotId, setSoilPlotId] = useState<string>('BF-DOR-01');
  const [depthCm, setDepthCm] = useState<string>('0-20');
  const [clayPct, setClayPct] = useState<string>('12.5');
  const [siltPct, setSiltPct] = useState<string>('18.0');
  const [sandPct, setSandPct] = useState<string>('69.5');
  const [phH2o, setPhH2o] = useState<string>('6.8');
  const [organicCarbon, setOrganicCarbon] = useState<string>('4.2');

  // IndexedDB data
  const individuals = useLiveQuery(() => db.individuals.toArray(), [], []);
  const traitsList = useLiveQuery(() => db.traits.orderBy('created_at').reverse().toArray(), [], []);
  const seedTrialsList = useLiveQuery(() => db.seed_trials.orderBy('created_at').reverse().toArray(), [], []);
  const soilList = useLiveQuery(() => db.soil_records.orderBy('created_at').reverse().toArray(), [], []);
  const plots = useLiveQuery(() => db.plots.toArray(), [], []);

  // Matching tree for leaf
  const matchedTree = individuals.find(
    (i) => i.qr_code_tag === leafQrTag || leafQrTag.includes(i.qr_code_tag)
  );

  // Calculations for Leaf
  const freshMg = parseFloat(freshMassMg) || 0;
  const dryMg = parseFloat(dryMassMg) || 0;
  const areaMm2 = parseFloat(leafAreaMm2) || 0;

  // Real-time leaf validation
  const massValidation = validateLeafMasses(freshMg, dryMg);

  // SLA = Area / Dry mass (mm2/mg)
  const computedSLA = dryMg > 0 ? areaMm2 / dryMg : 0;
  // LDMC = Dry mass / Fresh mass (mg/g)
  const computedLDMC = freshMg > 0 ? (dryMg / freshMg) * 1000 : 0;

  // 3-Sigma validation for SLA
  const sla3SigmaValidation = matchedTree?.taxon_id
    ? validateTraitOutlier3Sigma(matchedTree.taxon_id, 'SLA', computedSLA)
    : { isValid: true, isWarning: false, message: 'Prêt' };

  // Calculations for Wood
  const woodVol = parseFloat(woodVolumeCm3) || 0;
  const woodDry = parseFloat(woodDryMassG) || 0;
  const computedWoodDensity = woodVol > 0 ? woodDry / woodVol : 0;

  // Soil texture validation
  const soilValidation = validateSoilTexture(
    parseFloat(clayPct) || 0,
    parseFloat(siltPct) || 0,
    parseFloat(sandPct) || 0
  );

  // Handle Save Leaf Trait (SLA + LDMC)
  const handleSaveLeafTrait = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!massValidation.isValid) {
      speechService.notifyWarning(massValidation.message);
      alert(massValidation.message);
      return;
    }

    const indId = matchedTree?.ind_id || 'ind001';
    const measDate = new Date().toISOString().split('T')[0];

    const qcFlag = sla3SigmaValidation.isWarning ? 'SUSPECT_OUTLIER_3SIGMA' : 'VALID';

    // 1. SLA measurement
    const slaMeas: TraitMeasurement = {
      meas_id: `meas-${Date.now()}-sla`,
      ind_id: indId,
      qr_code_tag: leafQrTag,
      trait_name_ets: 'SLA',
      trait_value: Math.round(computedSLA * 100) / 100,
      unit: 'mm2/mg',
      organ_sampled: 'Feuille',
      measurement_protocol: 'Cornelissen et al. (2003) - Scanner 600dpi',
      instrument_id: instrumentId,
      fresh_mass_mg: freshMg,
      dry_mass_mg: dryMg,
      leaf_area_mm2: areaMm2,
      measurement_date: measDate,
      qc_flag: qcFlag,
      qc_notes: sla3SigmaValidation.isWarning ? sla3SigmaValidation.message : undefined,
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    // 2. LDMC measurement
    const ldmcMeas: TraitMeasurement = {
      meas_id: `meas-${Date.now()}-ldmc`,
      ind_id: indId,
      qr_code_tag: leafQrTag,
      trait_name_ets: 'LDMC',
      trait_value: Math.round(computedLDMC * 10) / 10,
      unit: 'mg/g',
      organ_sampled: 'Feuille',
      measurement_protocol: 'Poids frais réhydraté / Poids sec 72h',
      instrument_id: instrumentId,
      fresh_mass_mg: freshMg,
      dry_mass_mg: dryMg,
      measurement_date: measDate,
      qc_flag: 'VALID',
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    await db.traits.bulkAdd([slaMeas, ldmcMeas]);
    speechService.notifyTraitSaved('SLA', slaMeas.trait_value, 'mm2/mg');
    if (sla3SigmaValidation.isWarning) {
      speechService.notifyWarning(sla3SigmaValidation.message);
    }
    alert('Mesures foliaires SLA et LDMC enregistrées avec succès dans la base locale.');
  };

  // Handle Save Wood
  const handleSaveWoodTrait = async (e: React.FormEvent) => {
    e.preventDefault();
    const indId = matchedTree?.ind_id || 'ind001';
    const densityVal = Math.round(computedWoodDensity * 100) / 100;

    const woodMeas: TraitMeasurement = {
      meas_id: `meas-${Date.now()}-wood`,
      ind_id: indId,
      qr_code_tag: woodQrTag,
      trait_name_ets: 'Wood_density',
      trait_value: densityVal,
      unit: 'g/cm3',
      organ_sampled: 'Rameau',
      measurement_protocol: 'Archimède déplacement d\'eau & pesée sèche',
      measurement_date: new Date().toISOString().split('T')[0],
      qc_flag: densityVal < 0.2 || densityVal > 1.2 ? 'SUSPECT_OUTLIER_3SIGMA' : 'VALID',
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    await db.traits.add(woodMeas);
    speechService.notifyTraitSaved('Densité du bois', densityVal, 'g/cm3');
    alert(`Densité du bois (${densityVal} g/cm3) enregistrée avec succès.`);
  };

  // Handle Save Seed
  const handleSaveSeed = async (e: React.FormEvent) => {
    e.preventDefault();
    const indId = matchedTree?.ind_id || 'ind001';
    const tot = parseInt(totalSeeds) || 0;
    const germ = parseInt(germinatedCount) || 0;
    const gp = tot > 0 ? (germ / tot) * 100 : 0;

    const seed: SeedTrial = {
      germ_id: `germ-${Date.now()}`,
      ind_id: indId,
      seed_batch_qr: seedQrTag,
      temp_regime_c: tempRegime,
      osmotic_potential_mpa: parseFloat(osmoticMpa) || 0,
      pretreatment_type: pretreatment,
      total_seeds: tot,
      germinated_count: germ,
      t50_days: parseFloat(t50Days) || undefined,
      final_gp_pct: Math.round(gp * 10) / 10,
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    await db.seed_trials.add(seed);
    speechService.speak(`Essai germinatif lot ${seedQrTag} enregistré avec taux ${seed.final_gp_pct}%.`);
    alert('Essai germinatif enregistré avec succès.');
  };

  // Handle Save Soil
  const handleSaveSoil = async (e: React.FormEvent) => {
    e.preventDefault();
    const soil: SoilRecord = {
      env_id: `soil-${Date.now()}`,
      plot_id: soilPlotId,
      depth_cm: depthCm,
      clay_pct: parseFloat(clayPct) || 0,
      silt_pct: parseFloat(siltPct) || 0,
      sand_pct: parseFloat(sandPct) || 0,
      ph_h2o: phH2o ? parseFloat(phH2o) : undefined,
      organic_carbon_gkg: organicCarbon ? parseFloat(organicCarbon) : undefined,
      sampling_date: new Date().toISOString().split('T')[0],
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    await db.soil_records.add(soil);
    speechService.speak(`Données pédologiques placette ${soilPlotId} enregistrées.`);
    alert('Échantillon de sol enregistré.');
  };

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Header */}
      <div>
        <h1 className="text-lg font-black text-white flex items-center">
          <FlaskConical className="w-5 h-5 mr-1.5 text-emerald-400" /> Mesures Traits & Laboratoire
        </h1>
        <p className="text-xs text-zinc-400">
          Standard ETS v1.0, validation biologique temps réel & détection 3-sigmas
        </p>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-4 gap-1 rounded-xl bg-zinc-900 p-1 border border-zinc-800 text-[11px] font-semibold">
        <button
          onClick={() => setActiveTab('leaf')}
          className={`py-2 rounded-lg flex flex-col items-center justify-center transition ${
            activeTab === 'leaf'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Leaf className="w-4 h-4 mb-0.5" />
          <span>Foliaire (SLA)</span>
        </button>
        <button
          onClick={() => setActiveTab('wood')}
          className={`py-2 rounded-lg flex flex-col items-center justify-center transition ${
            activeTab === 'wood'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Layers className="w-4 h-4 mb-0.5" />
          <span>Bois (Densité)</span>
        </button>
        <button
          onClick={() => setActiveTab('seeds')}
          className={`py-2 rounded-lg flex flex-col items-center justify-center transition ${
            activeTab === 'seeds'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Sprout className="w-4 h-4 mb-0.5" />
          <span>Germination</span>
        </button>
        <button
          onClick={() => setActiveTab('soil')}
          className={`py-2 rounded-lg flex flex-col items-center justify-center transition ${
            activeTab === 'soil'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Droplets className="w-4 h-4 mb-0.5" />
          <span>Sol & Pédologie</span>
        </button>
      </div>

      {/* TAB 1: TRAIT FOLIAIRE (SLA & LDMC) */}
      {activeTab === 'leaf' && (
        <form
          onSubmit={handleSaveLeafTrait}
          className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-xl animate-fade-in text-xs"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-emerald-400 flex items-center">
              <Leaf className="w-4 h-4 mr-1" /> Traits Foliaires : SLA (mm²/mg) & LDMC (mg/g)
            </h2>
            <button
              type="button"
              onClick={() => setIsScannerOpen(true)}
              className="py-1 px-2 bg-savanna-800 hover:bg-savanna-700 text-emerald-300 rounded-lg flex items-center text-[10px] font-bold"
            >
              <QrCode className="w-3.5 h-3.5 mr-1" /> Scanner Sachet
            </button>
          </div>

          <div>
            <label className="text-zinc-400 block mb-1">
              QR-CODE ÉCHANTILLON FEUILLES / ARBRE *
            </label>
            <input
              type="text"
              required
              value={leafQrTag}
              onChange={(e) => setLeafQrTag(e.target.value.toUpperCase())}
              placeholder="Ex: TAG-BF-DOR-BAL-001"
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-black text-emerald-400 text-xs"
            />
            {matchedTree && (
              <span className="text-[10px] text-zinc-400 block mt-1">
                Arbre identifié : <strong>{matchedTree.scientific_name}</strong> (Placette {matchedTree.plot_id})
              </span>
            )}
          </div>

          {/* Measurements */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">SURFACE (mm²)</label>
              <input
                type="number"
                step="0.1"
                required
                value={leafAreaMm2}
                onChange={(e) => setLeafAreaMm2(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">M. FRAÎCHE (mg)</label>
              <input
                type="number"
                step="0.1"
                required
                value={freshMassMg}
                onChange={(e) => setFreshMassMg(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">M. SÈCHE (mg)</label>
              <input
                type="number"
                step="0.1"
                required
                value={dryMassMg}
                onChange={(e) => setDryMassMg(e.target.value)}
                className={`w-full bg-zinc-950 border rounded-lg p-2 font-mono font-bold text-zinc-100 ${
                  !massValidation.isValid ? 'border-red-500' : 'border-zinc-700'
                }`}
              />
            </div>
          </div>

          {/* STRICT VALIDATION ALERT */}
          {!massValidation.isValid && (
            <div className="p-2.5 rounded-xl bg-red-950/80 border border-red-700 text-red-200 flex items-start space-x-2 text-xs animate-shake">
              <AlertTriangle className="w-5 h-5 flex-shrink-0 text-red-400" />
              <div>
                <strong className="block font-bold">RÈGLE BIOLOGIQUE VIOLEÉ</strong>
                <span>{massValidation.message}</span>
              </div>
            </div>
          )}

          {/* 3-SIGMA OUTLIER DETECTION */}
          {sla3SigmaValidation.isWarning && (
            <div className="p-2.5 rounded-xl bg-amber-950/70 border border-amber-600 text-amber-200 flex items-start space-x-2 text-xs">
              <AlertTriangle className="w-5 h-5 flex-shrink-0 text-amber-400" />
              <div>
                <strong className="block font-bold">DÉTECTION STATISTIQUE 3-SIGMA</strong>
                <span>{sla3SigmaValidation.message}</span>
              </div>
            </div>
          )}

          {/* Real-time Computed Values Card */}
          <div className="p-3 bg-zinc-950 rounded-xl border border-zinc-800 grid grid-cols-2 gap-3 text-center">
            <div>
              <span className="text-[10px] text-zinc-500 uppercase block">SLA CALCULÉ</span>
              <span className="text-lg font-black text-emerald-400 font-mono">
                {computedSLA > 0 ? computedSLA.toFixed(2) : '—'}{' '}
                <span className="text-xs font-normal text-zinc-400">mm²/mg</span>
              </span>
            </div>
            <div>
              <span className="text-[10px] text-zinc-500 uppercase block">LDMC CALCULÉ</span>
              <span className="text-lg font-black text-sahel-400 font-mono">
                {computedLDMC > 0 ? computedLDMC.toFixed(1) : '—'}{' '}
                <span className="text-xs font-normal text-zinc-400">mg/g</span>
              </span>
            </div>
          </div>

          <div>
            <label className="text-zinc-400 block mb-1">INSTRUMENT DE MESURE (Scanner / Balance)</label>
            <input
              type="text"
              value={instrumentId}
              onChange={(e) => setInstrumentId(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
            />
          </div>

          <button
            type="submit"
            disabled={!massValidation.isValid}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-xl font-bold flex items-center justify-center space-x-2 shadow-lg transition active:scale-98"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Valider et Enregistrer Mesures Foliaires</span>
          </button>
        </form>
      )}

      {/* TAB 2: TRAIT BOIS (DENSITÉ) */}
      {activeTab === 'wood' && (
        <form
          onSubmit={handleSaveWoodTrait}
          className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-xl animate-fade-in text-xs"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-emerald-400 flex items-center">
              <Layers className="w-4 h-4 mr-1" /> Densité du Bois (Wood density g/cm³)
            </h2>
            <button
              type="button"
              onClick={() => setIsScannerOpen(true)}
              className="py-1 px-2 bg-savanna-800 hover:bg-savanna-700 text-emerald-300 rounded-lg flex items-center text-[10px] font-bold"
            >
              <QrCode className="w-3.5 h-3.5 mr-1" /> Scanner Échantillon
            </button>
          </div>

          <div>
            <label className="text-zinc-400 block mb-1">QR-CODE CAROTTE / RAMEAU *</label>
            <input
              type="text"
              required
              value={woodQrTag}
              onChange={(e) => setWoodQrTag(e.target.value.toUpperCase())}
              placeholder="Ex: TAG-WOOD-BF-DOR-BAL-001"
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-black text-emerald-400 text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">VOLUME FRAIS DÉPLACÉ (cm³) *</label>
              <input
                type="number"
                step="0.01"
                required
                value={woodVolumeCm3}
                onChange={(e) => setWoodVolumeCm3(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">MASSE SÈCHE À L'ÉTUVE (g) *</label>
              <input
                type="number"
                step="0.01"
                required
                value={woodDryMassG}
                onChange={(e) => setWoodDryMassG(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
          </div>

          {/* Computed Density Card */}
          <div className="p-3 bg-zinc-950 rounded-xl border border-zinc-800 text-center">
            <span className="text-[10px] text-zinc-500 uppercase block">DENSITÉ DU BOIS ESTIMÉE</span>
            <span className="text-2xl font-black text-emerald-400 font-mono">
              {computedWoodDensity > 0 ? computedWoodDensity.toFixed(3) : '—'}{' '}
              <span className="text-sm font-normal text-zinc-400">g/cm³</span>
            </span>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center justify-center space-x-2 shadow-lg"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Enregistrer la Mesure de Densité</span>
          </button>
        </form>
      )}

      {/* TAB 3: ESSAIS GERMINATIFS */}
      {activeTab === 'seeds' && (
        <form
          onSubmit={handleSaveSeed}
          className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-xl animate-fade-in text-xs"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-emerald-400 flex items-center">
              <Sprout className="w-4 h-4 mr-1" /> Essais Germinatifs & Résilience Semences
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">QR-CODE LOT SEMENCES *</label>
              <input
                type="text"
                required
                value={seedQrTag}
                onChange={(e) => setSeedQrTag(e.target.value.toUpperCase())}
                placeholder="Ex: LOT-BAL-DOR-2026-A"
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">RÉGIME TEMPÉRATURE (°C)</label>
              <select
                value={tempRegime}
                onChange={(e) => setTempRegime(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
              >
                <option value="30/20">30°C Jour / 20°C Nuit (Standard)</option>
                <option value="35/25">35°C Jour / 25°C Nuit (Canicule)</option>
                <option value="40/30">40°C Jour / 30°C Nuit (Stress Extrême)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">POTENTIEL OSMOTIQUE (MPa)</label>
              <select
                value={osmoticMpa}
                onChange={(e) => setOsmoticMpa(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
              >
                <option value="0.0">0.0 MPa (Témoin Eau)</option>
                <option value="-0.4">-0.4 MPa (PEG-6000 Stress Modéré)</option>
                <option value="-0.8">-0.8 MPa (PEG-6000 Stress Sévère)</option>
              </select>
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">PRÉ-TRAITEMENT</label>
              <input
                type="text"
                value={pretreatment}
                onChange={(e) => setPretreatment(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">TOTAL GRAINES</label>
              <input
                type="number"
                value={totalSeeds}
                onChange={(e) => setTotalSeeds(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-bold text-zinc-100 font-mono"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">GRAINES GERMÉES</label>
              <input
                type="number"
                value={germinatedCount}
                onChange={(e) => setGerminatedCount(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-bold text-zinc-100 font-mono"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">T50 (JOURS)</label>
              <input
                type="number"
                step="0.1"
                value={t50Days}
                onChange={(e) => setT50Days(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-bold text-zinc-100 font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center justify-center space-x-2 shadow-lg"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Enregistrer Essai de Germination</span>
          </button>
        </form>
      )}

      {/* TAB 4: SOL & PÉDOLOGIE */}
      {activeTab === 'soil' && (
        <form
          onSubmit={handleSaveSoil}
          className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-xl animate-fade-in text-xs"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-emerald-400 flex items-center">
              <Droplets className="w-4 h-4 mr-1" /> Relevé Pédologique de Placette
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">PLACETTE PARENTE *</label>
              <select
                value={soilPlotId}
                onChange={(e) => setSoilPlotId(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              >
                {plots.map((p) => (
                  <option key={p.plot_id} value={p.plot_id}>
                    {p.plot_id} ({p.site_name})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">PROFONDEUR (cm)</label>
              <select
                value={depthCm}
                onChange={(e) => setDepthCm(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
              >
                <option value="0-20">0 - 20 cm (Horizon superficiel)</option>
                <option value="20-40">20 - 40 cm (Horizon sous-jacent)</option>
              </select>
            </div>
          </div>

          {/* Granulometry */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">ARGILE (%)</label>
              <input
                type="number"
                step="0.1"
                value={clayPct}
                onChange={(e) => setClayPct(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">LIMON (%)</label>
              <input
                type="number"
                step="0.1"
                value={siltPct}
                onChange={(e) => setSiltPct(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">SABLE (%)</label>
              <input
                type="number"
                step="0.1"
                value={sandPct}
                onChange={(e) => setSandPct(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
          </div>

          {/* Granulometry Warning */}
          {soilValidation.isWarning && (
            <div className="p-2 rounded-lg bg-amber-950/60 border border-amber-800 text-amber-300 flex items-start space-x-1.5 text-[11px]">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{soilValidation.message}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">pH (H₂O)</label>
              <input
                type="number"
                step="0.1"
                value={phH2o}
                onChange={(e) => setPhH2o(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">CARBONE ORG. (g/kg)</label>
              <input
                type="number"
                step="0.1"
                value={organicCarbon}
                onChange={(e) => setOrganicCarbon(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-bold text-zinc-100"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center justify-center space-x-2 shadow-lg"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Enregistrer Relevé Pédologique</span>
          </button>
        </form>
      )}

      {/* QR Scanner */}
      <QRScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        onScanSuccess={(code) => {
          if (activeTab === 'leaf') setLeafQrTag(code);
          if (activeTab === 'wood') setWoodQrTag(code);
          if (activeTab === 'seeds') setSeedQrTag(code);
        }}
        title="Scanner QR-Code Échantillon Lab"
      />
    </div>
  );
}
