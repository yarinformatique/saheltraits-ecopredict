'use client';

import React, { useState, useEffect } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import { syncService } from '@/lib/syncService';
import { speechService } from '@/lib/speechFeedback';
import { SyncBatchResponsePayload } from '@/types';
import {
  RefreshCw,
  Server,
  Lock,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  Trees,
  FlaskConical,
  ClipboardList,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export default function SyncPage() {
  const [apiUrl, setApiUrl] = useState<string>('http://localhost:8000');
  const [username, setUsername] = useState<string>('enqueteur_terrain');
  const [password, setPassword] = useState<string>('Doctorat2027!');
  const [authStatus, setAuthStatus] = useState<string>('');
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [syncResult, setSyncResult] = useState<SyncBatchResponsePayload | null>(null);
  const [showPayloadPreview, setShowPayloadPreview] = useState<boolean>(false);

  // Live queries
  const pendingPlots = useLiveQuery(() => db.plots.where('sync_status').equals('PENDING').toArray(), [], []);
  const pendingInds = useLiveQuery(() => db.individuals.where('sync_status').equals('PENDING').toArray(), [], []);
  const pendingTraits = useLiveQuery(() => db.traits.where('sync_status').equals('PENDING').toArray(), [], []);
  const pendingSeeds = useLiveQuery(() => db.seed_trials.where('sync_status').equals('PENDING').toArray(), [], []);
  const pendingSoils = useLiveQuery(() => db.soil_records.where('sync_status').equals('PENDING').toArray(), [], []);
  const pendingSurveys = useLiveQuery(() => db.surveys.where('sync_status').equals('PENDING').toArray(), [], []);
  const syncLogs = useLiveQuery(() => db.sync_logs.orderBy('timestamp').reverse().toArray(), [], []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setApiUrl(syncService.getApiBaseUrl());
      const hasToken = syncService.getToken();
      if (hasToken) {
        setAuthStatus('Connecté avec jeton Bearer JWT');
      }
    }
  }, []);

  const handleUpdateUrl = (url: string) => {
    setApiUrl(url);
    syncService.setApiBaseUrl(url);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthStatus('Authentification en cours...');
    const res = await syncService.login(username, password);
    if (res.success) {
      setAuthStatus(`Connecté avec succès (${res.role || 'Opérateur terrain'})`);
      speechService.speak('Authentification au serveur réussie.');
    } else {
      setAuthStatus(`Échec : ${res.message}`);
      speechService.notifyWarning('Échec d\'authentification au serveur.');
    }
  };

  const handleRunSync = async () => {
    setIsSyncing(true);
    setSyncResult(null);
    try {
      const res = await syncService.syncPendingBatch();
      setSyncResult(res);
    } catch (err: any) {
      alert(`Erreur d'exécution : ${err.message}`);
    } finally {
      setIsSyncing(false);
    }
  };

  const totalPending =
    pendingPlots.length +
    pendingInds.length +
    pendingTraits.length +
    pendingSeeds.length +
    pendingSoils.length +
    pendingSurveys.length;

  return (
    <div className="space-y-4 animate-fade-in pb-12 text-xs">
      {/* Header */}
      <div>
        <h1 className="text-lg font-black text-white flex items-center">
          <RefreshCw className="w-5 h-5 mr-1.5 text-emerald-400" /> Synchronisation Différée
        </h1>
        <p className="text-xs text-zinc-400">
          Transmission intelligente vers l'endpoint <code>POST /api/v1/sync/field-batch</code>
        </p>
      </div>

      {/* Backend API Configuration & Authentication */}
      <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3 shadow-md">
        <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
          <Server className="w-4 h-4" />
          <span>Connexion Serveur SahelTraits-DB</span>
        </div>

        <div>
          <label className="text-zinc-400 text-[10px] uppercase font-semibold block mb-1">
            URL DU BACKEND FASTAPI
          </label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => handleUpdateUrl(e.target.value)}
            placeholder="http://localhost:8000"
            className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 font-mono text-zinc-100"
          />
        </div>

        {/* Login form */}
        <form onSubmit={handleLogin} className="space-y-2 pt-1 border-t border-zinc-800">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-zinc-300 flex items-center">
              <Lock className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Authentification Enquêteur (JWT)
            </span>
            {authStatus && (
              <span className={`text-[10px] font-mono ${
                authStatus.includes('succès') || authStatus.includes('Connecté')
                  ? 'text-emerald-400'
                  : 'text-amber-400'
              }`}>
                {authStatus}
              </span>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-zinc-400 text-[10px] block mb-0.5">UTILISATEUR</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-1.5 text-zinc-100 font-mono"
              />
            </div>
            <div>
              <label className="text-zinc-400 text-[10px] block mb-0.5">MOT DE PASSE</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-1.5 text-zinc-100 font-mono"
              />
            </div>
          </div>

          <div className="flex space-x-2">
            <button
              type="submit"
              className="py-1.5 px-3 bg-savanna-800 hover:bg-savanna-700 text-emerald-200 rounded-lg text-xs font-bold transition flex items-center"
            >
              <Lock className="w-3.5 h-3.5 mr-1" /> S'authentifier
            </button>
            <button
              type="button"
              onClick={() => {
                setUsername('yago_rachide');
                setPassword('Doctorat2027!');
              }}
              className="py-1 px-2 text-[10px] text-zinc-500 hover:text-zinc-300"
            >
              Profil Admin (YAGO)
            </button>
          </div>
        </form>
      </div>

      {/* Sync Queue Summary Card */}
      <div className="p-4 bg-zinc-900 border border-savanna-700 rounded-2xl space-y-3.5 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <RefreshCw className={`w-4 h-4 text-emerald-400 ${isSyncing ? 'animate-spin' : ''}`} />
            <span className="font-bold text-sm text-zinc-100">
              File d'Attente Locale ({totalPending} éléments)
            </span>
          </div>
          <span className="text-[10px] font-mono text-zinc-400 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800">
            {syncService.getDeviceId()}
          </span>
        </div>

        {/* Breakdown */}
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-emerald-400">{pendingPlots.length}</span>
            <span className="text-[10px] text-zinc-400">Placettes</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-emerald-400">{pendingInds.length}</span>
            <span className="text-[10px] text-zinc-400">Arbres QR</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-emerald-400">{pendingTraits.length}</span>
            <span className="text-[10px] text-zinc-400">Traits ETS</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-emerald-400">{pendingSeeds.length}</span>
            <span className="text-[10px] text-zinc-400">Germinations</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-emerald-400">{pendingSoils.length}</span>
            <span className="text-[10px] text-zinc-400">Sols</span>
          </div>
          <div className="bg-zinc-950 p-2 rounded-xl border border-zinc-800">
            <span className="block text-lg font-black text-emerald-400">{pendingSurveys.length}</span>
            <span className="text-[10px] text-zinc-400">Enquêtes M1-M5</span>
          </div>
        </div>

        {/* Sync Trigger Button */}
        <button
          type="button"
          onClick={handleRunSync}
          disabled={isSyncing || totalPending === 0}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-xl font-black text-sm flex items-center justify-center space-x-2 shadow-xl transition active:scale-98"
        >
          <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
          <span>
            {isSyncing
              ? 'Transmission du lot en cours...'
              : totalPending > 0
              ? `Synchroniser ${totalPending} Éléments vers SahelTraits-DB`
              : 'Toutes les données locales sont déjà synchronisées'}
          </span>
        </button>

        {/* Payload inspector toggle */}
        {totalPending > 0 && (
          <div>
            <button
              type="button"
              onClick={() => setShowPayloadPreview(!showPayloadPreview)}
              className="text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center space-x-1"
            >
              {showPayloadPreview ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              <span>Inspecter le lot JSON SyncBatchRequest</span>
            </button>
            {showPayloadPreview && (
              <pre className="mt-2 p-2.5 bg-zinc-950 rounded-xl border border-zinc-800 text-[10px] font-mono text-zinc-300 overflow-x-auto max-h-48">
                {JSON.stringify(
                  {
                    batch_id: 'PREVIEW-BATCH-001',
                    device_id: syncService.getDeviceId(),
                    collected_at: new Date().toISOString(),
                    plots_count: pendingPlots.length,
                    individuals_count: pendingInds.length,
                    traits_count: pendingTraits.length,
                    surveys_count: pendingSurveys.length,
                    samples: {
                      plots: pendingPlots.slice(0, 1),
                      individuals: pendingInds.slice(0, 1),
                    },
                  },
                  null,
                  2
                )}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Sync Result Card */}
      {syncResult && (
        <div className={`p-4 rounded-2xl border shadow-xl animate-fade-in space-y-2 ${
          syncResult.status === 'SUCCESS'
            ? 'bg-emerald-950/70 border-emerald-700 text-emerald-200'
            : syncResult.status === 'PARTIAL'
            ? 'bg-amber-950/70 border-amber-700 text-amber-200'
            : 'bg-red-950/70 border-red-700 text-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <span className="font-bold text-sm flex items-center">
              {syncResult.status === 'SUCCESS' && <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-400" />}
              {syncResult.status === 'PARTIAL' && <AlertTriangle className="w-4 h-4 mr-1.5 text-amber-400" />}
              {syncResult.status === 'ERROR' && <ShieldAlert className="w-4 h-4 mr-1.5 text-red-400" />}
              Statut : {syncResult.status}
            </span>
            <span className="font-mono text-[10px]">{syncResult.batch_id}</span>
          </div>

          <p className="text-xs font-semibold">{syncResult.message}</p>

          <div className="grid grid-cols-3 gap-2 text-center text-[11px] pt-1 font-mono">
            <div className="bg-black/30 p-1.5 rounded">
              <span>Placettes : <strong>{syncResult.plots_synced}</strong></span>
            </div>
            <div className="bg-black/30 p-1.5 rounded">
              <span>Arbres : <strong>{syncResult.individuals_synced}</strong></span>
            </div>
            <div className="bg-black/30 p-1.5 rounded">
              <span>Traits : <strong>{syncResult.traits_synced}</strong></span>
            </div>
          </div>

          {syncResult.flagged_outliers_count > 0 && (
            <div className="p-2 rounded bg-amber-900/60 border border-amber-600 text-amber-200 text-[11px]">
              ⚠️ <strong>{syncResult.flagged_outliers_count} mesure(s)</strong> marquée(s) comme SUSPECT_OUTLIER_3SIGMA par le contrôle qualité backend.
            </div>
          )}

          {syncResult.errors && syncResult.errors.length > 0 && (
            <div className="text-[10px] space-y-1">
              <span className="font-bold">Anomalies rapportées :</span>
              {syncResult.errors.map((err, i) => (
                <div key={i} className="font-mono bg-red-950 p-1 rounded">
                  {err}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sync History Logs */}
      <div className="space-y-2">
        <span className="text-zinc-400 font-bold uppercase tracking-wider text-[10px] block px-1">
          Historique des Synchronisations Antérieures ({syncLogs.length})
        </span>

        {syncLogs.length === 0 ? (
          <div className="p-4 text-center text-zinc-500 text-xs bg-zinc-900/50 rounded-xl">
            Aucun historique de transmission enregistré pour l'instant.
          </div>
        ) : (
          syncLogs.map((log) => (
            <div
              key={log.batch_id + log.timestamp}
              className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl flex items-center justify-between"
            >
              <div>
                <span className="font-mono font-bold text-zinc-200">{log.batch_id}</span>
                <div className="text-[10px] text-zinc-400">
                  {new Date(log.timestamp).toLocaleString('fr-FR')} • {log.message}
                </div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded font-bold font-mono ${
                log.status === 'SUCCESS'
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-red-950 text-red-400 border border-red-800'
              }`}>
                {log.status}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
