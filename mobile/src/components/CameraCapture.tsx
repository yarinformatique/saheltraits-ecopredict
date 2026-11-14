'use client';

import React, { useRef } from 'react';
import { Camera, Image as ImageIcon, Trash2 } from 'lucide-react';

interface CameraCaptureProps {
  photoBase64?: string;
  onPhotoChange: (base64: string | undefined) => void;
  label?: string;
}

export default function CameraCapture({
  photoBase64,
  onPhotoChange,
  label = 'Photo de l\'arbre / échantillon',
}: CameraCaptureProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      // Create an image to resize/compress to max 1024px to preserve IndexedDB storage
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 1024;
        const scale = Math.min(1, MAX_WIDTH / img.width);
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.8);
          onPhotoChange(compressedDataUrl);
        } else {
          onPhotoChange(reader.result as string);
        }
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-3">
      <span className="text-[11px] font-semibold text-zinc-300 block mb-2 flex items-center">
        <Camera className="w-3.5 h-3.5 mr-1 text-emerald-400" /> {label}
      </span>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
      />

      {photoBase64 ? (
        <div className="relative rounded-lg overflow-hidden border border-zinc-700 aspect-video max-h-48 bg-black">
          <img
            src={photoBase64}
            alt="Capture terrain"
            className="w-full h-full object-cover"
          />
          <button
            type="button"
            onClick={() => onPhotoChange(undefined)}
            className="absolute top-2 right-2 p-1.5 rounded-full bg-red-600/90 text-white hover:bg-red-500 shadow-md transition"
            title="Supprimer la photo"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="w-full border-2 border-dashed border-zinc-700 hover:border-emerald-500 rounded-xl py-6 flex flex-col items-center justify-center text-zinc-400 hover:text-zinc-200 transition"
        >
          <Camera className="w-8 h-8 text-zinc-500 mb-1" />
          <span className="text-xs font-medium">Prendre une photo (Caméra native)</span>
          <span className="text-[10px] text-zinc-500">Ou importer depuis la galerie</span>
        </button>
      )}
    </div>
  );
}
