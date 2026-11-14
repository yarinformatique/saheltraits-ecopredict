'use client';

import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import { SitePlot, RegenerationSubplot, ClimaticZone } from '@/types';
import GPSWidget from '@/components/GPSWidget';
import { speechService } from '@/lib/speechFeedback';
import { SAHEL_TAXA, searchTaxa } from '@/lib/taxaData';
import {
  MapPin,
  Plus,
  CheckCircle2,
  Clock,
  Layers,
  Sprout,
  Compass,
  FileSpreadsheet,
} from 'lucide-react';

export default function PlotsPage() {
  const [activeTab, setActiveTab] = useState<'plots' | 'regeneration'>('plots');
  const [showPlotForm, setShowPlotForm] = useState<boolean>(false);
  const [showRegenForm, setShowRegenForm] = useState<boolean>(false);

  // Placette form states
  const [plotId, setPlotId] = useState<string>('BF-DOR-02');
  const [siteName, setSiteName] = useState<string>('Dori - Mare de Yakouta');
  const [climaticZone, setClimaticZone] = useState<ClimaticZone>('Sahélienne');
  const [lat, setLat] = useState<number>(14.0325);
  const [lng, setLng] = useState<number>(-0.0925);
  const [elevationM, setElevationM] = useState<string>('285');
  const [slopeDeg, setSlopeDeg] = useState<string>('1.2');
  const [protectionStatus, setProtectionStatus] = useState<string>('Zone Pastorale Communale');
  const [fireFrequency, setFireFrequency] = useState<string>('1.5');
  const [notes, setNotes] = useState<string>('');
  const [gpsAccuracy, setGpsAccuracy] = useState<number>(3.2);

  // Regeneration form states
  const [selectedPlotForRegen, setSelectedPlotForRegen] = useState<string>('BF-DOR-01');
  const [subplotCode, setSubplotCode] = useState<'A' | 'B' | 'C' | 'D'>('A');
  const [regenTaxonId, setRegenTaxonId] = useState<string>(SAHEL_TAXA[0].taxon_id);
  const [regenSearch, setRegenSearch] = useState<string>('');
  const [heightClass, setHeightClass] = useState<'<50cm' | '50-150cm' | '>150cm'>('50-150cm');
  const [countIndividuals, setCountIndividuals] = useState<string>('12');

  // Queries from IndexedDB
  const plots = useLiveQuery(() => db.plots.orderBy('created_at').reverse().toArray(), [], []);
  const regenRecords = useLiveQuery(() => db.regeneration.toArray(), [], []);

  const handleSavePlot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plotId.trim() || !siteName.trim()) return;

    const newPlot: SitePlot = {
      plot_id: plotId.trim().toUpperCase(),
      site_name: siteName.trim(),
      climatic_zone: climaticZone,
      geom: {
        type: 'Point',
        coordinates: [Number(lng), Number(lat)],
      },
      latitude: Number(lat),
      longitude: Number(lng),
      elevation_m: elevationM ? parseFloat(elevationM) : undefined,
      slope_deg: slopeDeg ? parseFloat(slopeDeg) : undefined,
      protection_status: protectionStatus.trim() || undefined,
      fire_frequency_20yr: fireFrequency ? parseFloat(fireFrequency) : undefined,
      notes: notes.trim() || undefined,
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    try {
      await db.plots.put(newPlot);
      speechService.notifyPlotSaved(newPlot.plot_id, gpsAccuracy);
      setShowPlotForm(false);
      // Auto-increment plot id for next entry
      setPlotId(`BF-DOR-${String(plots.length + 3).padStart(2, '0')}`);
    } catch (err: any) {
      alert(`Erreur d'enregistrement : ${err.message}`);
    }
  };

  const handleSaveRegeneration = async (e: React.FormEvent) => {
    e.preventDefault();
    const taxon = SAHEL_TAXA.find((t) => t.taxon_id === regenTaxonId);

    const record: RegenerationSubplot = {
      sub_id: `REGEN-${Date.now()}`,
      plot_id: selectedPlotForRegen,
      subplot_code: subplotCode,
      dimension_m: '5x5',
      taxon_id: regenTaxonId,
      scientific_name: taxon?.scientific_name || 'Espèce inconnue',
      height_class: heightClass,
      count_individuals: parseInt(countIndividuals) || 0,
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    await db.regeneration.add(record);
    speechService.speak(`Régénération ${taxon?.vernacular_moore || taxon?.scientific_name} ajoutée.`);
    setShowRegenForm(false);
  };

  const filteredTaxa = searchTaxa(regenSearch);

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Header & Tabs */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-black text-white flex items-center">
            <MapPin className="w-5 h-5 mr-1.5 text-emerald-400" /> Gestion des Placettes
          </h1>
          <p className="text-xs text-zinc-400">
            Dispositif permanent 50 m × 20 m (1 000 m²) & sous-placettes 5 m × 5 m
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex rounded-xl bg-zinc-900 p-1 border border-zinc-800 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('plots')}
          className={`flex-1 py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'plots'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Placettes ({plots.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('regeneration')}
          className={`flex-1 py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'regeneration'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Sprout className="w-4 h-4" />
          <span>Régénération 5×5m ({regenRecords.length})</span>
        </button>
      </div>

      {/* TAB 1: PLOTS */}
      {activeTab === 'plots' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs text-zinc-400 font-medium">
              Norme standard : 50m longueur × 20m largeur
            </span>
            <button
              onClick={() => setShowPlotForm(!showPlotForm)}
              className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center shadow transition active:scale-95"
            >
              <Plus className="w-4 h-4 mr-1" />
              {showPlotForm ? 'Fermer le formulaire' : 'Nouvelle Placette'}
            </button>
          </div>

          {/* New Plot Form */}
          {showPlotForm && (
            <form
              onSubmit={handleSavePlot}
              className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-xl animate-fade-in"
            >
              <h2 className="text-sm font-bold text-emerald-400 flex items-center">
                <Plus className="w-4 h-4 mr-1" /> Création d'une Placette (50 m × 20 m)
              </h2>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <label className="text-zinc-400 block mb-1">CODE PLACETTE *</label>
                  <input
                    type="text"
                    required
                    value={plotId}
                    onChange={(e) => setPlotId(e.target.value.toUpperCase())}
                    placeholder="Ex: BF-DOR-01"
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono text-zinc-100 font-bold"
                  />
                </div>
                <div>
                  <label className="text-zinc-400 block mb-1">ZONE BIOCLIMATIQUE *</label>
                  <select
                    value={climaticZone}
                    onChange={(e) => setClimaticZone(e.target.value as ClimaticZone)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  >
                    <option value="Sahélienne">Sahélienne (&lt;600mm)</option>
                    <option value="Soudano-Sahélienne">Soudano-Sahélienne (600-900mm)</option>
                    <option value="Soudanienne">Soudanienne (&gt;900mm)</option>
                  </select>
                </div>
              </div>

              <div className="text-xs">
                <label className="text-zinc-400 block mb-1">NOM DU SITE / LOCALITÉ *</label>
                <input
                  type="text"
                  required
                  value={siteName}
                  onChange={(e) => setSiteName(e.target.value)}
                  placeholder="Ex: Dori - Mare de Yakouta"
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                />
              </div>

              {/* Native GPS capture */}
              <GPSWidget
                initialCoords={{ lat, lng }}
                onCapture={(c) => {
                  setLat(c.lat);
                  setLng(c.lng);
                  if (c.altitude) setElevationM(c.altitude.toFixed(1));
                  setGpsAccuracy(c.accuracy);
                }}
              />

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <label className="text-zinc-400 block mb-1">ALTITUDE (m)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={elevationM}
                    onChange={(e) => setElevationM(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  />
                </div>
                <div>
                  <label className="text-zinc-400 block mb-1">PENTE TERRAIN (°)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={slopeDeg}
                    onChange={(e) => setSlopeDeg(e.target.value)}
                    placeholder="Ex: 1.5"
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <label className="text-zinc-400 block mb-1">STATUT PROTECTION</label>
                  <input
                    type="text"
                    value={protectionStatus}
                    onChange={(e) => setProtectionStatus(e.target.value)}
                    placeholder="Ex: Forêt Classée"
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  />
                </div>
                <div>
                  <label className="text-zinc-400 block mb-1">FRÉQUENCE FEUX (20 ANS)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={fireFrequency}
                    onChange={(e) => setFireFrequency(e.target.value)}
                    placeholder="Ex: 2.5"
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  />
                </div>
              </div>

              <div className="text-xs">
                <label className="text-zinc-400 block mb-1">NOTES ÉCOLOGIQUES / HISTORIQUE</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Type de sol, faciès de végétation, perturbations observées..."
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-lg flex items-center justify-center space-x-2 active:scale-98"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Enregistrer la Placette (Persistance IndexedDB)</span>
              </button>
            </form>
          )}

          {/* List of existing plots */}
          <div className="space-y-2">
            {plots.map((plot) => (
              <div
                key={plot.plot_id}
                className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl space-y-1.5 hover:border-savanna-800 transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-black text-sm text-emerald-400">
                      {plot.plot_id}
                    </span>
                    <span className="text-[10px] bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded font-medium">
                      {plot.climatic_zone}
                    </span>
                  </div>
                  {plot.sync_status === 'SYNCED' ? (
                    <span className="text-[10px] text-emerald-400 flex items-center">
                      <CheckCircle2 className="w-3 h-3 mr-1" /> Synchronisé
                    </span>
                  ) : (
                    <span className="text-[10px] text-sahel-400 flex items-center font-bold">
                      <Clock className="w-3 h-3 mr-1" /> En attente sync
                    </span>
                  )}
                </div>

                <div className="text-xs font-semibold text-zinc-200">
                  {plot.site_name}
                </div>

                <div className="flex items-center space-x-3 text-[11px] text-zinc-400 font-mono">
                  <span>GPS: {plot.latitude.toFixed(4)}°, {plot.longitude.toFixed(4)}°</span>
                  {plot.elevation_m && <span>Alt: {plot.elevation_m}m</span>}
                  {plot.slope_deg && <span>Pente: {plot.slope_deg}°</span>}
                </div>

                {plot.notes && (
                  <p className="text-[11px] text-zinc-400 italic">
                    {plot.notes}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: REGENERATION SUBPLOTS */}
      {activeTab === 'regeneration' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs text-zinc-400 font-medium">
              4 sous-placettes (A, B, C, D) de 5 m × 5 m (25 m²)
            </span>
            <button
              onClick={() => setShowRegenForm(!showRegenForm)}
              className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center shadow transition active:scale-95"
            >
              <Plus className="w-4 h-4 mr-1" />
              {showRegenForm ? 'Fermer' : 'Saisir Régénération'}
            </button>
          </div>

          {showRegenForm && (
            <form
              onSubmit={handleSaveRegeneration}
              className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3 shadow-xl animate-fade-in text-xs"
            >
              <h2 className="font-bold text-emerald-400 text-sm flex items-center">
                <Sprout className="w-4 h-4 mr-1" /> Relevé Sous-Placette (5 m × 5 m)
              </h2>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-zinc-400 block mb-1">PLACETTE PARENTE</label>
                  <select
                    value={selectedPlotForRegen}
                    onChange={(e) => setSelectedPlotForRegen(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-mono font-bold"
                  >
                    {plots.map((p) => (
                      <option key={p.plot_id} value={p.plot_id}>
                        {p.plot_id} ({p.site_name})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-zinc-400 block mb-1">QUADRANT (5×5m)</label>
                  <select
                    value={subplotCode}
                    onChange={(e) => setSubplotCode(e.target.value as any)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-bold"
                  >
                    <option value="A">Sous-placette A (Coin SO)</option>
                    <option value="B">Sous-placette B (Coin NO)</option>
                    <option value="C">Sous-placette C (Coin SE)</option>
                    <option value="D">Sous-placette D (Coin NE)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">RECHERCHER ESSENCE (Mooré/Dioula/Fulfuldé)</label>
                <input
                  type="text"
                  placeholder="Ex: Kieglga, Balanites, Zaanga..."
                  value={regenSearch}
                  onChange={(e) => setRegenSearch(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 mb-1"
                />
                <select
                  value={regenTaxonId}
                  onChange={(e) => setRegenTaxonId(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  {filteredTaxa.map((t) => (
                    <option key={t.taxon_id} value={t.taxon_id}>
                      {t.scientific_name} — {t.vernacular_moore} / {t.vernacular_dioula} / {t.vernacular_fulfulde}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-zinc-400 block mb-1">CLASSE DE HAUTEUR</label>
                  <select
                    value={heightClass}
                    onChange={(e) => setHeightClass(e.target.value as any)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  >
                    <option value="<50cm">Semis &lt; 50 cm</option>
                    <option value="50-150cm">Gaulis 50 - 150 cm</option>
                    <option value=">150cm">Perchis &gt; 150 cm (DHP &lt; 5 cm)</option>
                  </select>
                </div>
                <div>
                  <label className="text-zinc-400 block mb-1">NOMBRE DE TIGES RELEVÉES</label>
                  <input
                    type="number"
                    min="1"
                    value={countIndividuals}
                    onChange={(e) => setCountIndividuals(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-bold"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center justify-center space-x-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Enregistrer Régénération</span>
              </button>
            </form>
          )}

          {/* List of regeneration records */}
          <div className="space-y-2">
            {regenRecords.length === 0 ? (
              <div className="p-6 text-center text-zinc-500 text-xs bg-zinc-900/50 rounded-xl">
                Aucun relevé de régénération saisi pour l'instant.
              </div>
            ) : (
              regenRecords.map((r) => (
                <div
                  key={r.sub_id}
                  className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-bold text-zinc-100">{r.scientific_name}</span>
                    <div className="text-[11px] text-zinc-400">
                      Placette <strong>{r.plot_id}</strong> (Quadrant {r.subplot_code} 5×5m) • {r.height_class}
                    </div>
                  </div>
                  <span className="px-2.5 py-1 bg-savanna-950 border border-savanna-800 text-emerald-400 rounded-lg font-black text-sm">
                    {r.count_individuals} tiges
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
