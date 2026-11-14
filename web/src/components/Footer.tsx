"use client";

import React from "react";
import { TreeDeciduous, Heart, ShieldCheck, Globe, BookOpen } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-950 text-slate-400 text-xs border-t border-slate-800 mt-16 py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-white font-bold text-sm">
              <TreeDeciduous className="w-5 h-5 text-emerald-500" />
              <span>SahelTraits-DB & EcoPredict</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Système intégré d'aide à la décision pour la résilience climatique de la flore ligneuse sahélienne et la restauration écologique des terres dégradées.
            </p>
          </div>

          <div>
            <span className="text-white font-bold block mb-2 text-xs uppercase tracking-wide">
              Cadre Institutionnel
            </span>
            <ul className="space-y-1 text-[11px] text-slate-400">
              <li>Université Joseph Ki-Zerbo (UJKZ - Ouagadougou)</li>
              <li>École Doctorale Sciences & Technologies / ICC</li>
              <li>MEEA (Ministère Environnement, Eau, Assainissement)</li>
              <li>MESRI (Recherche Scientifique & Innovation)</li>
            </ul>
          </div>

          <div>
            <span className="text-white font-bold block mb-2 text-xs uppercase tracking-wide">
              Standards & Open Data
            </span>
            <ul className="space-y-1 text-[11px] text-slate-400">
              <li>Standards FAIR & Creative Commons CC-BY 4.0</li>
              <li>ETS v1.0 (Ecological Trait-data Standard)</li>
              <li>Darwin Core Archive (DwC-A) pour le GBIF</li>
              <li>Projections CMIP6 & OGC GeoTIFF / PostGIS</li>
            </ul>
          </div>

          <div>
            <span className="text-white font-bold block mb-2 text-xs uppercase tracking-wide">
              Maître d'Ouvrage
            </span>
            <p className="text-[11px] text-slate-300">
              <strong>YAGO Abdoul Rachide</strong><br />
              Doctorant en Écologie Fonctionnelle & Bio-informatique (2026–2029)<br />
              Contact : <code className="text-sahel-300">rachide.yago@ujkz.bf</code>
            </p>
          </div>
        </div>

        <div className="border-t border-slate-900 pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 gap-3">
          <span>
            © 2026–2029 SahelTraits-DB & EcoPredict. Tous droits réservés sous licence Open Science.
          </span>
          <div className="flex items-center gap-4">
            <span>Ouagadougou, Burkina Faso</span>
            <span>•</span>
            <span>Grande Muraille Verte</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
