"use client";

import React, { useState } from "react";
import { SpeciesInfo } from "@/data/speciesData";
import { RadarChart } from "./RadarChart";
import {
  X,
  ExternalLink,
  Download,
  ShieldAlert,
  Sprout,
  Droplets,
  Flame,
  BookOpen,
  Calendar,
  Layers,
  Sparkles,
} from "lucide-react";

interface SpeciesModalProps {
  species: SpeciesInfo | null;
  onClose: () => void;
  onOpenExport: (spName: string) => void;
}

export const SpeciesModal: React.FC<SpeciesModalProps> = ({
  species,
  onClose,
  onOpenExport,
}) => {
  const [activeTab, setActiveTab] = useState<"traits" | "germination" | "climate" | "ethno">("traits");

  if (!species) return null;

  // Normalized values for radar
  const radarData = {
    sla: Math.min(100, (species.traits.sla_mm2mg / 20) * 100),
    ldmc: Math.min(100, (species.traits.ldmc_mgg / 500) * 100),
    wood_density: Math.min(100, (species.traits.wood_density_gcm3 / 0.85) * 100),
    cavitation: Math.min(100, (Math.abs(species.traits.p50_hydraulic_mpa) / 6.0) * 100),
    seed_mass: Math.min(100, (Math.log10(species.traits.seed_mass_mg) / 4) * 100),
    drought: species.traits.drought_index,
    fire: species.traits.fire_resistance,
    germination_peg: species.germination.gp_peg_pct,
  };

  const iucnColorMap = {
    LC: "bg-emerald-100 text-emerald-800 border-emerald-300",
    VU: "bg-amber-100 text-amber-800 border-amber-300",
    EN: "bg-red-100 text-red-800 border-red-300",
    CR: "bg-purple-100 text-purple-800 border-purple-300",
    NT: "bg-blue-100 text-blue-800 border-blue-300",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="relative px-6 py-4 bg-gradient-to-r from-savanna-900 to-slate-900 text-white flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs uppercase tracking-wider font-semibold text-sahel-300">
                {species.family} • {species.genus}
              </span>
              <span
                className={`text-[11px] px-2 py-0.5 rounded-full font-bold border ${
                  iucnColorMap[species.iucn_status] || "bg-slate-200 text-slate-800"
                }`}
              >
                UICN : {species.iucn_status}
              </span>
            </div>
            <h2 className="text-2xl font-bold italic tracking-tight">{species.scientific_name}</h2>
            <div className="flex flex-wrap gap-3 text-xs text-slate-300 mt-1">
              <span>Mooré: <strong className="text-sahel-200">{species.vernacular_moore || "—"}</strong></span>
              <span>Dioula: <strong className="text-sahel-200">{species.vernacular_dioula || "—"}</strong></span>
              <span>Fulfuldé: <strong className="text-sahel-200">{species.vernacular_fulfulde || "—"}</strong></span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/20 text-slate-300 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 px-6 bg-slate-50 text-sm font-medium">
          <button
            onClick={() => setActiveTab("traits")}
            className={`py-3 px-4 border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === "traits"
                ? "border-savanna-600 text-savanna-800 font-bold"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <Layers className="w-4 h-4" />
            Traits Multi-Organes & Radar
          </button>
          <button
            onClick={() => setActiveTab("climate")}
            className={`py-3 px-4 border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === "climate"
                ? "border-savanna-600 text-savanna-800 font-bold"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            Vulnérabilité EcoPredict 2050–2080
          </button>
          <button
            onClick={() => setActiveTab("germination")}
            className={`py-3 px-4 border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === "germination"
                ? "border-savanna-600 text-savanna-800 font-bold"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <Sprout className="w-4 h-4" />
            Régénération & Germination
          </button>
          <button
            onClick={() => setActiveTab("ethno")}
            className={`py-3 px-4 border-b-2 flex items-center gap-2 transition-colors ${
              activeTab === "ethno"
                ? "border-savanna-600 text-savanna-800 font-bold"
                : "border-transparent text-slate-600 hover:text-slate-900"
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Savoirs & Usages Locaux
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {activeTab === "traits" && (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
              {/* Radar Column */}
              <div className="md:col-span-5 flex flex-col items-center">
                <RadarChart data={radarData} size={300} speciesName={species.scientific_name} />
                <div className="mt-3 text-xs text-slate-500 text-center">
                  Aligné sur le standard <strong>ETS v1.0</strong> (Ecological Trait-data Standard).
                </div>
              </div>

              {/* Traits Values Table & Metrics */}
              <div className="md:col-span-7 space-y-4">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                    Groupe Fonctionnel & Rôle Écologique
                  </div>
                  <div className="text-sm font-bold text-savanna-900 mt-0.5">
                    {species.functional_group}
                  </div>
                  <p className="text-xs text-slate-600 mt-1">{species.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg">
                    <span className="text-slate-500 font-medium">SLA (Surface Foliaire Spéc.)</span>
                    <div className="text-lg font-bold text-emerald-900">
                      {species.traits.sla_mm2mg} <span className="text-xs font-normal">mm²/mg</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Cornelissen et al. (600 dpi)</span>
                  </div>

                  <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg">
                    <span className="text-slate-500 font-medium">LDMC (Matière Sèche)</span>
                    <div className="text-lg font-bold text-emerald-900">
                      {species.traits.ldmc_mgg} <span className="text-xs font-normal">mg/g</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Poids sec après 72h à 60°C</span>
                  </div>

                  <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg">
                    <span className="text-slate-500 font-medium">Densité Bois (Wood Density)</span>
                    <div className="text-lg font-bold text-amber-900">
                      {species.traits.wood_density_gcm3} <span className="text-xs font-normal">g/cm³</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Déplacement eau (Archimède)</span>
                  </div>

                  <div className="p-3 bg-cyan-50/70 border border-cyan-200 rounded-lg">
                    <span className="text-slate-500 font-medium">Marge Hydraulique (P50)</span>
                    <div className="text-lg font-bold text-cyan-900">
                      {species.traits.p50_hydraulic_mpa} <span className="text-xs font-normal">MPa</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Vulnérabilité cavitation</span>
                  </div>

                  <div className="p-3 bg-purple-50/70 border border-purple-200 rounded-lg">
                    <span className="text-slate-500 font-medium">Masse 100 Graines</span>
                    <div className="text-lg font-bold text-purple-900">
                      {species.traits.seed_mass_mg} <span className="text-xs font-normal">mg</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Écophysiologie de dispersion</span>
                  </div>

                  <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-lg">
                    <span className="text-slate-500 font-medium">Épaisseur Foliaire</span>
                    <div className="text-lg font-bold text-rose-900">
                      {species.traits.leaf_thickness_um} <span className="text-xs font-normal">µm</span>
                    </div>
                    <span className="text-[10px] text-slate-500">Protection cuticulaire</span>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-100 rounded-lg text-xs text-slate-700">
                  <div className="flex items-center gap-2">
                    <Droplets className="w-4 h-4 text-blue-600" />
                    <span>Tolérance Sécheresse : <strong>{species.traits.drought_index}/100</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Flame className="w-4 h-4 text-orange-600" />
                    <span>Résistance Feux : <strong>{species.traits.fire_resistance}/100</strong></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "climate" && (
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <h4 className="text-sm font-bold text-blue-900 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  Projections CMIP6 d'Aptitude Climatique au Burkina Faso
                </h4>
                <p className="text-xs text-blue-800 mt-1">
                  Basées sur l'ensemble de modèles biomod2 (Random Forest, MaxEnt, GLM) et les scénarios du GIEC :
                  SSP2-4.5 (trajectoire intermédiaire) vs SSP5-8.5 (scénario pessimiste à fortes émissions).
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* SSP 2-4.5 */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                  <div className="flex items-center justify-between border-b pb-2">
                    <span className="text-xs font-bold text-slate-700 uppercase">Scénario SSP2-4.5 (Intermédiaire)</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold">+1.8°C à +2.2°C</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-2 bg-white rounded border">
                      <span className="text-slate-500">Horizon 2050</span>
                      <div className="text-sm font-bold text-slate-800">
                        {species.projections.ssp245_2050.change_pct > 0 ? "+" : ""}
                        {species.projections.ssp245_2050.change_pct}% aire
                      </div>
                      <span className="text-[10px] text-emerald-700 font-medium">
                        {species.projections.ssp245_2050.status}
                      </span>
                    </div>
                    <div className="p-2 bg-white rounded border">
                      <span className="text-slate-500">Horizon 2080</span>
                      <div className="text-sm font-bold text-slate-800">
                        {species.projections.ssp245_2080.change_pct > 0 ? "+" : ""}
                        {species.projections.ssp245_2080.change_pct}% aire
                      </div>
                      <span className="text-[10px] text-emerald-700 font-medium">
                        {species.projections.ssp245_2080.status}
                      </span>
                    </div>
                  </div>
                </div>

                {/* SSP 5-8.5 */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                  <div className="flex items-center justify-between border-b pb-2">
                    <span className="text-xs font-bold text-slate-700 uppercase">Scénario SSP5-8.5 (Pessimiste)</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-semibold">+2.4°C à +4.3°C</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-2 bg-white rounded border">
                      <span className="text-slate-500">Horizon 2050</span>
                      <div className="text-sm font-bold text-slate-800">
                        {species.projections.ssp585_2050.change_pct > 0 ? "+" : ""}
                        {species.projections.ssp585_2050.change_pct}% aire
                      </div>
                      <span className="text-[10px] text-amber-700 font-medium">
                        {species.projections.ssp585_2050.status}
                      </span>
                    </div>
                    <div className="p-2 bg-white rounded border">
                      <span className="text-slate-500">Horizon 2080</span>
                      <div className="text-sm font-bold text-slate-800">
                        {species.projections.ssp585_2080.change_pct > 0 ? "+" : ""}
                        {species.projections.ssp585_2080.change_pct}% aire
                      </div>
                      <span className="text-[10px] text-rose-700 font-medium">
                        {species.projections.ssp585_2080.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Recommandation pour la Grande Muraille Verte & les reboisements : </strong>
                  {species.projections.ssp585_2080.vuln_idx > 40
                    ? "Vulnérabilité future sévère. Éviter les monocultures en zone sahélienne septentrionale; réserver aux corridors riverains et micro-refuges humides."
                    : "Espèce hautement résiliente. Recommandée prioritairement pour les programmes de restauration des paysages dégradés et stabilisation dunaire."}
                </div>
              </div>
            </div>
          )}

          {activeTab === "germination" && (
            <div className="space-y-4">
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                <h4 className="text-sm font-bold text-emerald-900 flex items-center gap-2">
                  <Sprout className="w-4 h-4 text-emerald-700" />
                  Écophysiologie de la Germination sous Contraintes Osmo-Thermiques
                </h4>
                <p className="text-xs text-emerald-800 mt-1">
                  Évaluation de la capacité régénérative sous déficit hydrique simulé au Polyéthylène Glycol (PEG 6000) et régimes thermiques sahéliens.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-3 bg-slate-50 border rounded-lg text-center">
                  <span className="text-slate-500">Vitesse de germination (T50)</span>
                  <div className="text-xl font-bold text-slate-800 mt-1">{species.germination.t50_days} jours</div>
                  <span className="text-[10px] text-slate-500">Temps pour 50% de germination</span>
                </div>
                <div className="p-3 bg-slate-50 border rounded-lg text-center">
                  <span className="text-slate-500">Taux Contrôle (0.0 MPa)</span>
                  <div className="text-xl font-bold text-emerald-700 mt-1">{species.germination.gp_ctrl_pct}%</div>
                  <span className="text-[10px] text-slate-500">Eau pure, 30°C/20°C</span>
                </div>
                <div className="p-3 bg-slate-50 border rounded-lg text-center">
                  <span className="text-slate-500">Stress Osmotique (-0.8 MPa)</span>
                  <div className="text-xl font-bold text-amber-700 mt-1">{species.germination.gp_peg_pct}%</div>
                  <span className="text-[10px] text-slate-500">Solution concentrée PEG 6000</span>
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border text-xs text-slate-700">
                <strong>Protocole de prétraitement recommandé pour pépiniéristes : </strong>
                {species.germination.regime}.
              </div>
            </div>
          )}

          {activeTab === "ethno" && (
            <div className="space-y-4">
              <div className="p-4 bg-sahel-50 border border-sahel-200 rounded-xl">
                <h4 className="text-sm font-bold text-sahel-900 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-sahel-700" />
                  Savoirs Écologiques Traditionnels & Ethnobotanique
                </h4>
                <p className="text-xs text-sahel-800 mt-1">
                  Issus des 450 enquêtes de terrain menées auprès des communautés agro-pastorales et herboristes du Burkina Faso.
                </p>
              </div>

              <div className="space-y-3">
                <div className="p-3 bg-white border border-slate-200 rounded-lg">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Usages Majeurs :</span>
                  <ul className="list-disc list-inside text-xs text-slate-700 mt-1 space-y-1">
                    {species.ethnobotany.traditional_uses.map((u, i) => (
                      <li key={i}>{u}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-3 bg-white border border-slate-200 rounded-lg">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Importance Culturelle & Coutumière :</span>
                  <p className="text-xs text-slate-700 mt-1">{species.ethnobotany.cultural_importance}</p>
                </div>

                <div className="p-3 bg-white border border-slate-200 rounded-lg">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Propriétés Médicinales & Pharmacopée :</span>
                  <p className="text-xs text-slate-700 mt-1">{species.ethnobotany.medicinal_properties}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <a
            href={`https://www.gbif.org/species/${species.gbif_usage_key}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-emerald-700 hover:text-emerald-900 hover:underline font-medium"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            Vérifier sur GBIF Backbone Taxonomy (#{species.gbif_usage_key})
          </a>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onOpenExport(species.scientific_name)}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-savanna-700 hover:bg-savanna-800 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
            >
              <Download className="w-4 h-4" />
              Exporter les Données (CSV / JSON / DwC-A)
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
