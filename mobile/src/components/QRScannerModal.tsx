'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Camera, X, CheckCircle, Keyboard, RefreshCw, AlertCircle } from 'lucide-react';
import { speechService } from '@/lib/speechFeedback';

interface QRScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScanSuccess: (scannedText: string) => void;
  title?: string;
}

export default function QRScannerModal({
  isOpen,
  onClose,
  onScanSuccess,
  title = 'Scanner Étiquette QR-Code',
}: QRScannerModalProps) {
  const [manualCode, setManualCode] = useState<string>('');
  const [useCamera, setUseCamera] = useState<boolean>(true);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (isOpen && useCamera) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [isOpen, useCamera]);

  const startCamera = async () => {
    setCameraError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraError('Caméra non accessible sur ce navigateur. Utiliser la saisie manuelle.');
        setUseCamera(false);
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err: any) {
      console.warn('Camera stream error:', err);
      setCameraError('Accès caméra bloqué ou non disponible. Veuillez saisir le tag manuellement.');
      setUseCamera(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleConfirm = (code: string) => {
    const clean = code.trim();
    if (!clean) return;
    speechService.speak(`Code ${clean} scanné.`);
    onScanSuccess(clean);
    stopCamera();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-sm bg-zinc-900 border border-savanna-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-3.5 bg-zinc-950 border-b border-zinc-800">
          <div className="flex items-center space-x-2 text-zinc-100 font-semibold text-sm">
            <Camera className="w-4 h-4 text-emerald-400" />
            <span>{title}</span>
          </div>
          <button
            onClick={() => {
              stopCamera();
              onClose();
            }}
            className="p-1 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Viewfinder or Manual Mode */}
        <div className="p-4 flex flex-col items-center">
          {useCamera ? (
            <div className="relative w-full aspect-square max-w-[260px] bg-black rounded-xl overflow-hidden border-2 border-emerald-500/60 flex items-center justify-center">
              <video
                ref={videoRef}
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              {/* Overlay target frame */}
              <div className="absolute inset-8 border-2 border-dashed border-emerald-400/80 rounded-lg pointer-events-none animate-pulse flex items-center justify-center">
                <span className="text-[10px] text-emerald-200 bg-black/70 px-2 py-0.5 rounded">
                  Centrer le QR-Code
                </span>
              </div>
            </div>
          ) : (
            <div className="w-full py-4 px-2 text-center text-zinc-400 text-xs">
              {cameraError && (
                <div className="mb-3 p-2 bg-amber-950/60 border border-amber-800 rounded-lg text-amber-300 text-left flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-400" />
                  <span>{cameraError}</span>
                </div>
              )}
              <Keyboard className="w-10 h-10 mx-auto text-zinc-600 mb-2" />
              <span>Saisissez directement l'identifiant imprimé sur l'étiquette de terrain.</span>
            </div>
          )}

          {/* Quick test presets button */}
          <div className="w-full mt-3 flex flex-wrap gap-1.5 justify-center">
            <span className="text-[10px] text-zinc-500 w-full text-center">Codes de test rapides :</span>
            {['TAG-BF-DOR-BAL-001', 'TAG-BF-KAY-FAI-002', 'TAG-LEAF-BAL-01'].map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleConfirm(tag)}
                className="text-[11px] bg-zinc-800 hover:bg-zinc-700 text-zinc-300 px-2 py-1 rounded border border-zinc-700 font-mono"
              >
                {tag}
              </button>
            ))}
          </div>

          {/* Manual Input field */}
          <div className="w-full mt-4">
            <label className="text-[11px] text-zinc-400 font-medium block mb-1">
              Saisie manuelle ou code lu :
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={manualCode}
                onChange={(e) => setManualCode(e.target.value.toUpperCase())}
                placeholder="Ex: TAG-BF-DOR-BAL-001"
                className="flex-1 bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs font-mono text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-emerald-500"
              />
              <button
                type="button"
                onClick={() => handleConfirm(manualCode)}
                disabled={!manualCode.trim()}
                className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-lg text-xs font-semibold flex items-center"
              >
                <CheckCircle className="w-4 h-4 mr-1" /> Valider
              </button>
            </div>
          </div>
        </div>

        {/* Footer controls */}
        <div className="p-3 bg-zinc-950 border-t border-zinc-800 flex justify-between">
          <button
            type="button"
            onClick={() => setUseCamera(!useCamera)}
            className="text-xs text-zinc-400 hover:text-zinc-200 flex items-center"
          >
            {useCamera ? (
              <>
                <Keyboard className="w-3.5 h-3.5 mr-1" /> Passer en saisie clavier
              </>
            ) : (
              <>
                <Camera className="w-3.5 h-3.5 mr-1" /> Activer la caméra
              </>
            )}
          </button>
          <button
            type="button"
            onClick={() => {
              stopCamera();
              onClose();
            }}
            className="text-xs text-zinc-400 hover:text-zinc-200"
          >
            Annuler
          </button>
        </div>
      </div>
    </div>
  );
}
