"use client";

import React, { useState } from "react";
import { X, Download, Copy, Check, FileSpreadsheet, FileCode, Archive, BookMarked } from "lucide-react";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultSpecies?: string;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  defaultSpecies,
}) => {
  const [format, setFormat] = useState<"csv" | "json" | "dwca">("csv");
  const [speciesFilter, setSpeciesFilter] = useState(defaultSpecies || "");
  const [zoneFilter, setZoneFilter] = useState("");
  const [qcFilter, setQcFilter] = useState("VALID");
  const [copiedCitation, setCopiedCitation] = useState(false);

  if (!isOpen) return null;

  const citationAPA = `Yago, A. R., Ouédraogo, A., Sawadogo, M., & Dupont, J. (2026). SahelTraits-DB: A standardized multi-organ functional trait database and EcoPredict vulnerability projection system for Sahelian and Sudano-Sahelian woody flora (Version 1.0.0) [Data set]. Université Joseph Ki-Zerbo (UJKZ-ICC). https://doi.org/10.5281/zenodo.14202600`;

  const citationBibTeX = `@dataset{yago2026saheltraits,
  author    = {Yago, Abdoul Rachide and Ouédraogo, Amadé and Sawadogo, Moussa and Dupont, Jean},
  title     = {{SahelTraits-DB: A standardized multi-organ functional trait database and EcoPredict vulnerability projection system for Sahelian and Sudano-Sahelian woody flora}},
  year      = {2026},
  version   = {1.0.0},
  publisher = {Université Joseph Ki-Zerbo / UJKZ-ICC},
  doi       = {10.5281/zenodo.14202600},
  url       = {https://saheltraits.ujkz.bf}
}`;

  const handleCopyCitation = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCitation(true);
    setTimeout(() => setCopiedCitation(false), 2000);
  };

  const handleTriggerDownload = () => {
    const params = new URLSearchParams();
    params.append("format", format);
    if (speciesFilter) params.append("species", speciesFilter);
    if (zoneFilter) params.append("climatic_zone", zoneFilter);
    if (qcFilter) params.append("qc_status", qcFilter);

    // Call FastAPI backend export endpoint
    const url = `http://localhost:8000/api/v1/traits/export?${params.toString()}`;
    window.open(url, "_blank");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Download className="w-5 h-5 text-sahel-400" />
            <h3 className="text-lg font-bold">Exportation de Données Ouvertes (Open Science FAIR)</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-white/20 text-slate-300 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Format Selection */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase mb-2">
              1. Choisir le format d'exportation standardisé
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setFormat("csv")}
                className={`p-3 rounded-xl border flex flex-col items-center text-center transition-all ${
                  format === "csv"
                    ? "border-savanna-600 bg-savanna-50 text-savanna-900 ring-2 ring-savanna-500/20"
                    : "border-slate-200 hover:border-slate-300 text-slate-600"
                }`}
              >
                <FileSpreadsheet className="w-6 h-6 mb-1 text-emerald-600" />
                <span className="text-xs font-bold">Format CSV</span>
                <span className="text-[10px] text-slate-500">Pour R, Python & Pandas</span>
              </button>

              <button
                type="button"
                onClick={() => setFormat("json")}
                className={`p-3 rounded-xl border flex flex-col items-center text-center transition-all ${
                  format === "json"
                    ? "border-savanna-600 bg-savanna-50 text-savanna-900 ring-2 ring-savanna-500/20"
                    : "border-slate-200 hover:border-slate-300 text-slate-600"
                }`}
              >
                <FileCode className="w-6 h-6 mb-1 text-blue-600" />
                <span className="text-xs font-bold">Format JSON</span>
                <span className="text-[10px] text-slate-500">Standard ETS v1.0 structuré</span>
              </button>

              <button
                type="button"
                onClick={() => setFormat("dwca")}
                className={`p-3 rounded-xl border flex flex-col items-center text-center transition-all ${
                  format === "dwca"
                    ? "border-savanna-600 bg-savanna-50 text-savanna-900 ring-2 ring-savanna-500/20"
                    : "border-slate-200 hover:border-slate-300 text-slate-600"
                }`}
              >
                <Archive className="w-6 h-6 mb-1 text-amber-600" />
                <span className="text-xs font-bold">Darwin Core (DwC-A)</span>
                <span className="text-[10px] text-slate-500">Archive ZIP pour GBIF</span>
              </button>
            </div>
          </div>

          {/* Filtering options */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Filtre par Espèce</label>
              <input
                type="text"
                placeholder="Ex: Balanites..."
                value={speciesFilter}
                onChange={(e) => setSpeciesFilter(e.target.value)}
                className="w-full text-xs px-3 py-2 border rounded-lg focus:ring-1 focus:ring-savanna-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Zone bioclimatique</label>
              <select
                value={zoneFilter}
                onChange={(e) => setZoneFilter(e.target.value)}
                className="w-full text-xs px-3 py-2 border rounded-lg focus:ring-1 focus:ring-savanna-500 outline-none"
              >
                <option value="">Toutes les zones</option>
                <option value="Sahélienne">Sahélienne</option>
                <option value="Soudano-Sahélienne">Soudano-Sahélienne</option>
                <option value="Soudanienne">Soudanienne</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Contrôle Qualité (QC)</label>
              <select
                value={qcFilter}
                onChange={(e) => setQcFilter(e.target.value)}
                className="w-full text-xs px-3 py-2 border rounded-lg focus:ring-1 focus:ring-savanna-500 outline-none"
              >
                <option value="VALID">Données Validées (QC VALID)</option>
                <option value="">Toutes les mesures (brutes)</option>
              </select>
            </div>
          </div>

          {/* Citation Generator */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <BookMarked className="w-4 h-4 text-savanna-700" />
                Citation bibliographique générée (APA 7th) :
              </span>
              <button
                onClick={() => handleCopyCitation(citationAPA)}
                className="inline-flex items-center gap-1 text-[11px] text-savanna-800 hover:text-savanna-950 font-semibold"
              >
                {copiedCitation ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                {copiedCitation ? "Copié !" : "Copier"}
              </button>
            </div>
            <p className="text-[11px] text-slate-600 italic bg-white p-2.5 rounded border border-slate-200 leading-relaxed font-serif">
              {citationAPA}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-semibold"
          >
            Annuler
          </button>
          <button
            onClick={handleTriggerDownload}
            className="inline-flex items-center gap-1.5 px-5 py-2 bg-savanna-700 hover:bg-savanna-800 text-white rounded-lg text-xs font-bold shadow transition-colors"
          >
            <Download className="w-4 h-4" />
            Télécharger le Jeu de Données ({format.toUpperCase()})
          </button>
        </div>
      </div>
    </div>
  );
};
