"use client";

import React, { useState, useEffect, useRef } from "react";
import { SPECIES_CATALOG } from "@/data/speciesData";
import { fetchPointDiagnosis } from "@/lib/api";
import {
  Compass,
  Layers,
  MapPin,
  Calendar,
  AlertTriangle,
  CheckCircle,
  FileText,
  Sliders,
  ChevronRight,
  Upload,
  Sparkles,
  Info,
  Droplets,
  Thermometer,
  ShieldCheck,
  Flame,
} from "lucide-react";

export const ClimateSimulator: React.FC = () => {
  const [selectedSpecies, setSelectedSpecies] = useState("Balanites aegyptiaca (L.) Delile");
  const [horizon, setHorizon] = useState<"actuel" | "2050" | "2080">("2050");
  const [scenario, setScenario] = useState<"ssp245" | "ssp585">("ssp245");
  const [layerType, setLayerType] = useState<"suitability" | "contraction" | "erosion" | "bio12">("suitability");

  // Selected coordinate for diagnosis (defaults to Dori, Sahel)
  const [coord, setCoord] = useState<{ lat: number; lon: number }>({ lat: 14.032, lon: -0.092 });
  const [siteName, setSiteName] = useState("Dori - Mare de Yakouta");
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);

  const [polygonCoords, setPolygonCoords] = useState<string>("");
  const [polygonError, setPolygonError] = useState<string | null>(null);

  // Leaflet map container reference
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markerRef = useRef<any>(null);
  const layerGroupRef = useRef<any>(null);

  // Run diagnosis whenever coordinate, horizon or scenario changes
  useEffect(() => {
    let isMounted = true;
    const runDiagnosis = async () => {
      setIsDiagnosing(true);
      try {
        const res = await fetchPointDiagnosis(coord.lat, coord.lon, horizon, scenario);
        if (isMounted) setDiagnosticResult(res);
      } catch (e) {
        console.error("Diagnosis error:", e);
      } finally {
        if (isMounted) setIsDiagnosing(false);
      }
    };
    runDiagnosis();
    return () => {
      isMounted = false;
    };
  }, [coord, horizon, scenario]);

  // Leaflet initialization on client-side
  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    let map = mapInstanceRef.current;
    if (!map) {
      const L = require("leaflet");

      // Fix default leaflet icons
      delete L.Icon.Default.prototype._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      // Init map centered on Burkina Faso
      map = L.map(mapContainerRef.current, {
        center: [12.35, -1.52],
        zoom: 7,
        minZoom: 6,
        maxZoom: 12,
        maxBounds: [
          [9.0, -6.0],
          [15.5, 3.0],
        ],
      });
      mapInstanceRef.current = map;

      // Base tile layer (OpenStreetMap / CartoDB Voyager)
      L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a> & OpenStreetMap',
        subdomains: "abcd",
        maxZoom: 19,
      }).addTo(map);

      layerGroupRef.current = L.layerGroup().addTo(map);

      // Add click handler to select point on Burkina Faso map
      map.on("click", (e: any) => {
        const lat = Number(e.latlng.lat.toFixed(4));
        const lon = Number(e.latlng.lng.toFixed(4));
        setCoord({ lat, lon });
        setSiteName(`Point GPS [${lat}°N, ${lon}°E]`);
      });
    }

    // Update marker on map
    const L = require("leaflet");
    if (markerRef.current) {
      markerRef.current.setLatLng([coord.lat, coord.lon]);
    } else {
      const customPin = L.divIcon({
        className: "custom-div-icon",
        html: `<div style="background-color: #dc2626; width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 8px rgba(0,0,0,0.5);"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      });
      markerRef.current = L.marker([coord.lat, coord.lon], { icon: customPin }).addTo(map);
    }

    // Draw Bioclimatic Bands and simulated raster cells on map
    if (layerGroupRef.current) {
      layerGroupRef.current.clearLayers();

      // Zone Sahélienne (Nord > 13.8)
      L.rectangle([[13.8, -5.5], [15.1, 2.4]], {
        color: layerType === "erosion" ? "#dc2626" : "#eab308",
        weight: 1.5,
        fillColor: layerType === "suitability" ? (scenario === "ssp585" ? "#ef4444" : "#f59e0b") : "#fef08a",
        fillOpacity: 0.22,
      }).bindTooltip("Zone Sahélienne (Dori/Oursi) • Aridité Forte", { sticky: true }).addTo(layerGroupRef.current);

      // Zone Soudano-Sahélienne (Centre 11.8 - 13.8)
      L.rectangle([[11.8, -5.5], [13.8, 2.4]], {
        color: "#22c55e",
        weight: 1.5,
        fillColor: layerType === "erosion" ? "#f97316" : (layerType === "suitability" ? "#10b981" : "#86efac"),
        fillOpacity: 0.18,
      }).bindTooltip("Zone Soudano-Sahélienne (Kaya/Ouaga) • Gradient Médian", { sticky: true }).addTo(layerGroupRef.current);

      // Zone Soudanienne (Sud < 11.8)
      L.rectangle([[9.4, -5.5], [11.8, 2.4]], {
        color: "#15803d",
        weight: 1.5,
        fillColor: layerType === "contraction" && selectedSpecies.includes("Pterocarpus") ? "#dc2626" : "#16a34a",
        fillOpacity: 0.25,
      }).bindTooltip("Zone Soudanienne (Pô/Bobo) • Refuge Climatique Ligneux", { sticky: true }).addTo(layerGroupRef.current);
    }
  }, [coord, layerType, scenario, selectedSpecies]);

  // Quick preset locations
  const presetSites = [
    { name: "Dori - Mare Yakouta (Sahel)", lat: 14.032, lon: -0.092 },
    { name: "Oursi - Dunes & Mare Ramsar", lat: 14.502, lon: -0.448 },
    { name: "Kaya - Forêt Classée Dem", lat: 13.078, lon: -1.121 },
    { name: "Ouagadougou - Ceinture Verte", lat: 12.370, lon: -1.520 },
    { name: "Pô - Parc Kaboré Tambi", lat: 11.170, lon: -1.150 },
    { name: "Bobo - Forêt Classée du Kou", lat: 11.180, lon: -4.290 },
  ];

  const handlePolygonImport = () => {
    try {
      setPolygonError(null);
      const parsed = JSON.parse(polygonCoords);
      let ring: number[][] = [];
      if (parsed.type === "Feature" && parsed.geometry?.coordinates) {
        ring = parsed.geometry.coordinates[0];
      } else if (parsed.type === "Polygon" && parsed.coordinates) {
        ring = parsed.coordinates[0];
      } else if (Array.isArray(parsed) && Array.isArray(parsed[0])) {
        ring = parsed;
      } else {
        throw new Error("Format GeoJSON ou liste de coordonnées non reconnu.");
      }

      if (ring.length < 3) throw new Error("Le polygone requiert au moins 3 points.");
      const lons = ring.map((pt) => pt[0]);
      const lats = ring.map((pt) => pt[1]);
      const cLon = lons.reduce((a, b) => a + b, 0) / lons.length;
      const cLat = lats.reduce((a, b) => a + b, 0) / lats.length;

      setCoord({ lat: Number(cLat.toFixed(4)), lon: Number(cLon.toFixed(4)) });
      setSiteName(`Périmètre Reboisement Importé (${ring.length} sommets)`);
    } catch (err: any) {
      setPolygonError(err.message || "Erreur de syntaxe JSON.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Simulation Header */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 mb-1">
              <Compass className="w-3.5 h-3.5" />
              Couche 4a & 4b • Modélisation Prédictive CMIP6 & biomod2
            </div>
            <h2 className="text-xl font-bold text-slate-900">
              Simulateur Cartographique « EcoPredict 2050–2080 »
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Évaluez l'aptitude climatique future des essences sahéliennes et générez un diagnostic décisionnel par clic GPS ou polygone de site.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Horizon Selector */}
            <div className="flex border rounded-xl p-1 bg-slate-50 text-xs font-bold text-slate-700">
              <button
                onClick={() => setHorizon("actuel")}
                className={`px-3 py-1.5 rounded-lg transition-all ${horizon === "actuel" ? "bg-white shadow text-slate-900" : "hover:text-slate-900"}`}
              >
                Actuel
              </button>
              <button
                onClick={() => setHorizon("2050")}
                className={`px-3 py-1.5 rounded-lg transition-all ${horizon === "2050" ? "bg-white shadow text-blue-800" : "hover:text-slate-900"}`}
              >
                Horizon 2050
              </button>
              <button
                onClick={() => setHorizon("2080")}
                className={`px-3 py-1.5 rounded-lg transition-all ${horizon === "2080" ? "bg-white shadow text-rose-800" : "hover:text-slate-900"}`}
              >
                Horizon 2080
              </button>
            </div>

            {/* Scenario Selector */}
            <div className="flex border rounded-xl p-1 bg-slate-50 text-xs font-bold text-slate-700">
              <button
                onClick={() => setScenario("ssp245")}
                className={`px-3 py-1.5 rounded-lg transition-all ${scenario === "ssp245" ? "bg-blue-600 text-white shadow" : "hover:text-slate-900"}`}
              >
                SSP2-4.5 (Intermédiaire)
              </button>
              <button
                onClick={() => setScenario("ssp585")}
                className={`px-3 py-1.5 rounded-lg transition-all ${scenario === "ssp585" ? "bg-rose-600 text-white shadow" : "hover:text-slate-900"}`}
              >
                SSP5-8.5 (Pessimiste)
              </button>
            </div>
          </div>
        </div>

        {/* Interactive Controls Bar */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 pt-4 text-xs">
          <div className="md:col-span-5">
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Espèce Cible (Modèle SDM / Niche Écologique) :
            </label>
            <select
              value={selectedSpecies}
              onChange={(e) => setSelectedSpecies(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border rounded-xl font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              {SPECIES_CATALOG.map((s) => (
                <option key={s.id} value={s.scientific_name}>
                  {s.scientific_name} ({s.vernacular_moore || s.family})
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-4">
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Couche Thématique Cartographique :
            </label>
            <select
              value={layerType}
              onChange={(e) => setLayerType(e.target.value as any)}
              className="w-full px-3 py-2 bg-slate-50 border rounded-xl font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="suitability">Aptitude Climatique Globale (Score 0-100)</option>
              <option value="contraction">Zones de Contraction & Refuges Climatiques</option>
              <option value="erosion">Indice d'Érosion Fonctionnelle (FEI)</option>
              <option value="bio12">Précipitations Annuelles (BIO12 mm/an)</option>
            </select>
          </div>

          <div className="md:col-span-3">
            <label className="block text-[11px] font-bold text-slate-600 mb-1">
              Sites Pilotes Prédéfinis :
            </label>
            <select
              onChange={(e) => {
                const site = presetSites.find((s) => s.name === e.target.value);
                if (site) {
                  setCoord({ lat: site.lat, lon: site.lon });
                  setSiteName(site.name);
                }
              }}
              className="w-full px-3 py-2 bg-slate-50 border rounded-xl font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="">Sélectionner un site...</option>
              {presetSites.map((s) => (
                <option key={s.name} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Map (Left) + Diagnostic Results (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Map Column */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-4 shadow-sm border border-slate-200 flex flex-col space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-600 px-1">
            <span className="font-semibold flex items-center gap-1.5 text-slate-800">
              <MapPin className="w-4 h-4 text-rose-600" />
              Cliquez n'importe où sur la carte pour diagnostiquer ce point GPS
            </span>
            <span className="text-[11px] text-slate-500">
              Point actif : <strong>{coord.lat}°N, {coord.lon}°E</strong>
            </span>
          </div>

          {/* Leaflet Map Box */}
          <div className="relative h-[480px] w-full rounded-xl overflow-hidden border border-slate-200">
            <div ref={mapContainerRef} className="w-full h-full" />

            {/* Map Legend Overlay */}
            <div className="absolute bottom-3 left-3 z-[400] bg-white/90 backdrop-blur-sm p-2.5 rounded-xl border border-slate-200 shadow-md text-[11px] space-y-1.5 max-w-[200px]">
              <span className="font-bold text-slate-800 block text-[10px] uppercase tracking-wide">
                Gradients Bioclimatiques (BF)
              </span>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-amber-400 border border-amber-600 flex-shrink-0" />
                <span className="text-slate-600">Sahélien (&gt;13.8°N)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-emerald-400 border border-emerald-600 flex-shrink-0" />
                <span className="text-slate-600">Soudano-Sahélien</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded bg-emerald-700 border border-emerald-900 flex-shrink-0" />
                <span className="text-slate-600">Soudanien (&lt;11.8°N)</span>
              </div>
            </div>
          </div>

          {/* Manual GPS & Polygon Drawer Accordion */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-700 flex items-center gap-1.5">
                <Upload className="w-3.5 h-3.5 text-slate-500" />
                Outil « Périmètre / Polygone de Reboisement » (GeoJSON / Shapefile)
              </span>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder='Ex: [[-0.095, 14.030], [-0.090, 14.030], [-0.090, 14.035], [-0.095, 14.035]]'
                value={polygonCoords}
                onChange={(e) => setPolygonCoords(e.target.value)}
                className="flex-1 text-[11px] px-3 py-1.5 bg-white border rounded-lg font-mono outline-none"
              />
              <button
                onClick={handlePolygonImport}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-lg font-semibold text-[11px]"
              >
                Diagnostiquer Périmètre
              </button>
            </div>
            {polygonError && <span className="text-[11px] text-rose-600">{polygonError}</span>}
          </div>
        </div>

        {/* Diagnosis & Decision Support Column */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 space-y-4">
            {/* Header of Diagnostic */}
            <div className="flex items-start justify-between pb-3 border-b">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                  Rapport Décisionnel Instantané
                </span>
                <h3 className="text-base font-bold text-slate-900">{siteName}</h3>
                <div className="text-xs text-slate-500 mt-0.5">
                  Zone Bioclimatique :{" "}
                  <strong className="text-savanna-900">
                    {diagnosticResult?.climate_diagnostic?.zone || "En analyse..."}
                  </strong>
                </div>
              </div>

              <div className="text-right">
                <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-blue-100 text-blue-800 uppercase">
                  {horizon.toUpperCase()} • {scenario.toUpperCase()}
                </span>
              </div>
            </div>

            {/* Climate Projections Summary Cards */}
            {diagnosticResult && (
              <div className="grid grid-cols-2 gap-2.5 text-xs">
                <div className="p-2.5 bg-blue-50/70 rounded-xl border border-blue-200">
                  <span className="text-slate-500 text-[10px] block font-medium">Pluviométrie Annuelle (BIO12)</span>
                  <div className="text-base font-bold text-blue-900">
                    {diagnosticResult.climate_diagnostic.future_precip_mm} mm/an
                  </div>
                  <span className="text-[10px] text-slate-500">
                    Base: {diagnosticResult.climate_diagnostic.base_precip_mm} mm ({diagnosticResult.climate_diagnostic.delta_precip_pct}%)
                  </span>
                </div>

                <div className="p-2.5 bg-rose-50/70 rounded-xl border border-rose-200">
                  <span className="text-slate-500 text-[10px] block font-medium">Température Moyenne (BIO1)</span>
                  <div className="text-base font-bold text-rose-900">
                    {diagnosticResult.climate_diagnostic.future_temp_c} °C
                  </div>
                  <span className="text-[10px] text-slate-500">
                    Anomalie : +{diagnosticResult.climate_diagnostic.delta_temp_c} °C
                  </span>
                </div>

                <div className="p-2.5 bg-amber-50/70 rounded-xl border border-amber-200 col-span-2 flex items-center justify-between">
                  <div>
                    <span className="text-slate-500 text-[10px] block font-medium">Indice d'Aridité (P / PET)</span>
                    <strong className="text-sm font-bold text-amber-900">
                      {diagnosticResult.climate_diagnostic.aridity_index} (UNEP / CGIAR)
                    </strong>
                  </div>
                  <span className="text-[11px] text-amber-800 font-semibold px-2 py-0.5 rounded bg-amber-100">
                    {diagnosticResult.climate_diagnostic.aridity_index < 0.25 ? "Aride" : "Semi-Aride"}
                  </span>
                </div>
              </div>
            )}

            {/* Species Recommendations Ranking */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-800 uppercase tracking-wide">
                  Matrice d'Aptitude des Espèces :
                </span>
                <span className="text-[11px] text-slate-500">
                  {diagnosticResult?.summary?.recommended_count || 0} recommandées
                </span>
              </div>

              <div className="max-h-[340px] overflow-y-auto space-y-2 pr-1">
                {diagnosticResult?.species_ranking?.map((sp: any, idx: number) => {
                  const isTop = sp.survival_score >= 75;
                  const isModerate = sp.survival_score >= 50 && sp.survival_score < 75;
                  const isRisk = sp.survival_score < 50;

                  return (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl border transition-all text-xs ${
                        isTop
                          ? "bg-emerald-50/70 border-emerald-300"
                          : isModerate
                          ? "bg-amber-50/70 border-amber-200"
                          : "bg-rose-50/70 border-rose-200"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-bold italic text-slate-900">{sp.scientific_name}</div>
                          <div className="text-[11px] text-slate-500">
                            {sp.vernacular_moore ? `Mooré: ${sp.vernacular_moore}` : sp.family} • {sp.functional_group}
                          </div>
                        </div>
                        <div className="text-right">
                          <span
                            className={`text-sm font-extrabold ${
                              isTop ? "text-emerald-700" : isModerate ? "text-amber-700" : "text-rose-700"
                            }`}
                          >
                            {sp.survival_score}%
                          </span>
                          <span className="block text-[9px] uppercase font-bold text-slate-500">
                            Survie
                          </span>
                        </div>
                      </div>

                      <div className="mt-1.5 flex items-center gap-1.5 text-[11px]">
                        {isTop && <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />}
                        {isRisk && <AlertTriangle className="w-3.5 h-3.5 text-rose-600 flex-shrink-0" />}
                        <span className="font-semibold text-slate-700">{sp.recommendation}</span>
                      </div>

                      <p className="mt-1 text-[10px] text-slate-600 italic">
                        {sp.rationale}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Quick Export Diagnostic */}
            <div className="pt-2 border-t">
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(diagnosticResult, null, 2)], {
                    type: "application/json",
                  });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `ecopredict_diagnostic_${coord.lat}_${coord.lon}_${horizon}_${scenario}.json`;
                  a.click();
                }}
                className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs flex items-center justify-center gap-2 transition-colors"
              >
                <FileText className="w-4 h-4 text-slate-500" />
                Exporter ce Rapport Décisionnel (Format JSON / MEEA)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
