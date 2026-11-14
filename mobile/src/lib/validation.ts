// SahelField - Système de validation temps réel des données de terrain et laboratoire

import { findTaxonById } from './taxaData';

export interface ValidationResult {
  isValid: boolean;
  isWarning: boolean;
  message: string;
}

export function validateDBH(dbh: number): ValidationResult {
  if (dbh === undefined || dbh === null || isNaN(dbh)) {
    return { isValid: false, isWarning: false, message: 'Le DHP est obligatoire.' };
  }
  if (dbh < 0) {
    return { isValid: false, isWarning: false, message: 'Le DHP ne peut pas être négatif.' };
  }
  if (dbh < 5) {
    return {
      isValid: false,
      isWarning: true,
      message: 'DHP < 5 cm : Les tiges < 5 cm relèvent des sous-placettes de régénération (5m × 5m).',
    };
  }
  if (dbh > 400) {
    return {
      isValid: true,
      isWarning: true,
      message: 'Attention : DHP exceptionnellement grand (> 400 cm). Vérifier s\'il s\'agit d\'un baobab adulte.',
    };
  }
  return { isValid: true, isWarning: false, message: 'DHP valide.' };
}

export function validateTreeHeight(height: number): ValidationResult {
  if (height === undefined || height === null || isNaN(height)) {
    return { isValid: false, isWarning: false, message: 'La hauteur est obligatoire.' };
  }
  if (height <= 0) {
    return { isValid: false, isWarning: false, message: 'La hauteur totale doit être strictement positive.' };
  }
  if (height > 35) {
    return {
      isValid: true,
      isWarning: true,
      message: 'Attention : Hauteur > 35 m rare en zone sahélienne/soudanienne.',
    };
  }
  return { isValid: true, isWarning: false, message: 'Hauteur valide.' };
}

export function validateLeafMasses(freshMassMg: number, dryMassMg: number): ValidationResult {
  if (freshMassMg !== undefined && dryMassMg !== undefined && freshMassMg > 0 && dryMassMg > 0) {
    if (dryMassMg > freshMassMg) {
      return {
        isValid: false,
        isWarning: false,
        message: 'BLOCAGE : La masse sèche (' + dryMassMg + ' mg) ne peut pas dépasser la masse fraîche saturée (' + freshMassMg + ' mg) !',
      };
    }
    if (dryMassMg / freshMassMg > 0.85) {
      return {
        isValid: true,
        isWarning: true,
        message: 'Alerte : Rapport masse sèche / masse fraîche inhabituellement élevé (> 85%). Vérifier réhydratation.',
      };
    }
  }
  return { isValid: true, isWarning: false, message: 'Masses foliaires cohérentes.' };
}

export function validateTraitOutlier3Sigma(taxonId: string, traitName: string, value: number): ValidationResult {
  const taxon = findTaxonById(taxonId);
  if (!taxon || value === undefined || value === null || isNaN(value)) {
    return { isValid: true, isWarning: false, message: 'Trait enregistré.' };
  }

  if (traitName === 'SLA' && taxon.typical_sla_mean && taxon.typical_sla_sd) {
    const mean = taxon.typical_sla_mean;
    const sd = taxon.typical_sla_sd;
    const diff = Math.abs(value - mean);
    if (diff > 3 * sd) {
      return {
        isValid: true,
        isWarning: true,
        message: `ALERTE 3-SIGMA : Valeur SLA (${value.toFixed(2)} mm²/mg) hors intervalle de confiance 3σ [${(mean - 3 * sd).toFixed(2)} - ${(mean + 3 * sd).toFixed(2)}]. Le backend marquera cette mesure comme SUSPECT_OUTLIER_3SIGMA.`,
      };
    }
  }

  if (traitName === 'Wood_density' && taxon.typical_wood_density_mean) {
    if (value < 0.1 || value > 1.4) {
      return {
        isValid: true,
        isWarning: true,
        message: `ALERTE : Densité du bois (${value.toFixed(2)} g/cm³) atypique pour les ligneux sahéliens.`,
      };
    }
  }

  return { isValid: true, isWarning: false, message: 'Mesure conforme aux distributions écologiques.' };
}

export function validateSoilTexture(clay: number, silt: number, sand: number): ValidationResult {
  const sum = clay + silt + sand;
  if (Math.abs(sum - 100) > 2) {
    return {
      isValid: false,
      isWarning: true,
      message: `Attention : La somme des fractions granulométriques (Argile ${clay}% + Limon ${silt}% + Sable ${sand}% = ${sum.toFixed(1)}%) doit être égale à 100% ± 2%.`,
    };
  }
  return { isValid: true, isWarning: false, message: 'Granulométrie valide.' };
}

export function getGPSQualityBadge(accuracyMeters?: number): {
  color: string;
  label: string;
  isHighPrecision: boolean;
} {
  if (accuracyMeters === undefined || accuracyMeters === null) {
    return { color: 'bg-zinc-700 text-zinc-300', label: 'GPS Inactif', isHighPrecision: false };
  }
  if (accuracyMeters <= 5.0) {
    return { color: 'bg-emerald-600 text-white', label: `GPS Haute Précision (${accuracyMeters.toFixed(1)}m < 5m)`, isHighPrecision: true };
  }
  if (accuracyMeters <= 10.0) {
    return { color: 'bg-amber-600 text-white', label: `GPS Acceptable (${accuracyMeters.toFixed(1)}m)`, isHighPrecision: false };
  }
  return { color: 'bg-red-600 text-white', label: `GPS Faible Précision (${accuracyMeters.toFixed(1)}m > 10m)`, isHighPrecision: false };
}
