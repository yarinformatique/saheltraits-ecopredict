'use client';

import React, { useState, useEffect } from 'react';
import QRCode from 'qrcode';
import { Download, Printer, Copy, Check, QrCode as QrIcon } from 'lucide-react';

interface QRTagGeneratorProps {
  initialPlotId?: string;
  initialSpeciesCode?: string;
  initialTreeId?: string;
}

export default function QRTagGenerator({
  initialPlotId = 'BF-DOR-01',
  initialSpeciesCode = 'BAL',
  initialTreeId = '001',
}: QRTagGeneratorProps) {
  const [plotId, setPlotId] = useState<string>(initialPlotId);
  const [speciesCode, setSpeciesCode] = useState<string>(initialSpeciesCode);
  const [treeNum, setTreeNum] = useState<string>(initialTreeId);
  const [sampleType, setSampleType] = useState<'TREE' | 'LEAF' | 'WOOD' | 'SEED' | 'SOIL'>('TREE');

  const [qrDataUrl, setQrDataUrl] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);

  // Compute tag code
  const getTagCode = () => {
    const cleanPlot = plotId.trim().toUpperCase() || 'PLOT';
    const cleanSp = speciesCode.trim().toUpperCase() || 'SP';
    const cleanNum = treeNum.trim().padStart(3, '0');

    switch (sampleType) {
      case 'TREE':
        return `TAG-${cleanPlot}-${cleanSp}-${cleanNum}`;
      case 'LEAF':
        return `TAG-LEAF-${cleanPlot}-${cleanSp}-${cleanNum}-A`;
      case 'WOOD':
        return `TAG-WOOD-${cleanPlot}-${cleanSp}-${cleanNum}`;
      case 'SEED':
        return `LOT-${cleanSp}-${cleanPlot}-2026-${cleanNum}`;
      case 'SOIL':
        return `TAG-SOIL-${cleanPlot}-S${cleanNum}`;
      default:
        return `TAG-${cleanPlot}-${cleanSp}-${cleanNum}`;
    }
  };

  const tagCode = getTagCode();

  useEffect(() => {
    QRCode.toDataURL(tagCode, {
      width: 250,
      margin: 2,
      color: {
        dark: '#0c2312',
        light: '#ffffff',
      },
    })
      .then((url) => setQrDataUrl(url))
      .catch((err) => console.error('QR code generation error:', err));
  }, [tagCode]);

  const handleCopy = () => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(tagCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!qrDataUrl) return;
    const a = document.createElement('a');
    a.href = qrDataUrl;
    a.download = `${tagCode}.png`;
    a.click();
  };

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  return (
    <div className="bg-zinc-900 border border-savanna-800 rounded-2xl p-4 shadow-lg text-zinc-100">
      <div className="flex items-center space-x-2 text-emerald-400 font-bold mb-3 text-sm">
        <QrIcon className="w-5 h-5" />
        <span>Générateur d'Identifiants & QR-Codes Terrain</span>
      </div>

      {/* Select sample organ */}
      <div className="grid grid-cols-5 gap-1 text-[11px] font-semibold mb-3">
        {(['TREE', 'LEAF', 'WOOD', 'SEED', 'SOIL'] as const).map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setSampleType(type)}
            className={`py-1.5 px-1 rounded-lg border text-center transition ${
              sampleType === type
                ? 'bg-emerald-600 border-emerald-400 text-white font-bold'
                : 'bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-zinc-200'
            }`}
          >
            {type === 'TREE' && 'Arbre'}
            {type === 'LEAF' && 'Feuilles'}
            {type === 'WOOD' && 'Bois'}
            {type === 'SEED' && 'Graines'}
            {type === 'SOIL' && 'Sol'}
          </button>
        ))}
      </div>

      {/* Inputs */}
      <div className="grid grid-cols-3 gap-2 text-xs mb-3">
        <div>
          <label className="text-zinc-400 text-[10px] block mb-1">PLACETTE</label>
          <input
            type="text"
            value={plotId}
            onChange={(e) => setPlotId(e.target.value.toUpperCase())}
            className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-2 py-1.5 font-mono text-xs text-white"
          />
        </div>
        <div>
          <label className="text-zinc-400 text-[10px] block mb-1">CODE ESSENCE</label>
          <input
            type="text"
            value={speciesCode}
            onChange={(e) => setSpeciesCode(e.target.value.toUpperCase())}
            placeholder="BAL, FAI..."
            className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-2 py-1.5 font-mono text-xs text-white"
          />
        </div>
        <div>
          <label className="text-zinc-400 text-[10px] block mb-1">N° INDIVIDU</label>
          <input
            type="text"
            value={treeNum}
            onChange={(e) => setTreeNum(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-2 py-1.5 font-mono text-xs text-white"
          />
        </div>
      </div>

      {/* Live Label Card */}
      <div className="bg-white text-zinc-900 rounded-xl p-3 flex items-center space-x-3 border-2 border-dashed border-zinc-400 my-3">
        {qrDataUrl ? (
          <img
            src={qrDataUrl}
            alt="QR Code"
            className="w-24 h-24 object-contain rounded border border-zinc-200"
          />
        ) : (
          <div className="w-24 h-24 bg-zinc-200 animate-pulse rounded" />
        )}
        <div className="flex-1 min-w-0">
          <div className="text-[10px] uppercase font-bold text-zinc-500 tracking-wider">
            SAHELTRAITS-DB — ÉCHANTILLON
          </div>
          <div className="font-mono font-black text-sm text-emerald-800 break-all leading-tight my-1">
            {tagCode}
          </div>
          <div className="text-[11px] text-zinc-600">
            Placette : <strong>{plotId}</strong> | Organe : <strong>{sampleType}</strong>
          </div>
          <div className="text-[10px] text-zinc-400 mt-1">
            Date : {new Date().toLocaleDateString('fr-FR')} | Traçabilité Doctorat
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex space-x-2 text-xs">
        <button
          type="button"
          onClick={handleCopy}
          className="flex-1 flex items-center justify-center py-2 px-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition font-medium"
        >
          {copied ? <Check className="w-3.5 h-3.5 mr-1 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
          {copied ? 'Copié !' : 'Copier Tag'}
        </button>

        <button
          type="button"
          onClick={handleDownload}
          className="flex-1 flex items-center justify-center py-2 px-3 rounded-lg bg-savanna-800 hover:bg-savanna-700 text-emerald-200 transition font-medium"
        >
          <Download className="w-3.5 h-3.5 mr-1" /> Télécharger PNG
        </button>

        <button
          type="button"
          onClick={handlePrint}
          className="flex items-center justify-center py-2 px-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition"
          title="Imprimer l'étiquette"
        >
          <Printer className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
