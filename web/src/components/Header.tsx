"use client";

import React from "react";
import {
  Compass,
  Sprout,
  BarChart3,
  BookOpen,
  Download,
  ExternalLink,
  ShieldCheck,
  TreeDeciduous,
} from "lucide-react";

interface HeaderProps {
  activeTab: "explorer" | "simulator" | "surveys" | "manual";
  onTabChange: (tab: "explorer" | "simulator" | "surveys" | "manual") => void;
  onOpenExport: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onTabChange,
  onOpenExport,
}) => {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Branding Bar */}
        <div className="flex items-center justify-between py-3 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-savanna-600 to-emerald-800 flex items-center justify-center shadow-md border border-savanna-400/30">
              <TreeDeciduous className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-tight text-white">
                  SAHELTRAITS-DB <span className="text-sahel-400 font-light">&</span> ECOPREDICT
                </h1>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
                  Couche 4b • v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Portail Web d'Aide à la Décision • Thèse Doctorat : <strong>YAGO Abdoul Rachide</strong> (UJKZ-ICC)
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-3">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
            >
              <ExternalLink className="w-3.5 h-3.5 text-sahel-300" />
              API REST & Swagger (Couche 3)
            </a>

            <button
              onClick={onOpenExport}
              className="inline-flex items-center gap-1.5 text-xs font-bold bg-savanna-600 hover:bg-savanna-700 text-white px-3.5 py-1.5 rounded-lg shadow-sm transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              Export FAIR (DwC-A)
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-4 pt-1 overflow-x-auto text-xs font-medium">
          <button
            onClick={() => onTabChange("explorer")}
            className={`py-3 px-3 border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === "explorer"
                ? "border-savanna-500 text-savanna-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sprout className="w-4 h-4" />
            1. Explorateur Taxons & Traits (ETS v1.0)
          </button>

          <button
            onClick={() => onTabChange("simulator")}
            className={`py-3 px-3 border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === "simulator"
                ? "border-savanna-500 text-savanna-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Compass className="w-4 h-4" />
            2. Simulateur Cartographique « EcoPredict 2050–2080 »
          </button>

          <button
            onClick={() => onTabChange("surveys")}
            className={`py-3 px-3 border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === "surveys"
                ? "border-savanna-500 text-savanna-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            3. Tableau de Bord des 450 Enquêtes & Feux MODIS
          </button>

          <button
            onClick={() => onTabChange("manual")}
            className={`py-3 px-3 border-b-2 flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === "manual"
                ? "border-savanna-500 text-savanna-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="w-4 h-4" />
            4. Manuel d'Utilisation Illustré (MEEA / ONG)
          </button>
        </nav>
      </div>
    </header>
  );
};
