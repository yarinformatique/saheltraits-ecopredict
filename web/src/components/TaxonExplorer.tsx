"use client";

import React, { useState, useMemo } from "react";
import { SPECIES_CATALOG, FAMILIES_LIST, FUNCTIONAL_GROUPS, SpeciesInfo } from "@/data/speciesData";
import { SpeciesModal } from "./SpeciesModal";
import { ExportModal } from "./ExportModal";
import {
  Search,
  Filter,
  Grid,
  Table as TableIcon,
  Download,
  Info,
  ExternalLink,
  Droplets,
  Flame,
  Sprout,
  ArrowUpDown,
} from "lucide-react";

export const TaxonExplorer: React.FC = () => {
  const [search, setSearch] = useState("");
  const [selectedFamily, setSelectedFamily] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");
  const [selectedIucn, setSelectedIucn] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [activeSpecies, setActiveSpecies] = useState<SpeciesInfo | null>(null);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportSpeciesName, setExportSpeciesName] = useState<string | undefined>(undefined);

  const filteredSpecies = useMemo(() => {
    return SPECIES_CATALOG.filter((s) => {
      const matchSearch =
        !search ||
        s.scientific_name.toLowerCase().includes(search.toLowerCase()) ||
        s.vernacular_moore.toLowerCase().includes(search.toLowerCase()) ||
        s.vernacular_dioula.toLowerCase().includes(search.toLowerCase()) ||
        s.vernacular_fulfulde.toLowerCase().includes(search.toLowerCase()) ||
        s.family.toLowerCase().includes(search.toLowerCase());

      const matchFamily = !selectedFamily || s.family === selectedFamily;
      const matchGroup = !selectedGroup || s.functional_group === selectedGroup;
      const matchIucn = !selectedIucn || s.iucn_status === selectedIucn;

      return matchSearch && matchFamily && matchGroup && matchIucn;
    });
  }, [search, selectedFamily, selectedGroup, selectedIucn]);

  const handleOpenExport = (spName?: string) => {
    setExportSpeciesName(spName);
    setExportModalOpen(true);
  };

  const iucnColorMap = {
    LC: "bg-emerald-100 text-emerald-800 border-emerald-300",
    VU: "bg-amber-100 text-amber-800 border-amber-300",
    EN: "bg-red-100 text-red-800 border-red-300",
    CR: "bg-purple-100 text-purple-800 border-purple-300",
    NT: "bg-blue-100 text-blue-800 border-blue-300",
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Controls */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 mb-1">
              <Sprout className="w-3.5 h-3.5" />
              Couche 4b • Catalogue Ouvert des Traits Multi-Organes
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              Explorateur Botanique & Profils Fonctionnels (ETS v1.0)
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              28 espèces ligneuses sahéliennes emblématiques du Burkina Faso échantillonnées sur le gradient Dori–Kaya–Pô.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleOpenExport()}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-savanna-700 hover:bg-savanna-800 text-white rounded-xl text-xs font-bold shadow-sm transition-all"
            >
              <Download className="w-4 h-4" />
              Télécharger Jeu Complet (DwC-A / CSV)
            </button>
            <div className="flex border rounded-lg p-0.5 bg-slate-100 text-slate-600">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-1.5 rounded ${viewMode === "grid" ? "bg-white text-slate-900 shadow-sm" : "hover:text-slate-900"}`}
                title="Vue en Cartes"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded ${viewMode === "table" ? "bg-white text-slate-900 shadow-sm" : "hover:text-slate-900"}`}
                title="Vue en Tableau"
              >
                <TableIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Multi-criteria filter bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Recherche (ex: Balanites, Kieglga, Baobab)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border rounded-xl focus:bg-white focus:ring-2 focus:ring-savanna-500 outline-none"
            />
          </div>

          <select
            value={selectedFamily}
            onChange={(e) => setSelectedFamily(e.target.value)}
            className="text-xs px-3 py-2 bg-slate-50 border rounded-xl focus:bg-white focus:ring-2 focus:ring-savanna-500 outline-none"
          >
            <option value="">Toutes les familles ({FAMILIES_LIST.length})</option>
            {FAMILIES_LIST.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>

          <select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            className="text-xs px-3 py-2 bg-slate-50 border rounded-xl focus:bg-white focus:ring-2 focus:ring-savanna-500 outline-none"
          >
            <option value="">Tous les groupes fonctionnels</option>
            {FUNCTIONAL_GROUPS.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>

          <select
            value={selectedIucn}
            onChange={(e) => setSelectedIucn(e.target.value)}
            className="text-xs px-3 py-2 bg-slate-50 border rounded-xl focus:bg-white focus:ring-2 focus:ring-savanna-500 outline-none"
          >
            <option value="">Tous les statuts UICN</option>
            <option value="LC">Préoccupation mineure (LC)</option>
            <option value="VU">Vulnérable (VU)</option>
            <option value="EN">En danger (EN)</option>
          </select>
        </div>

        <div className="text-xs text-slate-400 mt-2">
          {filteredSpecies.length} espèce(s) trouvée(s) sur 28 répertoriées.
        </div>
      </div>

      {/* Grid View */}
      {viewMode === "grid" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredSpecies.map((sp) => (
            <div
              key={sp.id}
              onClick={() => setActiveSpecies(sp)}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-savanna-400 transition-all cursor-pointer flex flex-col overflow-hidden group"
            >
              {/* Photo & Badge */}
              <div className="relative h-44 w-full bg-slate-100 overflow-hidden">
                <img
                  src={sp.photo_url}
                  alt={sp.scientific_name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />
                <div className="absolute top-3 left-3 flex gap-1.5">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-900/80 text-white backdrop-blur-sm">
                    {sp.family}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full border backdrop-blur-sm ${
                      iucnColorMap[sp.iucn_status] || "bg-slate-200"
                    }`}
                  >
                    UICN : {sp.iucn_status}
                  </span>
                </div>

                <div className="absolute bottom-2.5 left-3 right-3 text-white">
                  <h3 className="font-bold text-base italic leading-tight drop-shadow-sm">
                    {sp.scientific_name}
                  </h3>
                  <div className="text-[11px] text-sahel-200 drop-shadow-sm flex gap-2 mt-0.5">
                    {sp.vernacular_moore && <span>Mooré: <strong>{sp.vernacular_moore}</strong></span>}
                    {sp.vernacular_dioula && <span>• Dioula: <strong>{sp.vernacular_dioula}</strong></span>}
                  </div>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                  {sp.description}
                </p>

                {/* Key Traits Badges */}
                <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2 border-t border-slate-100">
                  <div className="bg-slate-50 p-1.5 rounded-lg border">
                    <span className="text-[10px] text-slate-400 block">SLA (mm²/mg)</span>
                    <strong className="text-slate-800 font-bold">{sp.traits.sla_mm2mg}</strong>
                  </div>
                  <div className="bg-slate-50 p-1.5 rounded-lg border">
                    <span className="text-[10px] text-slate-400 block">Bois (g/cm³)</span>
                    <strong className="text-slate-800 font-bold">{sp.traits.wood_density_gcm3}</strong>
                  </div>
                  <div className="bg-slate-50 p-1.5 rounded-lg border">
                    <span className="text-[10px] text-slate-400 block">P50 (MPa)</span>
                    <strong className="text-slate-800 font-bold">{sp.traits.p50_hydraulic_mpa}</strong>
                  </div>
                </div>

                {/* Card Action bar */}
                <div className="flex items-center justify-between pt-2 text-xs font-semibold text-savanna-700 group-hover:text-savanna-900">
                  <span>Explorer profil radar & SDM &rarr;</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                    ETS v1.0
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Table View */}
      {viewMode === "table" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 uppercase border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Espèce (Nom Scientifique)</th>
                  <th className="py-3 px-4">Famille</th>
                  <th className="py-3 px-4">Noms Vernaculaires</th>
                  <th className="py-3 px-4">UICN</th>
                  <th className="py-3 px-4 text-right">SLA (mm²/mg)</th>
                  <th className="py-3 px-4 text-right">LDMC (mg/g)</th>
                  <th className="py-3 px-4 text-right">Bois (g/cm³)</th>
                  <th className="py-3 px-4 text-right">P50 (MPa)</th>
                  <th className="py-3 px-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredSpecies.map((sp) => (
                  <tr
                    key={sp.id}
                    onClick={() => setActiveSpecies(sp)}
                    className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-bold italic text-slate-900">
                      {sp.scientific_name}
                    </td>
                    <td className="py-3 px-4 text-slate-600">{sp.family}</td>
                    <td className="py-3 px-4 text-slate-500">
                      {sp.vernacular_moore || "—"} / {sp.vernacular_dioula || "—"}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          iucnColorMap[sp.iucn_status] || "bg-slate-100"
                        }`}
                      >
                        {sp.iucn_status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-medium">{sp.traits.sla_mm2mg}</td>
                    <td className="py-3 px-4 text-right font-medium">{sp.traits.ldmc_mgg}</td>
                    <td className="py-3 px-4 text-right font-medium">{sp.traits.wood_density_gcm3}</td>
                    <td className="py-3 px-4 text-right font-medium">{sp.traits.p50_hydraulic_mpa}</td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveSpecies(sp);
                        }}
                        className="text-xs px-2.5 py-1 bg-slate-100 hover:bg-savanna-700 hover:text-white rounded-md transition-colors"
                      >
                        Fiche
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals */}
      <SpeciesModal
        species={activeSpecies}
        onClose={() => setActiveSpecies(null)}
        onOpenExport={(spName) => handleOpenExport(spName)}
      />

      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        defaultSpecies={exportSpeciesName}
      />
    </div>
  );
};
