"use client";

import React, { useState } from "react";
import { SURVEYS_SUMMARY, SURVEY_VILLAGES, SurveyVillageData } from "@/data/surveysData";
import {
  Flame,
  Droplets,
  Users,
  AlertTriangle,
  TrendingDown,
  Calendar,
  MapPin,
  Search,
  Filter,
  BarChart3,
  ShieldCheck,
  CheckCircle,
} from "lucide-react";

export const SurveysDashboard: React.FC = () => {
  const [selectedZone, setSelectedZone] = useState<string>("");
  const [villageSearch, setVillageSearch] = useState<string>("");
  const [selectedVillage, setSelectedVillage] = useState<SurveyVillageData | null>(SURVEY_VILLAGES[0]);

  const filteredVillages = SURVEY_VILLAGES.filter((v) => {
    const matchZone = !selectedZone || v.climatic_zone === selectedZone;
    const matchSearch =
      !villageSearch ||
      v.village_name.toLowerCase().includes(villageSearch.toLowerCase()) ||
      v.most_declining_species.some((s) => s.toLowerCase().includes(villageSearch.toLowerCase())) ||
      v.most_resilient_species.some((s) => s.toLowerCase().includes(villageSearch.toLowerCase()));
    return matchZone && matchSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200 mb-1">
          <Flame className="w-3.5 h-3.5 text-orange-600" />
          Couche 4b • Synthèse Ethno-Écologique & Télédétection MODIS
        </div>
        <h2 className="text-xl font-bold text-slate-900">
          Tableau de Bord des 450 Enquêtes de Terrain & Pressions Environnementales
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Croisement des perceptions locales du dépérissement ligneux avec l'aridité bioclimatique et la récurrence des feux de brousse MODIS (2000–2020).
        </p>

        {/* 4 Top KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
              Enquêtes Réalisées
            </span>
            <div className="text-2xl font-black text-slate-900 mt-1">
              {SURVEYS_SUMMARY.total_surveys}
            </div>
            <span className="text-[11px] text-slate-500">
              45 terroirs • 3 zones climatiques
            </span>
          </div>

          <div className="p-4 bg-rose-50/70 rounded-xl border border-rose-200">
            <span className="text-[11px] font-semibold text-rose-700 uppercase tracking-wider block">
              Perception Dépérissement
            </span>
            <div className="text-2xl font-black text-rose-950 mt-1">
              {SURVEYS_SUMMARY.global_statistics.overall_decline_pct}%
            </div>
            <span className="text-[11px] text-rose-700 font-medium">
              Régression nette constatée (-1 ou -2)
            </span>
          </div>

          <div className="p-4 bg-amber-50/70 rounded-xl border border-amber-200">
            <span className="text-[11px] font-semibold text-amber-700 uppercase tracking-wider block">
              Décalages Phénologiques
            </span>
            <div className="text-2xl font-black text-amber-950 mt-1">
              {SURVEYS_SUMMARY.global_statistics.phenology_shift_reported_pct}%
            </div>
            <span className="text-[11px] text-amber-700 font-medium">
              Floraison décalée ou avortée
            </span>
          </div>

          <div className="p-4 bg-blue-50/70 rounded-xl border border-blue-200">
            <span className="text-[11px] font-semibold text-blue-700 uppercase tracking-wider block">
              Corrélation Aridité / Déclin
            </span>
            <div className="text-2xl font-black text-blue-950 mt-1">
              r = {SURVEYS_SUMMARY.global_statistics.correlation_aridity_decline}
            </div>
            <span className="text-[11px] text-blue-700 font-medium">
              p &lt; 0.001 (Pearson hautement signif.)
            </span>
          </div>
        </div>
      </div>

      {/* Cross-Analysis Sections: MODIS & Aridity Correlations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* MODIS Fire Index Correlation Card */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b">
            <div className="flex items-center gap-2">
              <Flame className="w-5 h-5 text-orange-600" />
              <h3 className="text-sm font-bold text-slate-800">
                Pression Feux MODIS vs Dépérissement Perçu
              </h3>
            </div>
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-orange-100 text-orange-800">
              r = +0.68
            </span>
          </div>

          <p className="text-xs text-slate-600">
            Les données satellitaires MODIS (MCD64A1, fréquence cumulée 2000–2020) mettent en évidence que la récurrence des feux tardifs amplifie la mortalité des jeunes recrues ligneuses dans les zones soudaniennes (Pô, Léo, Bobo, Gaoua).
          </p>

          {/* Simulated Scatter Plot / Bar Visualization */}
          <div className="space-y-2 pt-2">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">
              Score moyen de feux par zone bioclimatique (20 ans) :
            </div>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1 font-medium text-slate-700">
                  <span>Zone Soudanienne (Pô, Bobo, Gaoua)</span>
                  <strong className="text-orange-700">14.2 feux / 20 ans</strong>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-orange-500 h-full rounded-full" style={{ width: "85%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 font-medium text-slate-700">
                  <span>Zone Soudano-Sahélienne (Kaya, Ouaga, Fada)</span>
                  <strong className="text-amber-700">5.6 feux / 20 ans</strong>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: "38%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 font-medium text-slate-700">
                  <span>Zone Sahélienne (Dori, Oursi, Tin-Akoff)</span>
                  <strong className="text-emerald-700">1.6 feux / 20 ans (paucité biomasse)</strong>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: "12%" }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Aridity Index Correlation Card */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b">
            <div className="flex items-center gap-2">
              <Droplets className="w-5 h-5 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-800">
                Indice d'Aridité (P/PET) vs Mortalité Ligneuse
              </h3>
            </div>
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
              r = -0.74
            </span>
          </div>

          <p className="text-xs text-slate-600">
            L'indice d'aridité globale UNEP (Précipitations / Évapotranspiration potentielle) révèle que la bande sahélienne septentrionale (&lt; 0.20) subit un dépérissement critique des espèces non-xérophytes (Pterocarpus, Adansonia, Khaya).
          </p>

          <div className="space-y-2 pt-2">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">
              Distribution des Usages Traditionnels Principaux (PFNL) :
            </div>
            <div className="space-y-2 text-xs">
              {SURVEYS_SUMMARY.top_traditional_uses.map((use, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-[11px] mb-1 font-medium text-slate-700">
                    <span>{use.label}</span>
                    <strong className="text-slate-900">{use.pct}% ({use.count}/450)</strong>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div className="bg-savanna-600 h-full rounded-full" style={{ width: `${use.pct}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Villages Explorer Table & Detail Modal */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Données de Terrain par Terroir & Localité Enquêtée
            </h3>
            <span className="text-xs text-slate-500">
              {filteredVillages.length} localités affichées (10 enquêtes approfondies par village)
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-2.5 top-2 text-slate-400" />
              <input
                type="text"
                placeholder="Chercher localité ou espèce..."
                value={villageSearch}
                onChange={(e) => setVillageSearch(e.target.value)}
                className="text-xs pl-8 pr-3 py-1.5 bg-slate-50 border rounded-lg outline-none focus:bg-white"
              />
            </div>

            <select
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
              className="text-xs px-2.5 py-1.5 bg-slate-50 border rounded-lg outline-none"
            >
              <option value="">Toutes les zones</option>
              <option value="Sahélienne">Sahélienne</option>
              <option value="Soudano-Sahélienne">Soudano-Sahélienne</option>
              <option value="Soudanienne">Soudanienne</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Localité / Terroir</th>
                <th className="py-2.5 px-3">Zone Bioclimatique</th>
                <th className="py-2.5 px-3 text-center">Indice Aridité (P/PET)</th>
                <th className="py-2.5 px-3 text-center">Feux MODIS (20 ans)</th>
                <th className="py-2.5 px-3 text-center">Score Déclin (-2 à +2)</th>
                <th className="py-2.5 px-3 text-center">Décalage Phénologique</th>
                <th className="py-2.5 px-3">Espèces Résilientes Constatées</th>
                <th className="py-2.5 px-3">Espèces les Plus Vulnérables</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredVillages.map((v, i) => (
                <tr
                  key={i}
                  onClick={() => setSelectedVillage(v)}
                  className={`cursor-pointer transition-colors ${
                    selectedVillage?.village_name === v.village_name
                      ? "bg-emerald-50/70"
                      : "hover:bg-slate-50"
                  }`}
                >
                  <td className="py-2.5 px-3 font-bold text-slate-900 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-rose-500" />
                    {v.village_name}
                  </td>
                  <td className="py-2.5 px-3 text-slate-600">{v.climatic_zone}</td>
                  <td className="py-2.5 px-3 text-center font-mono font-medium">{v.aridity_index}</td>
                  <td className="py-2.5 px-3 text-center font-medium">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] ${
                        v.fire_index_modis > 10
                          ? "bg-rose-100 text-rose-800 font-bold"
                          : v.fire_index_modis > 4
                          ? "bg-amber-100 text-amber-800"
                          : "bg-emerald-100 text-emerald-800"
                      }`}
                    >
                      {v.fire_index_modis}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center font-bold text-rose-700">
                    {v.mean_decline_score}
                  </td>
                  <td className="py-2.5 px-3 text-center font-semibold text-amber-700">
                    {v.phenology_shift_pct}%
                  </td>
                  <td className="py-2.5 px-3 text-emerald-800 font-medium">
                    {v.most_resilient_species.join(", ")}
                  </td>
                  <td className="py-2.5 px-3 text-rose-800 font-medium">
                    {v.most_declining_species.join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
