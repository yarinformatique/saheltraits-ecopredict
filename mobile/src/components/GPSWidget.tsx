'use client';

import React, { useState, useEffect } from 'react';
import { Crosshair, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { getGPSQualityBadge } from '@/lib/validation';
import { speechService } from '@/lib/speechFeedback';

interface GPSWidgetProps {
  onCapture: (coords: { lat: number; lng: number; altitude?: number; accuracy: number }) => void;
  initialCoords?: { lat: number; lng: number };
}

export default function GPSWidget({ onCapture, initialCoords }: GPSWidgetProps) {
  const [lat, setLat] = useState<number | null>(initialCoords?.lat || null);
  const [lng, setLng] = useState<number | null>(initialCoords?.lng || null);
  const [altitude, setAltitude] = useState<number | null>(null);
  const [accuracy, setAccuracy] = useState<number | null>(null);
  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const requestPosition = () => {
    if (!('geolocation' in navigator)) {
      setErrorMessage('La géolocalisation n\'est pas supportée par ce terminal.');
      return;
    }

    setIsLocating(true);
    setErrorMessage(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const c = pos.coords;
        setLat(c.latitude);
        setLng(c.longitude);
        setAltitude(c.altitude !== null ? Math.round(c.altitude * 10) / 10 : null);
        setAccuracy(Math.round(c.accuracy * 10) / 10);
        setIsLocating(false);

        onCapture({
          lat: c.latitude,
          lng: c.longitude,
          altitude: c.altitude || undefined,
          accuracy: c.accuracy,
        });

        if (c.accuracy <= 5.0) {
          speechService.speak(`Signal GPS haute précision acquis : ${c.accuracy.toFixed(1)} mètres.`);
        } else {
          speechService.notifyWarning(`Précision GPS modérée : ${c.accuracy.toFixed(1)} mètres.`);
        }
      },
      (err) => {
        setIsLocating(false);
        let msg = 'Impossible de lire le GPS';
        if (err.code === err.PERMISSION_DENIED) msg = 'Autorisation GPS refusée';
        if (err.code === err.POSITION_UNAVAILABLE) msg = 'Position satellite indisponible';
        if (err.code === err.TIMEOUT) msg = 'Délai d\'attente GPS expiré';
        setErrorMessage(msg);
        speechService.notifyWarning(msg);
      },
      {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 0,
      }
    );
  };

  useEffect(() => {
    // If no initial coordinates, trigger auto GPS capture on mount
    if (!initialCoords?.lat) {
      requestPosition();
    }
  }, []);

  const badge = getGPSQualityBadge(accuracy ?? undefined);

  return (
    <div className="bg-zinc-900 border border-savanna-800 rounded-xl p-3 shadow-md">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-300 flex items-center">
          <Crosshair className="w-4 h-4 mr-1 text-emerald-400" /> Coordonnées Terrain GPS
        </span>
        <span className={`text-[11px] px-2 py-0.5 rounded-full font-bold ${badge.color}`}>
          {badge.label}
        </span>
      </div>

      {errorMessage && (
        <div className="flex items-center text-xs text-red-400 bg-red-950/40 p-2 rounded-lg mb-2 border border-red-800">
          <AlertTriangle className="w-4 h-4 mr-1 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 text-xs mb-3">
        <div className="bg-zinc-950 p-2 rounded border border-zinc-800">
          <span className="text-zinc-500 block text-[10px]">LATITUDE (WGS84)</span>
          <span className="font-mono text-zinc-100 font-bold">
            {lat !== null ? lat.toFixed(6) + '°' : 'En attente...'}
          </span>
        </div>
        <div className="bg-zinc-950 p-2 rounded border border-zinc-800">
          <span className="text-zinc-500 block text-[10px]">LONGITUDE (WGS84)</span>
          <span className="font-mono text-zinc-100 font-bold">
            {lng !== null ? lng.toFixed(6) + '°' : 'En attente...'}
          </span>
        </div>
        <div className="bg-zinc-950 p-2 rounded border border-zinc-800">
          <span className="text-zinc-500 block text-[10px]">ALTITUDE</span>
          <span className="font-mono text-zinc-100">
            {altitude !== null ? `${altitude} m` : '—'}
          </span>
        </div>
        <div className="bg-zinc-950 p-2 rounded border border-zinc-800">
          <span className="text-zinc-500 block text-[10px]">PRÉCISION ESTIMÉE</span>
          <span className="font-mono text-zinc-100 font-semibold">
            {accuracy !== null ? `± ${accuracy} m` : '—'}
          </span>
        </div>
      </div>

      <button
        type="button"
        onClick={requestPosition}
        disabled={isLocating}
        className="w-full flex items-center justify-center py-2 px-3 rounded-lg bg-savanna-800 hover:bg-savanna-700 text-emerald-200 text-xs font-semibold transition active:scale-95 disabled:opacity-50"
      >
        <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLocating ? 'animate-spin' : ''}`} />
        {isLocating ? 'Fixation des satellites...' : 'Re-capturer Position GPS (Haute Précision)'}
      </button>
    </div>
  );
}
