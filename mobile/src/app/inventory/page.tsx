'use client';

import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import { Individual, CanopyPosition } from '@/types';
import GPSWidget from '@/components/GPSWidget';
import QRScannerModal from '@/components/QRScannerModal';
import CameraCapture from '@/components/CameraCapture';
import { SAHEL_TAXA, searchTaxa } from '@/lib/taxaData';
import { validateDBH, validateTreeHeight } from '@/lib/validation';
import { speechService } from '@/lib/speechFeedback';
import {
  Trees,
  Plus,
  QrCode,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Search,
  Camera,
  Activity,
  HeartPulse,
} from 'lucide-react';

export default function InventoryPage() {
  const [showForm, setShowForm] = useState<boolean>(false);
  const [isScannerOpen, setIsScannerOpen] = useState<boolean>(false);
  const [searchFilter, setSearchFilter] = useState<string>('');

  // Form states
  const [plotId, setPlotId] = useState<string>('BF-DOR-01');
  const [taxonId, setTaxonId] = useState<string>(SAHEL_TAXA[0].taxon_id);
  const [speciesSearch, setSpeciesSearch] = useState<string>('');
  const [qrCodeTag, setQrCodeTag] = useState<string>('TAG-BF-DOR-BAL-003');
  const [dbhCm, setDbhCm] = useState<string>('28.5');
  const [heightM, setHeightM] = useState<string>('7.2');
  const [crownM, setCrownM] = useState<string>('4.8');
  const [canopyPosition, setCanopyPosition] = useState<CanopyPosition>('Dominant');
  const [healthScore, setHealthScore] = useState<number>(5);
  const [lat, setLat] = useState<number>(14.0325);
  const [lng, setLng] = useState<number>(-0.0925);
  const [gpsAccuracy, setGpsAccuracy] = useState<number>(2.5);
  const [photoBase64, setPhotoBase64] = useState<string | undefined>(undefined);
  const [notes, setNotes] = useState<string>('');

  // Live queries
  const plots = useLiveQuery(() => db.plots.toArray(), [], []);
  const individuals = useLiveQuery(() => db.individuals.orderBy('created_at').reverse().toArray(), [], []);

  const selectedTaxon = SAHEL_TAXA.find((t) => t.taxon_id === taxonId);

  // Real-time validations
  const dbhVal = parseFloat(dbhCm);
  const heightVal = parseFloat(heightM);
  const dbhValidation = validateDBH(dbhVal);
  const heightValidation = validateTreeHeight(heightVal);

  const handleGenerateNextTag = () => {
    const spShort = selectedTaxon?.scientific_name.substring(0, 3).toUpperCase() || 'SP';
    const tag = `TAG-${plotId}-${spShort}-${String((individuals?.length || 0) + 1).padStart(3, '0')}`;
    setQrCodeTag(tag);
  };

  const handleSaveTree = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!dbhValidation.isValid) {
      speechService.notifyWarning(dbhValidation.message);
      alert(`Erreur : ${dbhValidation.message}`);
      return;
    }

    if (!heightValidation.isValid) {
      speechService.notifyWarning(heightValidation.message);
      alert(`Erreur : ${heightValidation.message}`);
      return;
    }

    const indId = `c${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;

    const newTree: Individual = {
      ind_id: indId,
      plot_id: plotId,
      taxon_id: taxonId,
      scientific_name: selectedTaxon?.scientific_name,
      vernacular_name: `${selectedTaxon?.vernacular_moore} / ${selectedTaxon?.vernacular_dioula} / ${selectedTaxon?.vernacular_fulfulde}`,
      qr_code_tag: qrCodeTag.trim().toUpperCase(),
      dbh_cm: dbhVal,
      total_height_m: heightVal,
      crown_diameter_m: parseFloat(crownM) || 0,
      canopy_position: canopyPosition,
      health_status_score: healthScore,
      geom_tree: {
        type: 'Point',
        coordinates: [lng, lat],
      },
      latitude: lat,
      longitude: lng,
      gps_accuracy_m: gpsAccuracy,
      photo_base64: photoBase64,
      notes: notes.trim() || undefined,
      created_at: new Date().toISOString(),
      sync_status: 'PENDING',
    };

    try {
      await db.individuals.put(newTree);
      speechService.notifyTreeSaved(selectedTaxon?.scientific_name || 'Arbre', newTree.qr_code_tag);
      setShowForm(false);
      // Prepare next tag
      handleGenerateNextTag();
      setPhotoBase64(undefined);
    } catch (err: any) {
      alert(`Erreur d'enregistrement : ${err.message}`);
    }
  };

  const filteredTaxa = searchTaxa(speciesSearch);

  const filteredTrees = (individuals || []).filter((tree) => {
    if (!searchFilter) return true;
    const q = searchFilter.toLowerCase();
    return (
      tree.qr_code_tag.toLowerCase().includes(q) ||
      (tree.scientific_name && tree.scientific_name.toLowerCase().includes(q)) ||
      (tree.vernacular_name && tree.vernacular_name.toLowerCase().includes(q)) ||
      tree.plot_id.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-black text-white flex items-center">
            <Trees className="w-5 h-5 mr-1.5 text-emerald-400" /> Inventaire Dendrométrique
          </h1>
          <p className="text-xs text-zinc-400">
            Arbres adultes (DHP ≥ 5 cm) & rattachement QR-Code
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center shadow transition active:scale-95"
        >
          <Plus className="w-4 h-4 mr-1" />
          {showForm ? 'Fermer' : 'Saisir un Arbre'}
        </button>
      </div>

      {/* FORM MODAL / ACCORDION */}
      {showForm && (
        <form
          onSubmit={handleSaveTree}
          className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-2xl animate-fade-in text-xs"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-emerald-400 flex items-center">
              <Plus className="w-4 h-4 mr-1" /> Nouvel Arbre Inventorié (DHP ≥ 5 cm)
            </h2>
            <button
              type="button"
              onClick={() => setIsScannerOpen(true)}
              className="py-1 px-2.5 bg-savanna-800 hover:bg-savanna-700 text-emerald-300 rounded-lg flex items-center text-[11px] font-semibold"
            >
              <QrCode className="w-3.5 h-3.5 mr-1" /> Scanner Tag Arbre
            </button>
          </div>

          {/* Plot & QR Tag */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">PLACETTE PARENTE *</label>
              <select
                value={plotId}
                onChange={(e) => setPlotId(e.target.value)}
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
              <div className="flex justify-between items-center mb-1">
                <label className="text-zinc-400 block">QR-CODE TAG *</label>
                <button
                  type="button"
                  onClick={handleGenerateNextTag}
                  className="text-[10px] text-emerald-400 hover:underline"
                >
                  Auto-générer
                </button>
              </div>
              <input
                type="text"
                required
                value={qrCodeTag}
                onChange={(e) => setQrCodeTag(e.target.value.toUpperCase())}
                placeholder="Ex: TAG-BF-DOR-BAL-001"
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono font-black text-emerald-400"
              />
            </div>
          </div>

          {/* Species selector */}
          <div>
            <label className="text-zinc-400 block mb-1">
              ESSENCE (Recherche Noms Scientifiques & Vernaculaires) *
            </label>
            <input
              type="text"
              placeholder="Filtrer : Kieglga, Zaanga, Baobab, Balanites..."
              value={speciesSearch}
              onChange={(e) => setSpeciesSearch(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 mb-1"
            />
            <select
              value={taxonId}
              onChange={(e) => {
                setTaxonId(e.target.value);
                const sp = SAHEL_TAXA.find((t) => t.taxon_id === e.target.value);
                if (sp) {
                  const spShort = sp.scientific_name.substring(0, 3).toUpperCase();
                  setQrCodeTag(`TAG-${plotId}-${spShort}-${String((individuals?.length || 0) + 1).padStart(3, '0')}`);
                }
              }}
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-semibold"
            >
              {filteredTaxa.map((t) => (
                <option key={t.taxon_id} value={t.taxon_id}>
                  {t.scientific_name} [Mooré: {t.vernacular_moore} | Dioula: {t.vernacular_dioula} | Fulfuldé: {t.vernacular_fulfulde}]
                </option>
              ))}
            </select>
          </div>

          {/* Dendrometry inputs */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">DHP (cm) ≥ 5 *</label>
              <input
                type="number"
                step="0.1"
                required
                value={dbhCm}
                onChange={(e) => setDbhCm(e.target.value)}
                className={`w-full bg-zinc-950 border rounded-lg p-2 font-bold font-mono text-zinc-100 ${
                  !dbhValidation.isValid
                    ? 'border-red-500 focus:ring-red-500'
                    : dbhValidation.isWarning
                    ? 'border-amber-500'
                    : 'border-zinc-700'
                }`}
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">HAUTEUR (m) *</label>
              <input
                type="number"
                step="0.1"
                required
                value={heightM}
                onChange={(e) => setHeightM(e.target.value)}
                className={`w-full bg-zinc-950 border rounded-lg p-2 font-bold font-mono text-zinc-100 ${
                  !heightValidation.isValid ? 'border-red-500' : 'border-zinc-700'
                }`}
              />
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">HOUPPIER (m)</label>
              <input
                type="number"
                step="0.1"
                value={crownM}
                onChange={(e) => setCrownM(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-bold font-mono text-zinc-100"
              />
            </div>
          </div>

          {/* Validation Feedback Banner */}
          {(!dbhValidation.isValid || dbhValidation.isWarning) && (
            <div className={`p-2 rounded-lg border flex items-start space-x-1.5 text-[11px] ${
              !dbhValidation.isValid
                ? 'bg-red-950/60 border-red-800 text-red-300'
                : 'bg-amber-950/60 border-amber-800 text-amber-300'
            }`}>
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{dbhValidation.message}</span>
            </div>
          )}

          {/* Canopy Position & Health Score */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 block mb-1">POSITION CANOPÉE</label>
              <select
                value={canopyPosition}
                onChange={(e) => setCanopyPosition(e.target.value as CanopyPosition)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
              >
                <option value="Dominant">Dominant</option>
                <option value="Codominant">Codominant</option>
                <option value="Intermédiaire">Intermédiaire</option>
                <option value="Sous-étage">Sous-étage</option>
                <option value="Émergent">Émergent (ex: Grand Baobab)</option>
              </select>
            </div>
            <div>
              <label className="text-zinc-400 block mb-1">
                SCORE SANITAIRE (1 à 5) : <strong className="text-emerald-400">{healthScore}/5</strong>
              </label>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((score) => (
                  <button
                    key={score}
                    type="button"
                    onClick={() => setHealthScore(score)}
                    className={`flex-1 py-1.5 rounded-lg border text-center font-bold transition ${
                      healthScore === score
                        ? score >= 4
                          ? 'bg-emerald-600 border-emerald-400 text-white'
                          : score === 3
                          ? 'bg-amber-600 border-amber-400 text-white'
                          : 'bg-red-600 border-red-400 text-white'
                        : 'bg-zinc-950 border-zinc-800 text-zinc-400'
                    }`}
                  >
                    {score}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* GPS Position */}
          <GPSWidget
            initialCoords={{ lat, lng }}
            onCapture={(c) => {
              setLat(c.lat);
              setLng(c.lng);
              setGpsAccuracy(c.accuracy);
            }}
          />

          {/* Camera Photo Capture */}
          <CameraCapture
            photoBase64={photoBase64}
            onPhotoChange={setPhotoBase64}
            label="Photo de l'arbre et du tronc (Caméra de terrain)"
          />

          <div>
            <label className="text-zinc-400 block mb-1">NOTES OU SÉQUELLES (gui, émondage, termites...)</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Ex: Émondé sur flanc est, fructification abondante"
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
            />
          </div>

          <button
            type="submit"
            disabled={!dbhValidation.isValid}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-xl font-bold flex items-center justify-center space-x-2 shadow-lg transition active:scale-98"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Enregistrer l'Arbre (Persistance Hors-Ligne)</span>
          </button>
        </form>
      )}

      {/* Filter and Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-3 text-zinc-500" />
        <input
          type="text"
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          placeholder="Rechercher par QR-Code, essence ou placette..."
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl pl-9 pr-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500"
        />
      </div>

      {/* List of trees */}
      <div className="space-y-2">
        {filteredTrees.length === 0 ? (
          <div className="p-8 text-center text-zinc-500 text-xs bg-zinc-900/50 rounded-2xl">
            Aucun arbre trouvé. Commencez par enregistrer un premier spécimen !
          </div>
        ) : (
          filteredTrees.map((tree) => (
            <div
              key={tree.ind_id}
              className="p-3 bg-zinc-900 border border-zinc-800 rounded-2xl flex flex-col space-y-2 hover:border-savanna-700 transition"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-black text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                    {tree.qr_code_tag}
                  </span>
                  <span className="text-[11px] text-zinc-400 font-mono">
                    Placette {tree.plot_id}
                  </span>
                </div>
                {tree.sync_status === 'SYNCED' ? (
                  <span className="text-[10px] text-emerald-400 flex items-center">
                    <CheckCircle2 className="w-3 h-3 mr-0.5" /> Synchronisé
                  </span>
                ) : (
                  <span className="text-[10px] text-sahel-400 font-bold flex items-center">
                    <Clock className="w-3 h-3 mr-0.5" /> En attente sync
                  </span>
                )}
              </div>

              <div className="flex items-start space-x-3">
                {tree.photo_base64 ? (
                  <img
                    src={tree.photo_base64}
                    alt="Arbre"
                    className="w-14 h-14 object-cover rounded-xl border border-zinc-700 flex-shrink-0"
                  />
                ) : (
                  <div className="w-14 h-14 bg-zinc-950 rounded-xl border border-zinc-800 flex items-center justify-center flex-shrink-0 text-zinc-600">
                    <Trees className="w-6 h-6" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="text-xs font-bold text-zinc-100 truncate">
                    {tree.scientific_name || 'Espèce sahélienne'}
                  </h3>
                  <div className="text-[10px] text-zinc-400 truncate">
                    {tree.vernacular_name}
                  </div>
                  <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1 text-[11px] font-mono text-zinc-300">
                    <span>DHP: <strong>{tree.dbh_cm} cm</strong></span>
                    <span>H: <strong>{tree.total_height_m} m</strong></span>
                    <span>Houppier: <strong>{tree.crown_diameter_m} m</strong></span>
                    <span className="text-emerald-400">Santé: <strong>{tree.health_status_score}/5</strong></span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* QR Scanner Modal */}
      <QRScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        onScanSuccess={(code) => setQrCodeTag(code)}
        title="Scanner QR-Code d'Arbre"
      />
    </div>
  );
}
