"use client";

import React from "react";

interface RadarChartProps {
  data: {
    sla: number; // 0-100 normalized
    ldmc: number;
    wood_density: number;
    cavitation: number;
    seed_mass: number;
    drought: number;
    fire: number;
    germination_peg: number;
  };
  labels?: string[];
  size?: number;
  speciesName?: string;
}

export const RadarChart: React.FC<RadarChartProps> = ({
  data,
  size = 320,
  speciesName,
}) => {
  const axes = [
    { key: "sla", label: "SLA (Foliaire)" },
    { key: "ldmc", label: "LDMC (Matière Sèche)" },
    { key: "wood_density", label: "Densité Bois (Xylème)" },
    { key: "cavitation", label: "Sécurité Hydr. (|P50|)" },
    { key: "germination_peg", label: "Germin. sous PEG" },
    { key: "drought", label: "Résistance Sécheresse" },
    { key: "fire", label: "Résistance Feux" },
    { key: "seed_mass", label: "Masse Semence" },
  ];

  const center = size / 2;
  const radius = (size / 2) - 45;
  const totalAxes = axes.length;
  const angleSlice = (Math.PI * 2) / totalAxes;

  // Compute points
  const points = axes.map((axis, i) => {
    const val = Math.max(10, Math.min(100, (data as any)[axis.key] || 50));
    const r = (val / 100) * radius;
    const angle = i * angleSlice - Math.PI / 2;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return { x, y, val };
  });

  const polygonPath = points.map((p) => `${p.x},${p.y}`).join(" ");

  // Grid circles
  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className="flex flex-col items-center justify-center p-2 bg-slate-50 rounded-xl border border-slate-200">
      <svg width={size} height={size} className="overflow-visible">
        {/* Concentric grid rings */}
        {gridLevels.map((lvl, idx) => (
          <circle
            key={idx}
            cx={center}
            cy={center}
            r={radius * lvl}
            fill="none"
            stroke="#e2e8f0"
            strokeDasharray={lvl < 1 ? "3 3" : undefined}
            strokeWidth="1.2"
          />
        ))}

        {/* Axis lines */}
        {axes.map((axis, i) => {
          const angle = i * angleSlice - Math.PI / 2;
          const x2 = center + radius * Math.cos(angle);
          const y2 = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke="#cbd5e1"
              strokeWidth="1"
            />
          );
        })}

        {/* Data polygon with gradient */}
        <defs>
          <linearGradient id="radarGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#22c55e" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#059669" stopOpacity="0.25" />
          </linearGradient>
        </defs>

        <polygon
          points={polygonPath}
          fill="url(#radarGradient)"
          stroke="#16a34a"
          strokeWidth="2.5"
          className="transition-all duration-300"
        />

        {/* Data point dots */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="4.5"
            fill="#15803d"
            stroke="#ffffff"
            strokeWidth="2"
            className="hover:scale-125 transition-transform"
          />
        ))}

        {/* Axis text labels */}
        {axes.map((axis, i) => {
          const angle = i * angleSlice - Math.PI / 2;
          const labelDist = radius + 22;
          const lx = center + labelDist * Math.cos(angle);
          const ly = center + labelDist * Math.sin(angle);
          let textAnchor = "middle";
          if (Math.cos(angle) > 0.3) textAnchor = "start";
          if (Math.cos(angle) < -0.3) textAnchor = "end";

          return (
            <text
              key={i}
              x={lx}
              y={ly}
              textAnchor={textAnchor}
              dominantBaseline="central"
              className="text-[10px] font-medium fill-slate-700 select-none"
            >
              {axis.label}
            </text>
          );
        })}
      </svg>
      {speciesName && (
        <span className="text-xs text-slate-500 italic mt-2">
          Profil multi-organes normalisé (ETS v1.0)
        </span>
      )}
    </div>
  );
};
