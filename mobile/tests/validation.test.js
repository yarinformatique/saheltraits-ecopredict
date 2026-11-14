// Validation Test Suite for SahelField Mobile Rules
const assert = require('assert');

// 1. DHP Validation Logic
function validateDBH(dbh) {
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
  return { isValid: true, isWarning: false, message: 'DHP valide.' };
}

// 2. Leaf Dry Mass vs Fresh Mass Biological Rule
function validateLeafMasses(freshMassMg, dryMassMg) {
  if (freshMassMg !== undefined && dryMassMg !== undefined && freshMassMg > 0 && dryMassMg > 0) {
    if (dryMassMg > freshMassMg) {
      return {
        isValid: false,
        isWarning: false,
        message: 'BLOCAGE : La masse sèche (' + dryMassMg + ' mg) ne peut pas dépasser la masse fraîche saturée (' + freshMassMg + ' mg) !',
      };
    }
  }
  return { isValid: true, isWarning: false, message: 'Masses foliaires cohérentes.' };
}

// 3. 3-Sigma Statistical Outlier Rule (Balanites SLA mean=9.9, sd=0.6)
function validate3SigmaSLA(value, mean = 9.9, sd = 0.6) {
  const diff = Math.abs(value - mean);
  if (diff > 3 * sd) {
    return {
      isOutlier: true,
      flag: 'SUSPECT_OUTLIER_3SIGMA',
      bounds: [mean - 3 * sd, mean + 3 * sd],
    };
  }
  return { isOutlier: false, flag: 'VALID', bounds: [mean - 3 * sd, mean + 3 * sd] };
}

// 4. Smith's Saliency Formula S = (L - r + 1) / L
function computeSmithSaliency(listLength, rank) {
  return (listLength - rank + 1) / listLength;
}

// 5. Soil texture sum rule
function validateSoilTexture(clay, silt, sand) {
  const sum = clay + silt + sand;
  return Math.abs(sum - 100) <= 2;
}

console.log('🧪 Exécution de la suite de tests unitaires SahelField...');

// Test 1: DHP validations
assert.strictEqual(validateDBH(-5).isValid, false, 'DHP négatif doit être invalide');
assert.strictEqual(validateDBH(3.2).isValid, false, 'DHP < 5cm doit être bloqué');
assert.strictEqual(validateDBH(28.4).isValid, true, 'DHP >= 5cm doit être valide');
console.log('  ✅ Test 1 : Règles dendrométriques DHP réussies.');

// Test 2: Leaf biological constraint
const invalidLeaf = validateLeafMasses(150, 180);
assert.strictEqual(invalidLeaf.isValid, false, 'Masse sèche > Masse fraîche doit être bloquée');
assert.ok(invalidLeaf.message.includes('BLOCAGE'), 'Message de blocage requis');
const validLeaf = validateLeafMasses(250, 95);
assert.strictEqual(validLeaf.isValid, true, 'Masse sèche < Masse fraîche doit être acceptée');
console.log('  ✅ Test 2 : Règle biologique foliaire (Masse sèche < Masse fraîche) réussie.');

// Test 3: 3-Sigma detection
const normalSla = validate3SigmaSLA(10.2);
assert.strictEqual(normalSla.isOutlier, false);
assert.strictEqual(normalSla.flag, 'VALID');

const outlierSla = validate3SigmaSLA(28.5); // Way beyond 9.9 + 3*0.6 = 11.7
assert.strictEqual(outlierSla.isOutlier, true);
assert.strictEqual(outlierSla.flag, 'SUSPECT_OUTLIER_3SIGMA');
console.log('  ✅ Test 3 : Détection statistique temps réel des 3-sigmas réussie.');

// Test 4: Smith's Saliency calculation
const L = 5;
assert.strictEqual(computeSmithSaliency(L, 1), 1.0, 'Rang 1 pour L=5 doit avoir S=1.0');
assert.strictEqual(computeSmithSaliency(L, 5), 0.2, 'Rang 5 pour L=5 doit avoir S=0.2');
console.log('  ✅ Test 4 : Calcul de l\'Indice de Saillance de Smith réussi.');

// Test 5: Soil texture
assert.strictEqual(validateSoilTexture(12.5, 18.0, 69.5), true, 'Texture somme 100% doit être valide');
assert.strictEqual(validateSoilTexture(10, 10, 10), false, 'Texture somme 30% doit être rejetée');
console.log('  ✅ Test 5 : Règle de cohérence granulométrique du sol réussie.');

console.log('🎉 Tous les tests de validation métier sont VALIDÉS !');
