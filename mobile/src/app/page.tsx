'use client';

import React from 'react';
import Link from 'next/link';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import {
  MapPin,
  Trees,
  FlaskConical,
  ClipboardList,
  QrCode,
  RefreshCw,
  Download,
  ShieldCheck,
  CheckCircle2,
  ChevronRight,
  Database,
  Smartphone,
} from 'lucide-react';

export default function HomePage() {
  const plotsCount = useLiveQuery(() => db.plots.count(), [], 0);
  const indCount = useLiveQuery(() => db.individuals.count(), [], 0);
  const traitsCount = useLiveQuery(() => db.traits.count(), [], 0);
  const surveysCount = useLiveQuery(() => db.surveys.count(), [], 0);

  const pendingPlots = useLiveQuery(() => db.plots.where('sync_status').equals('PENDING').count(), [], 0);
  const pendingInds = useLiveQuery(() => db.individuals.where('sync_status').equals('PENDING').count(), [], 0);
  const pendingTraits = useLiveQuery(() => db.traits.where('sync_status').equals('PENDING').count(), [], 0);
  const pendingSurveys = useLiveQuery(() => db.surveys.where('sync_status').equals('PENDING').count(), [], 0);

  const totalPending = (pendingPlots || 0) + (pendingInds || 0) + (pendingTraits || 0) + (pendingSurveys || 0);

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Doctoral Banner */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-savanna-900 to-zinc-900 border border-savanna-700/60 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-6 -mt-6 w-28 h-28 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="flex items-center space-x-2 text-[10px] uppercase font-bold tracking-wider text-sahel-300">
          <Smartphone className="w-3.5 h-3.5" />
          <span>SahelField App — Couche 1 Collecte Terrain</span>
        </div>
        <h1 className="text-xl font-black text-white mt-1 leading-snug">
          Inventaires Forestiers & Enquêtes Numériques
        </h1>
        <p className="text-xs text-zinc-300 mt-1">
          Thèse de Doctorat en Écologie Fonctionnelle & Bio-informatique (2026–2029)
        </p>
        <div className="mt-3 flex items-center justify-between text-[11px] text-zinc-400 border-t border-savanna-800/80 pt-2.5">
          <span>Maître d'ouvrage : <strong className="text-zinc-200">YAGO Abdoul Rachide</strong></span>
          <span className="flex items-center text-emerald-400 font-semibold">
            <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Offline-First
          </span>
        </div>
      </div>

      {/* Offline Sync Status Card */}
      <div className="bg-zinc-900/90 border border-zinc-800 rounded-2xl p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Database className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-zinc-200">
              Persistance Locale IndexedDB
            </span>
          </div>
          {totalPending > 0 ? (
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-sahel-600 text-white font-bold animate-pulse">
              {totalPending} en attente de sync
            </span>
          ) : (
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold flex items-center">
              <CheckCircle2 className="w-3 h-3 mr-1" /> À jour
            </span>
          )}
        </div>

        <div className="grid grid-cols-4 gap-2 text-center text-xs">
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-white">{plotsCount}</span>
            <span className="text-[10px] text-zinc-400">Placettes</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-white">{indCount}</span>
            <span className="text-[10px] text-zinc-400">Arbres</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-white">{traitsCount}</span>
            <span className="text-[10px] text-zinc-400">Traits</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-white">{surveysCount}</span>
            <span className="text-[10px] text-zinc-400">Enquêtes</span>
          </div>
        </div>

        {totalPending > 0 && (
          <Link
            href="/sync"
            className="mt-3 w-full py-2 px-3 rounded-xl bg-sahel-600 hover:bg-sahel-500 text-black text-xs font-bold flex items-center justify-center transition active:scale-95"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Synchroniser {totalPending} données vers SahelTraits-DB
          </Link>
        )}
      </div>

      {/* Main Feature Navigation Grid */}
      <div className="space-y-2">
        <span className="text-xs font-bold uppercase tracking-wider text-zinc-400 px-1">
          Modules de Terrain
        </span>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <Link
            href="/plots"
            className="flex items-center justify-between p-3.5 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 hover:border-savanna-700 rounded-2xl transition group"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-savanna-950 text-emerald-400 border border-savanna-800">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition">
                  Placettes (50m × 20m)
                </h3>
                <p className="text-[11px] text-zinc-400">
                  GPS &lt; 5m, altitude, pente et régénération
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-zinc-500 group-hover:translate-x-1 transition" />
          </Link>

          <Link
            href="/inventory"
            className="flex items-center justify-between p-3.5 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 hover:border-savanna-700 rounded-2xl transition group"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-savanna-950 text-emerald-400 border border-savanna-800">
                <Trees className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition">
                  Inventaire Dendrométrique
                </h3>
                <p className="text-[11px] text-zinc-400">
                  DHP ≥ 5 cm, hauteur, houppier, score 1-5
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-zinc-500 group-hover:translate-x-1 transition" />
          </Link>

          <Link
            href="/traits"
            className="flex items-center justify-between p-3.5 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 hover:border-savanna-700 rounded-2xl transition group"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-savanna-950 text-emerald-400 border border-savanna-800">
                <FlaskConical className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition">
                  Mesures Traits ETS v1.0
                </h3>
                <p className="text-[11px] text-zinc-400">
                  SLA, LDMC, bois, alerte 3σ & validation
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-zinc-500 group-hover:translate-x-1 transition" />
          </Link>

          <Link
            href="/qrcode"
            className="flex items-center justify-between p-3.5 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 hover:border-savanna-700 rounded-2xl transition group"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-savanna-950 text-emerald-400 border border-savanna-800">
                <QrCode className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition">
                  QR-Codes & Traçabilité
                </h3>
                <p className="text-[11px] text-zinc-400">
                  Scanner caméra & générateur d'étiquettes
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-zinc-500 group-hover:translate-x-1 transition" />
          </Link>

          <Link
            href="/surveys"
            className="flex items-center justify-between p-3.5 bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 hover:border-savanna-700 rounded-2xl transition group sm:col-span-2"
          >
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-savanna-950 text-emerald-400 border border-savanna-800">
                <ClipboardList className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition">
                  Module Enquêtes Socio-Écologiques (M1–M5)
                </h3>
                <p className="text-[11px] text-zinc-400">
                  450 répondants (150 experts, 300 riverains), Smith Saliency & XLSForm Kobo
                </p>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-zinc-500 group-hover:translate-x-1 transition" />
          </Link>
        </div>
      </div>

      {/* XLSForm KoboToolbox Direct Download Section */}
      <div className="p-4 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-between">
        <div className="space-y-0.5">
          <span className="text-xs font-bold text-zinc-100 block">
            Fichier XLSForm Déployable (Kobo / ODK)
          </span>
          <span className="text-[11px] text-zinc-400 block">
            sahelfield_enquete_socioeco.xlsx (Standard XLSForm validé)
          </span>
        </div>
        <a
          href="/forms/sahelfield_enquete_socioeco.xlsx"
          download="sahelfield_enquete_socioeco.xlsx"
          className="py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center transition active:scale-95 shadow-md flex-shrink-0"
        >
          <Download className="w-3.5 h-3.5 mr-1" /> Télécharger .xlsx
        </a>
      </div>
    </div>
  );
}
