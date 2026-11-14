import { SPECIES_CATALOG, SpeciesInfo } from "@/data/speciesData";
import { SURVEY_VILLAGES, SURVEYS_SUMMARY } from "@/data/surveysData";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api/v1";

export async function fetchTaxaFromBackend(search?: string, family?: string): Promise<any[]> {
  try {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (family) params.append("family", family);
    const res = await fetch(`${BACKEND_URL}/taxonomy?${params.toString()}`, { cache: "no-store" });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Graceful fallback on local catalog
  }
  let filtered = [...SPECIES_CATALOG];
  if (search) {
    const q = search.toLowerCase();
    filtered = filtered.filter(
      (s) =>
        s.scientific_name.toLowerCase().includes(q) ||
        s.vernacular_moore.toLowerCase().includes(q) ||
        s.vernacular_dioula.toLowerCase().includes(q) ||
        s.vernacular_fulfulde.toLowerCase().includes(q)
    );
  }
  if (family) {
    filtered = filtered.filter((s) => s.family === family);
  }
  return filtered;
}

export async function fetchPointDiagnosis(lat: number, lon: number, horizon: string, scenario: string): Promise<any> {
  try {
    const res = await fetch(`${BACKEND_URL}/ecopredict/diagnose-point`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ latitude: lat, longitude: lon, horizon, scenario }),
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (e) {
    // Fallback calculation directly in client
  }

  // Client-side simulation fallback
  const latFactor = Math.max(0.0, Math.min(1.0, (15.2 - lat) / 5.2));
  const basePrecip = 350.0 + latFactor * 750.0 - Math.abs(lon + 1.5) * 15.0;
  const baseTemp = 30.5 - latFactor * 3.5;

  let deltaT = 0.0;
  let deltaP = 0.0;
  if (horizon === "2050") {
    deltaT = scenario === "ssp245" ? 1.6 : 2.4;
    deltaP = scenario === "ssp245" ? -4.5 : -9.2;
  } else if (horizon === "2080") {
    deltaT = scenario === "ssp245" ? 2.2 : 4.3;
    deltaP = scenario === "ssp245" ? -7.0 : -18.5;
  }

  const futTemp = Number((baseTemp + deltaT).toFixed(2));
  const futPrecip = Number((basePrecip * (1.0 + deltaP / 100.0)).toFixed(1));
  const pet = Math.max(1200.0, 1400.0 + (futTemp - 26.0) * 85.0);
  const aridity = Number((futPrecip / pet).toFixed(3));

  let zone = "Soudanienne";
  if (lat >= 13.8) zone = "Sahélienne";
  else if (lat >= 11.8) zone = "Soudano-Sahélienne";

  const rankings = SPECIES_CATALOG.map((sp) => {
    let score = 70.0;
    if (zone === "Sahélienne") {
      score = sp.traits.drought_index * 0.95;
    } else if (zone === "Soudano-Sahélienne") {
      score = (sp.traits.drought_index * 0.6) + (sp.traits.fire_resistance * 0.4);
    } else {
      score = (sp.traits.fire_resistance * 0.6) + (sp.traits.drought_index * 0.4);
    }
    if (horizon !== "actuel") {
      const scenKey = `${scenario}_${horizon}` as keyof typeof sp.projections;
      const proj = sp.projections[scenKey];
      if (proj) score = score * (1.0 - (proj.vuln_idx / 200.0));
    }
    score = Math.max(10, Math.min(99, Math.round(score)));

    let category = "Favorable / Tolérante";
    let rec = "Adaptée sous suivi hydrique";
    if (score >= 75) {
      category = "Hautement Recommandée";
      rec = "Prioritaire pour reboisement";
    } else if (score < 50) {
      category = "À Haut Risque / Maladaptée";
      rec = "Non recommandée dans cette zone sous ce scénario";
    }

    return {
      scientific_name: sp.scientific_name,
      family: sp.family,
      vernacular_moore: sp.vernacular_moore,
      vernacular_dioula: sp.vernacular_dioula,
      vernacular_fulfulde: sp.vernacular_fulfulde,
      functional_group: sp.functional_group,
      survival_score: score,
      category,
      recommendation: rec,
      rationale: sp.description,
      drought_tolerance: sp.traits.drought_index / 100,
      fire_tolerance: sp.traits.fire_resistance / 100,
    };
  }).sort((a, b) => b.survival_score - a.survival_score);

  return {
    query: { latitude: lat, longitude: lon, horizon, scenario },
    climate_diagnostic: {
      zone,
      base_temp_c: Number(baseTemp.toFixed(2)),
      base_precip_mm: Number(basePrecip.toFixed(1)),
      future_temp_c: futTemp,
      future_precip_mm: futPrecip,
      delta_temp_c: deltaT,
      delta_precip_pct: deltaP,
      pet_mm: Number(pet.toFixed(1)),
      aridity_index: aridity,
    },
    species_ranking: rankings,
    summary: {
      total_evaluated: rankings.length,
      recommended_count: rankings.filter((s) => s.survival_score >= 75).length,
      moderate_count: rankings.filter((s) => s.survival_score >= 50 && s.survival_score < 75).length,
      at_risk_count: rankings.filter((s) => s.survival_score < 50).length,
      top_choice: rankings[0]?.scientific_name,
    },
  };
}
