'use client';

import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, Volume2, VolumeX, ShieldCheck } from 'lucide-react';
import { speechService } from '@/lib/speechFeedback';
import { syncService } from '@/lib/syncService';

export default function OfflineBadge() {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(true);
  const [pendingCount, setPendingCount] = useState<number>(0);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setIsOnline(navigator.onLine);
      setVoiceEnabled(speechService.getIsEnabled());

      const handleOnline = () => {
        setIsOnline(true);
        speechService.speak('Connexion internet rétablie. Synchronisation possible.');
      };
      const handleOffline = () => {
        setIsOnline(false);
        speechService.speak('Mode hors-ligne activé. Les données restent sécurisées sur le smartphone.');
      };

      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      // Refresh pending count
      const updatePending = async () => {
        try {
          const counts = await syncService.countPendingItems();
          setPendingCount(counts.total);
        } catch {}
      };
      updatePending();
      const interval = setInterval(updatePending, 3000);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
        clearInterval(interval);
      };
    }
  }, []);

  const toggleVoice = () => {
    const next = !voiceEnabled;
    setVoiceEnabled(next);
    speechService.setEnabled(next);
    if (next) {
      speechService.speak('Synthèse vocale activée.');
    }
  };

  return (
    <div className="flex items-center justify-between px-3 py-1.5 bg-savanna-950/95 text-xs border-b border-savanna-800 text-zinc-200">
      <div className="flex items-center space-x-2">
        {isOnline ? (
          <span className="flex items-center px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-700 font-medium">
            <Wifi className="w-3.5 h-3.5 mr-1" /> En Ligne (4G/Wi-Fi)
          </span>
        ) : (
          <span className="flex items-center px-2 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-700 font-medium animate-pulse">
            <WifiOff className="w-3.5 h-3.5 mr-1" /> 100% Hors-Ligne (Stockage Sécurisé)
          </span>
        )}

        {pendingCount > 0 && (
          <span className="px-2 py-0.5 rounded-full bg-sahel-600 text-white font-bold">
            {pendingCount} en attente
          </span>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={toggleVoice}
          title={voiceEnabled ? 'Désactiver la voix' : 'Activer la voix'}
          className={`p-1 rounded-md transition-colors ${
            voiceEnabled ? 'bg-savanna-800 text-emerald-400' : 'bg-zinc-800 text-zinc-500'
          }`}
        >
          {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>

        <span className="hidden sm:flex items-center text-zinc-400">
          <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-500" /> Dexie.js IndexedDB
        </span>
      </div>
    </div>
  );
}
