"use client";

import React from "react";
import {
  BookOpen,
  FileText,
  MapPin,
  Sprout,
  Compass,
  Download,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Printer,
  Sparkles,
} from "lucide-react";

export const UserManual: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Banner */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 mb-1">
              <BookOpen className="w-3.5 h-3.5" />
              Livrable Contractuel Couche 4b • Thèse Doctorale
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              Manuel d'Utilisation Illustré : Portail SahelTraits-DB & EcoPredict
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Guide opérationnel destiné aux cadres techniques des ministères (MEEA, MESRI), de l'Agence Nationale de la Grande Muraille Verte et des ONG de reboisement.
            </p>
          </div>

          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-bold shadow-sm transition-all"
          >
            <Printer className="w-4 h-4" />
            Imprimer / Exporter PDF
          </button>
        </div>

        {/* Metadata Card */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-4 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Maître d'Ouvrage</span>
            <strong className="text-slate-800">YAGO Abdoul Rachide</strong>
            <span className="text-[11px] text-slate-500 block">Doctorat Écologie Fonctionnelle & Bio-info</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Institutions Partenaires</span>
            <strong className="text-slate-800">UJKZ-ICC • MEEA • MESRI</strong>
            <span className="text-[11px] text-slate-500 block">Université Joseph Ki-Zerbo (Ouagadougou)</span>
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border">
            <span className="text-slate-400 block text-[10px] uppercase font-bold">Standards Internationaux</span>
            <strong className="text-slate-800">FAIR • ETS v1.0 • DwC-A</strong>
            <span className="text-[11px] text-slate-500 block">GBIF Backbone & PostGIS SRID 4326</span>
          </div>
        </div>
      </div>

      {/* Chapter 1: Architecture */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-savanna-100 text-savanna-800 text-xs flex items-center justify-center font-bold">
            1
          </span>
          Architecture Globale du Système & Couplage Multi-Échelles
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Le projet de thèse s'articule en 4 couches coordonnées assurant la traçabilité intégrale de la semence à la politique publique :
        </p>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <strong className="text-slate-900 block font-bold">Couche 1 : Vision Foliaire</strong>
            <span className="text-[11px] text-slate-500">Phénotypage numérique haute résolution des feuilles et calibration automatique.</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <strong className="text-slate-900 block font-bold">Couche 2 : Collecte Mobile</strong>
            <span className="text-[11px] text-slate-500">Application PWA déconnectée avec balisage QR-code des arbres et synchronisation batch.</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <strong className="text-slate-900 block font-bold">Couche 3 : Entrepôt REST</strong>
            <span className="text-[11px] text-slate-500">API FastAPI / SQLite / PostgreSQL PostGIS avec contrôle qualité 3-sigma (QC).</span>
          </div>
          <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
            <strong className="text-emerald-950 block font-bold">Couche 4 : Pipeline & Web</strong>
            <span className="text-[11px] text-emerald-800">Modèles SDM CMIP6 et portail web interactif d'aide à la décision (ce tableau de bord).</span>
          </div>
        </div>
      </div>

      {/* Chapter 2: Taxon Explorer & FAIR Export */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-savanna-100 text-savanna-800 text-xs flex items-center justify-center font-bold">
            2
          </span>
          Guide Pratique : Exploration Taxonomique & Exportation FAIR
        </h3>
        <div className="space-y-3 text-xs text-slate-700 leading-relaxed">
          <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
            <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-xs flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
              a
            </span>
            <div>
              <strong>Recherche Multicritères :</strong> Vous pouvez rechercher une espèce par son nom scientifique (ex: <em>Balanites aegyptiaca</em>) ou ses noms en dialectes locaux (<em>Kieglga</em> en Mooré, <em>Ségéné</em> en Dioula, <em>Murtooki</em> en Fulfuldé).
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
            <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-xs flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
              b
            </span>
            <div>
              <strong>Profil Radar Multi-Organes :</strong> Cliquez sur n'importe quelle carte pour ouvrir la fiche détaillée. Le graphique radar présente simultanément les traits foliaires (SLA, LDMC), anatomiques (densité du bois), hydrauliques (P50 cavitation) et séminaux (masse des graines, germination sous PEG).
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
            <span className="w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-xs flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
              c
            </span>
            <div>
              <strong>Exportation FAIR & Citation Universitaire :</strong> Cliquez sur « Exporter les Données » pour générer instantanément un fichier CSV, JSON (ETS v1.0) ou une archive Darwin Core (DwC-A). La citation bibliographique officielle (norme APA 7th et BibTeX) est générée automatiquement pour vos rapports et publications.
            </div>
          </div>
        </div>
      </div>

      {/* Chapter 3: Simulator & Diagnostic Tool */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-savanna-100 text-savanna-800 text-xs flex items-center justify-center font-bold">
            3
          </span>
          Guide Pratique : Simulateur « EcoPredict » & Outil Diagnostic
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          L'outil diagnostic permet aux gestionnaires des Eaux et Forêts et ONG de valider la faisabilité d'un reboisement avant investissement :
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 bg-emerald-50/70 border border-emerald-200 rounded-xl space-y-1.5">
            <div className="font-bold text-emerald-900 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              Espèces Recommandées (&gt; 75%)
            </div>
            <p className="text-[11px] text-emerald-800">
              Essences dont les traits fonctionnels (bois lourd, faible SLA, marge hydraulique P50 protectrice) garantissent un taux de survie maximal sous le climat futur.
            </p>
          </div>

          <div className="p-3.5 bg-amber-50/70 border border-amber-200 rounded-xl space-y-1.5">
            <div className="font-bold text-amber-900 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-amber-600" />
              Espèces Sous Surveillance (50–74%)
            </div>
            <p className="text-[11px] text-amber-800">
              Tolérantes mais nécessitant un paillage initial, des demi-lunes hydriques ou un suivi des premières années de plantation.
            </p>
          </div>

          <div className="p-3.5 bg-rose-50/70 border border-rose-200 rounded-xl space-y-1.5">
            <div className="font-bold text-rose-900 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              Espèces à Haut Risque (&lt; 50%)
            </div>
            <p className="text-[11px] text-rose-800">
              Fort risque d'échec ou de mortalité massive sous le scénario SSP5-8.5. À proscrire en plein découvert, réserver aux bas-fonds humides protégés.
            </p>
          </div>
        </div>

        <div className="p-3.5 bg-slate-50 border rounded-xl text-xs text-slate-700">
          <strong>Mode d'emploi diagnostic par polygone :</strong> Vous pouvez coller les coordonnées GPS d'une parcelle (format GeoJSON ou liste de sommets [lon, lat]) pour calculer le centroïde de la zone et agréger instantanément le diagnostic climatique.
        </div>
      </div>

      {/* Chapter 4: Surveys & Field Pressures */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-savanna-100 text-savanna-800 text-xs flex items-center justify-center font-bold">
            4
          </span>
          Interprétation des Données Ethno-écologiques & Feux MODIS
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Le module des enquêtes (450 questionnaires administrés dans 45 villages) apporte la validation empirique locale aux projections climatiques théoriques :
        </p>
        <ul className="list-disc list-inside text-xs text-slate-700 space-y-1.5 pl-2">
          <li>
            <strong>Concordance Forte :</strong> Les espèces identifiées comme vulnérables par les modèles biomod2 (ex: <em>Pterocarpus erinaceus</em>, <em>Khaya senegalensis</em>) sont exactement celles dont les agropasteurs constatent la forte régression (-1.5 à -1.8).
          </li>
          <li>
            <strong>Impact des Feux :</strong> Dans le sud (zone soudanienne), les feux tardifs constituent la première cause d'échec des régénérations naturelles assistées (RNA), tandis que dans le nord sahélien, c'est l'abaissement des nappes phréatiques qui domine.
          </li>
          <li>
            <strong>Valorisation des PFNL :</strong> La préservation des espèces fruitières (<em>Parkia</em>, <em>Vitellaria</em>, <em>Ziziphus</em>, <em>Balanites</em>) constitue le levier le plus puissant d'adhésion des populations locales aux projets de restauration.
          </li>
        </ul>
      </div>
    </div>
  );
};
