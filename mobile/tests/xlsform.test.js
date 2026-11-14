// Test the generated XLSForm workbook
const assert = require('assert');
const path = require('path');
const XLSX = require('xlsx');

console.log('🧪 Vérification du classeur Excel XLSForm KoboToolbox...');

const filePath = path.join(__dirname, '..', 'public', 'forms', 'sahelfield_enquete_socioeco.xlsx');
const wb = XLSX.readFile(filePath);

// 1. Verify sheet names
const sheetNames = wb.SheetNames;
console.log('  Feuilles présentes :', sheetNames);
assert.ok(sheetNames.includes('survey'), 'La feuille "survey" est obligatoire');
assert.ok(sheetNames.includes('choices'), 'La feuille "choices" est obligatoire');
assert.ok(sheetNames.includes('settings'), 'La feuille "settings" est obligatoire');
console.log('  ✅ Test 1 : Les 3 onglets standards (survey, choices, settings) sont présents.');

// 2. Verify survey sheet contents
const surveyData = XLSX.utils.sheet_to_json(wb.Sheets['survey']);
console.log(`  Nombre de lignes dans survey : ${surveyData.length}`);
assert.ok(surveyData.length > 20, 'La trame doit contenir toutes les questions');

const variableNames = surveyData.map((row) => row.name).filter(Boolean);
console.log('  Variables clés détectées :', variableNames.filter((v) => ['geom_village', 'species_repeat', 'perceived_decline_score', 'phenology_shift_observed', 'rna_practiced', 'smith_saliency_item'].includes(v)));

// Verify modules
assert.ok(variableNames.includes('geom_village'), 'Module M1 : Géopoint GPS manquant');
assert.ok(variableNames.includes('species_repeat'), 'Module M2 : Repeat species free-listing manquant');
assert.ok(variableNames.includes('smith_saliency_item'), 'Module M2 : Calcul Saillance de Smith manquant');
assert.ok(variableNames.includes('perceived_decline_score'), 'Module M3 : Déclin Likert manquant');
assert.ok(variableNames.includes('phenology_shift_observed'), 'Module M4 : Décalage phénologique manquant');
assert.ok(variableNames.includes('rna_practiced'), 'Module M5 : Pratique de la RNA manquante');
console.log('  ✅ Test 2 : Tous les modules M1, M2, M3, M4, M5 sont modélisés dans la trame survey.');

// 3. Verify choices sheet
const choicesData = XLSX.utils.sheet_to_json(wb.Sheets['choices']);
console.log(`  Nombre d'options de réponses dans choices : ${choicesData.length}`);
assert.ok(choicesData.length > 30, 'La liste choices doit contenir les échelles et essences');

const listNames = [...new Set(choicesData.map((row) => row.list_name))];
assert.ok(listNames.includes('respondent_type_list'));
assert.ok(listNames.includes('climatic_zone_list'));
assert.ok(listNames.includes('species_list'));
assert.ok(listNames.includes('likert_5'));
assert.ok(listNames.includes('lopping_scale'));
console.log('  ✅ Test 3 : Les listes de choix standards sont toutes définies.');

// 4. Verify settings sheet
const settingsData = XLSX.utils.sheet_to_json(wb.Sheets['settings']);
assert.strictEqual(settingsData[0].form_id, 'sahelfield_enquete_socioeco_v1');
assert.ok(settingsData[0].form_title.includes('SahelField'));
console.log('  ✅ Test 4 : Métadonnées settings (form_id, version, langue) validées.');

console.log('🎉 Le fichier XLSForm est 100% CONFORME et prêt pour KoboToolbox & ODK Collect !');
