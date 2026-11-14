'use client';

import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import QRTagGenerator from '@/components/QRTagGenerator';
import QRScannerModal from '@/components/QRScannerModal';
import {
  QrCode,
  Scan,
  Trees,
  FlaskConical,
  CheckCircle2,
  AlertCircle,
  Clock,
  Printer,
} from 'lucide-react';

export default function QRCodeHubPage() {
  const [activeMode, setActiveMode] = useState<'generate' | 'scan'>('generate');
  const [isScannerOpen, setIsScannerOpen] = useState<boolean>(false);
  const [inspectedCode, setInspectedCode] = useState<string>('TAG-BF-DOR-BAL-001');

  const individuals = useLiveQuery(() => db.individuals.toArray(), [], []);
  const traits = useLiveQuery(() => db.traits.toArray(), [], []);

  // Find matching tree or linked traits
  const matchedTree = individuals.find(
    (i) => i.qr_code_tag === inspectedCode || inspectedCode.includes(i.qr_code_tag)
  );

  const matchedTraits = traits.filter(
    (t) =>
      t.qr_code_tag === inspectedCode ||
      (matchedTree && t.ind_id === matchedTree.ind_id)
  );

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Header */}
      <div>
        <h1 className="text-lg font-black text-white flex items-center">
          <QrCode className="w-5 h-5 mr-1.5 text-emerald-400" /> Traçabilité & QR-Codes
        </h1>
        <p className="text-xs text-zinc-400">
          Liaison biométrique : Arbre ↔ Feuilles ↔ Bois ↔ Graines ↔ Sol
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex rounded-xl bg-zinc-900 p-1 border border-zinc-800 text-xs font-semibold">
        <button
          onClick={() => setActiveMode('generate')}
          className={`flex-1 py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeMode === 'generate'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Printer className="w-4 h-4" />
          <span>Générer / Imprimer Étiquettes</span>
        </button>
        <button
          onClick={() => setActiveMode('scan')}
          className={`flex-1 py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeMode === 'scan'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Scan className="w-4 h-4" />
          <span>Inspecter Spécimen par QR</span>
        </button>
      </div>

      {/* MODE 1: GENERATE */}
      {activeMode === 'generate' && (
        <div className="space-y-3">
          <QRTagGenerator />
        </div>
      )}

      {/* MODE 2: SCAN & INSPECT */}
      {activeMode === 'scan' && (
        <div className="space-y-4 text-xs">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-bold text-zinc-200">Rechercher / Scanner un Échantillon</span>
              <button
                type="button"
                onClick={() => setIsScannerOpen(true)}
                className="py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold flex items-center shadow active:scale-95"
              >
                <Scan className="w-4 h-4 mr-1" /> Ouvrir Caméra Scanner
              </button>
            </div>

            <div>
              <label className="text-[10px] text-zinc-400 uppercase font-medium block mb-1">
                CODE OU IDENTIFIANT TAG SAISI :
              </label>
              <input
                type="text"
                value={inspectedCode}
                onChange={(e) => setInspectedCode(e.target.value.toUpperCase())}
                placeholder="Ex: TAG-BF-DOR-BAL-001"
                className="w-full bg-zinc-950 border border-zinc-700 rounded-xl p-2.5 font-mono font-black text-emerald-400 text-sm"
              />
            </div>
          </div>

          {/* Inspection results */}
          {matchedTree ? (
            <div className="bg-zinc-900 border border-savanna-700 rounded-2xl p-4 space-y-3 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded-full">
                  Spécimen Validé en Base Locale
                </span>
                <span className="font-mono text-zinc-400 text-[11px]">
                  Placette {matchedTree.plot_id}
                </span>
              </div>

              <div className="flex items-start space-x-3">
                {matchedTree.photo_base64 ? (
                  <img
                    src={matchedTree.photo_base64}
                    alt="Arbre"
                    className="w-16 h-16 object-cover rounded-xl border border-zinc-700"
                  />
                ) : (
                  <div className="w-16 h-16 bg-zinc-950 rounded-xl border border-zinc-800 flex items-center justify-center text-zinc-600">
                    <Trees className="w-8 h-8" />
                  </div>
                )}
                <div>
                  <h3 className="font-black text-sm text-zinc-100">
                    {matchedTree.scientific_name}
                  </h3>
                  <p className="text-[11px] text-zinc-400">{matchedTree.vernacular_name}</p>
                  <p className="text-[10px] font-mono text-zinc-500 mt-1">
                    GPS: {matchedTree.latitude.toFixed(5)}°, {matchedTree.longitude.toFixed(5)}°
                  </p>
                </div>
              </div>

              {/* Dendrometry summary */}
              <div className="grid grid-cols-4 gap-2 bg-zinc-950 p-2.5 rounded-xl border border-zinc-800 text-center font-mono">
                <div>
                  <span className="text-[9px] text-zinc-500 block">DHP</span>
                  <span className="font-bold text-zinc-200">{matchedTree.dbh_cm} cm</span>
                </div>
                <div>
                  <span className="text-[9px] text-zinc-500 block">HAUTEUR</span>
                  <span className="font-bold text-zinc-200">{matchedTree.total_height_m} m</span>
                </div>
                <div>
                  <span className="text-[9px] text-zinc-500 block">HOUPPIER</span>
                  <span className="font-bold text-zinc-200">{matchedTree.crown_diameter_m} m</span>
                </div>
                <div>
                  <span className="text-[9px] text-zinc-500 block">SANTÉ</span>
                  <span className="font-bold text-emerald-400">{matchedTree.health_status_score}/5</span>
                </div>
              </div>

              {/* Linked traits */}
              <div className="space-y-1.5 pt-2 border-t border-zinc-800">
                <span className="text-zinc-400 text-[11px] font-semibold flex items-center">
                  <FlaskConical className="w-3.5 h-3.5 mr-1 text-emerald-400" />
                  Mesures de traits associées ({matchedTraits.length}) :
                </span>
                {matchedTraits.length === 0 ? (
                  <p className="text-[11px] text-zinc-500 italic">
                    Aucune mesure foliaire ou de bois n'a encore été rattachée à cet arbre.
                  </p>
                ) : (
                  <div className="space-y-1">
                    {matchedTraits.map((t) => (
                      <div
                        key={t.meas_id}
                        className="flex items-center justify-between bg-zinc-950 px-2.5 py-1.5 rounded-lg border border-zinc-800"
                      >
                        <span className="font-bold text-zinc-200">
                          {t.trait_name_ets} ({t.organ_sampled})
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-emerald-400 font-bold">
                            {t.trait_value} {t.unit}
                          </span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold ${
                            t.qc_flag === 'VALID' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'
                          }`}>
                            {t.qc_flag}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-zinc-500 text-xs bg-zinc-900/40 rounded-2xl border border-zinc-800 flex flex-col items-center">
              <AlertCircle className="w-8 h-8 text-zinc-600 mb-2" />
              <span>Aucun arbre correspondant à <strong>{inspectedCode}</strong> dans le stockage local.</span>
              <span className="text-[10px] text-zinc-600 mt-1">Scannez une étiquette ou vérifiez la syntaxe du tag.</span>
            </div>
          )}
        </div>
      )}

      {/* QR Scanner Modal */}
      <QRScannerModal
        isOpen={isScannerOpen}
        onClose={() => setIsScannerOpen(false)}
        onScanSuccess={(code) => setInspectedCode(code)}
        title="Scanner QR pour Inspection"
      />
    </div>
  );
}
