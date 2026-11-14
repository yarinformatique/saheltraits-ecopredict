'use client';

import React, { useState } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { db } from '@/lib/db';
import { EthnoSurvey, ClimaticZone, RespondentType } from '@/types';
import GPSWidget from '@/components/GPSWidget';
import { SAHEL_TAXA, searchTaxa } from '@/lib/taxaData';
import { speechService } from '@/lib/speechFeedback';
import { generateXLSFormWorkbook } from '@/lib/xlsformGenerator';
import {
  ClipboardList,
  Plus,
  Download,
  CheckCircle2,
  Users,
  Award,
  Calendar,
  Sparkles,
  HelpCircle,
  FileSpreadsheet,
  Clock,
  ExternalLink,
} from 'lucide-react';

export default function SurveysPage() {
  const [activeTab, setActiveTab] = useState<'form' | 'xlsform' | 'list'>('form');

  // M1 Form state
  const [interviewerId, setInterviewerId] = useState<string>('ENQ-01 / Moussa SAWADOGO');
  const [respondentType, setRespondentType] = useState<RespondentType>('Local');
  const [villageName, setVillageName] = useState<string>('Yakouta (Dori)');
  const [climaticZone, setClimaticZone] = useState<ClimaticZone>('Sahélienne');
  const [lat, setLat] = useState<number>(14.0250);
  const [lng, setLng] = useState<number>(-0.0880);
  const [respondentProfile, setRespondentProfile] = useState<string>('Agropasteur (mixte)');
  const [seniorityYears, setSeniorityYears] = useState<string>('35');

  // M2 Free-Listing states (dynamic list of 1 to 10 species)
  const [citedTaxa, setCitedTaxa] = useState<Array<{
    taxon_id: string;
    scientific_name: string;
    vernacular_name: string;
    primary_use: string;
  }>>([
    {
      taxon_id: 'b0000000-0000-0000-0000-000000000001',
      scientific_name: 'Balanites aegyptiaca (L.) Delile',
      vernacular_name: 'Kieglga / Murtooki',
      primary_use: 'Alimentation & Fourrage',
    },
    {
      taxon_id: 'b0000000-0000-0000-0000-000000000003',
      scientific_name: 'Faidherbia albida (Delile) A.Chev.',
      vernacular_name: 'Zaanga / Caski',
      primary_use: 'Agroforesterie & Fertilité du sol',
    },
    {
      taxon_id: 'b0000000-0000-0000-0000-000000000004',
      scientific_name: 'Vachellia tortilis (Forssk.) Galasso & Banfi',
      vernacular_name: 'Gom-peelga / Cilluki',
      primary_use: 'Fourrage aérien gousses',
    },
  ]);

  const [addTaxonId, setAddTaxonId] = useState<string>(SAHEL_TAXA[1].taxon_id);
  const [addTaxonSearch, setAddTaxonSearch] = useState<string>('');
  const [addPrimaryUse, setAddPrimaryUse] = useState<string>('Alimentation humaine & PFNL');

  // M3 Diagnostic & Déclin (-2 to +2)
  const [perceivedDecline, setPerceivedDecline] = useState<number>(0);
  const [diebackSeverity, setDiebackSeverity] = useState<number>(-1);
  const [parasitePressure, setParasitePressure] = useState<number>(1);

  // M4 Phénologie
  const [phenologyShiftObserved, setPhenologyShiftObserved] = useState<boolean>(true);
  const [floweringShift, setFloweringShift] = useState<number>(1);
  const [fruitingShift, setFruitingShift] = useState<number>(1);
  const [phenologyDetails, setPhenologyDetails] = useState<string>(
    'Floraison décalée de 3 semaines après les premières pluies utiles'
  );

  // M5 Pressions & RNA
  const [loppingIntensity, setLoppingIntensity] = useState<number>(2);
  const [fireFrequency, setFireFrequency] = useState<string>('Tous les 2 à 3 ans');
  const [rnaPracticed, setRnaPracticed] = useState<boolean>(true);
  const [rnaTechniques, setRnaTechniques] = useState<string>(
    'Protection des rejets, taille de formation, zaï autour des semenciers'
  );
  const [droughtResilienceRank, setDroughtResilienceRank] = useState<number>(1);
  const [traditionalUses, setTraditionalUses] = useState<string>(
    'Huile cosmétique et médicinale de Kieglga, fruits consommés en période de soudure, bois d\'œuvre'
  );

  // Queries
  const surveys = useLiveQuery(() => db.surveys.orderBy('created_at').reverse().toArray(), [], []);

  // Compute Smith's Saliency for current list: S = (L - r + 1) / L
  const L = citedTaxa.length;

  const handleAddCitedTaxon = () => {
    if (citedTaxa.length >= 10) {
      alert('Maximum 10 espèces pour le module free-listing.');
      return;
    }
    const t = SAHEL_TAXA.find((x) => x.taxon_id === addTaxonId);
    if (!t) return;
    setCitedTaxa([
      ...citedTaxa,
      {
        taxon_id: t.taxon_id,
        scientific_name: t.scientific_name,
        vernacular_name: `${t.vernacular_moore} / ${t.vernacular_dioula} / ${t.vernacular_fulfulde}`,
        primary_use: addPrimaryUse,
      },
    ]);
  };

  const handleRemoveCitedTaxon = (index: number) => {
    setCitedTaxa(citedTaxa.filter((_, i) => i !== index));
  };

  const handleSaveSurvey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (citedTaxa.length === 0) {
      alert('Veuillez citer au moins une espèce végétale dans le Module M2.');
      return;
    }

    const now = new Date().toISOString();

    // Create survey record for each cited taxon with its Smith's Saliency rank
    const newSurveys: EthnoSurvey[] = citedTaxa.map((item, idx) => ({
      survey_id: `SURV-${Date.now()}-${idx + 1}`,
      taxon_id: item.taxon_id,
      scientific_name: item.scientific_name,
      vernacular_name: item.vernacular_name,
      respondent_type: respondentType,
      respondent_profile: respondentProfile,
      respondent_seniority_years: parseInt(seniorityYears) || 0,
      village_name: villageName,
      geom_village: {
        type: 'Point',
        coordinates: [lng, lat],
      },
      latitude: lat,
      longitude: lng,
      climatic_zone: climaticZone,
      perceived_decline_score: perceivedDecline,
      phenology_shift_observed: phenologyShiftObserved,
      phenology_shift_details: phenologyDetails,
      phenology_flowering_shift: floweringShift,
      phenology_fruiting_shift: fruitingShift,
      drought_resilience_rank: droughtResilienceRank,
      traditional_uses: traditionalUses,
      lopping_intensity: loppingIntensity,
      fire_frequency: fireFrequency,
      rna_practiced: rnaPracticed,
      rna_techniques: rnaTechniques,
      smith_saliency_rank: idx + 1, // rank 1..L
      interviewer_id: interviewerId,
      created_at: now,
      sync_status: 'PENDING',
    }));

    await db.surveys.bulkAdd(newSurveys);
    speechService.speak(`Enquête auprès de ${villageName} enregistrée pour ${citedTaxa.length} espèces.`);
    alert(`Enquête enregistrée avec succès (${newSurveys.length} fiches espèces prêtes pour synchronisation SahelTraits-DB).`);
    setActiveTab('list');
  };

  const handleDownloadXLSForm = () => {
    const bytes = generateXLSFormWorkbook();
    const blob = new Blob([bytes], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sahelfield_enquete_socioeco.xlsx';
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredTaxa = searchTaxa(addTaxonSearch);

  // Respondent statistics
  const countExperts = surveys.filter((s) => s.respondent_type === 'Expert').length;
  const countLocals = surveys.filter((s) => s.respondent_type === 'Local').length;

  return (
    <div className="space-y-4 animate-fade-in pb-12">
      {/* Header */}
      <div>
        <h1 className="text-lg font-black text-white flex items-center">
          <ClipboardList className="w-5 h-5 mr-1.5 text-emerald-400" /> Module Enquêtes Socio-Écologiques
        </h1>
        <p className="text-xs text-zinc-400">
          Volet A (150 Experts) & Volet B (300 Riverains) • Modules M1 à M5 & Indice de Smith
        </p>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-3 gap-1 rounded-xl bg-zinc-900 p-1 border border-zinc-800 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('form')}
          className={`py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'form'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Plus className="w-4 h-4" />
          <span>Saisie M1–M5</span>
        </button>
        <button
          onClick={() => setActiveTab('xlsform')}
          className={`py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'xlsform'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Trame XLSForm</span>
        </button>
        <button
          onClick={() => setActiveTab('list')}
          className={`py-2 rounded-lg flex items-center justify-center space-x-1.5 transition ${
            activeTab === 'list'
              ? 'bg-savanna-800 text-emerald-300 font-bold shadow'
              : 'text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Enquêtes ({surveys.length})</span>
        </button>
      </div>

      {/* TAB 1: FORMULAIRE IN-APP M1 À M5 */}
      {activeTab === 'form' && (
        <form onSubmit={handleSaveSurvey} className="space-y-4 text-xs">
          {/* M1 : ANCRAGE GÉOGRAPHIQUE */}
          <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3 shadow-md">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
              <span className="w-6 h-6 rounded-full bg-savanna-950 border border-savanna-700 flex items-center justify-center text-xs">
                M1
              </span>
              <span>Module M1 : Ancrage Géographique & Profil Répondant</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-zinc-400 block mb-1">ENQUÊTEUR TERRAIN</label>
                <input
                  type="text"
                  value={interviewerId}
                  onChange={(e) => setInterviewerId(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                />
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">VOLET D'ENQUÊTE *</label>
                <select
                  value={respondentType}
                  onChange={(e) => setRespondentType(e.target.value as RespondentType)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-bold"
                >
                  <option value="Local">Volet B : 300 Riverains Locaux (Terrain)</option>
                  <option value="Expert">Volet A : 150 Experts (Gestionnaires / Chercheurs)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-zinc-400 block mb-1">TERROIR / VILLAGE *</label>
                <input
                  type="text"
                  required
                  value={villageName}
                  onChange={(e) => setVillageName(e.target.value)}
                  placeholder="Ex: Yakouta, Dem, Pô..."
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                />
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">ZONE BIOCLIMATIQUE *</label>
                <select
                  value={climaticZone}
                  onChange={(e) => setClimaticZone(e.target.value as ClimaticZone)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  <option value="Sahélienne">Sahélienne (&lt;600mm)</option>
                  <option value="Soudano-Sahélienne">Soudano-Sahélienne (600-900mm)</option>
                  <option value="Soudanienne">Soudanienne (&gt;900mm)</option>
                </select>
              </div>
            </div>

            <GPSWidget
              initialCoords={{ lat, lng }}
              onCapture={(c) => {
                setLat(c.lat);
                setLng(c.lng);
              }}
            />

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-zinc-400 block mb-1">PROFIL DU RÉPONDANT</label>
                <select
                  value={respondentProfile}
                  onChange={(e) => setRespondentProfile(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  <option value="Agriculteur exploitant">Agriculteur exploitant</option>
                  <option value="Éleveur transhumant / Pasteur">Éleveur transhumant</option>
                  <option value="Agropasteur (mixte)">Agropasteur (mixte)</option>
                  <option value="Tradithérapeute / Tradipraticien">Tradithérapeute</option>
                  <option value="Chef coutumier / Chef de terre">Chef coutumier</option>
                  <option value="Agent des Eaux et Forêts">Agent des Eaux et Forêts</option>
                  <option value="Chercheur / Universitaire">Chercheur / Universitaire</option>
                </select>
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">ANCIENNETÉ (ANNÉES)</label>
                <input
                  type="number"
                  min="0"
                  max="120"
                  value={seniorityYears}
                  onChange={(e) => setSeniorityYears(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-bold"
                />
              </div>
            </div>
          </div>

          {/* M2 : FREE-LISTING & SMITH SALIENCY */}
          <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3 shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                <span className="w-6 h-6 rounded-full bg-savanna-950 border border-savanna-700 flex items-center justify-center text-xs">
                  M2
                </span>
                <span>Module M2 : Free-Listing Ethnobotanique ({citedTaxa.length}/10 espèces)</span>
              </div>
              <span className="text-[10px] text-zinc-400 font-mono">
                Indice de Saillance de Smith
              </span>
            </div>

            <p className="text-[11px] text-zinc-300 italic">
              Énumération libre et ordonnée des essences les plus importantes. Le calcul automatique du rang r et du score de Smith (S = (L - r + 1) / L) s&apos;effectue en temps réel.
            </p>

            {/* Cited taxa list */}
            <div className="space-y-1.5">
              {citedTaxa.map((item, idx) => {
                const rank = idx + 1;
                const saliency = (L - rank + 1) / L;
                return (
                  <div
                    key={item.taxon_id + idx}
                    className="flex items-center justify-between bg-zinc-950 p-2 rounded-xl border border-zinc-800 text-xs"
                  >
                    <div className="flex items-center space-x-2.5">
                      <span className="w-6 h-6 rounded-full bg-emerald-950 border border-emerald-700 text-emerald-300 font-bold flex items-center justify-center text-[11px]">
                        #{rank}
                      </span>
                      <div>
                        <span className="font-bold text-zinc-100">{item.scientific_name}</span>
                        <div className="text-[10px] text-zinc-400">
                          {item.vernacular_name} • <span className="text-zinc-300">{item.primary_use}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-emerald-400 text-[11px] bg-savanna-950 px-2 py-0.5 rounded border border-savanna-800 font-bold">
                        S = {saliency.toFixed(2)}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveCitedTaxon(idx)}
                        className="text-red-400 hover:text-red-300 px-1 font-bold text-sm"
                        title="Retirer"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add species */}
            {citedTaxa.length < 10 && (
              <div className="p-2.5 bg-zinc-950 rounded-xl border border-zinc-800 space-y-2">
                <span className="text-[10px] font-bold text-zinc-400 uppercase">
                  Ajouter l'espèce suivante citée au rang #{citedTaxa.length + 1} :
                </span>
                <input
                  type="text"
                  placeholder="Rechercher par nom Mooré, Dioula, Fulfuldé ou latin..."
                  value={addTaxonSearch}
                  onChange={(e) => setAddTaxonSearch(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                />
                <select
                  value={addTaxonId}
                  onChange={(e) => setAddTaxonId(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  {filteredTaxa.map((t) => (
                    <option key={t.taxon_id} value={t.taxon_id}>
                      {t.scientific_name} [M: {t.vernacular_moore} | D: {t.vernacular_dioula} | F: {t.vernacular_fulfulde}]
                    </option>
                  ))}
                </select>

                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={addPrimaryUse}
                    onChange={(e) => setAddPrimaryUse(e.target.value)}
                    placeholder="Usage prioritaire..."
                    className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  />
                  <button
                    type="button"
                    onClick={handleAddCitedTaxon}
                    className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold"
                  >
                    + Ajouter
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* M3 : DIAGNOSTIC SANITAIRE (-2 à +2) */}
          <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3 shadow-md">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
              <span className="w-6 h-6 rounded-full bg-savanna-950 border border-savanna-700 flex items-center justify-center text-xs">
                M3
              </span>
              <span>Module M3 : Diagnostic & Dynamique des Populations (-2 à +2)</span>
            </div>

            {/* Perceived decline */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-zinc-300 font-semibold">Tendance perçue sur 20 ans :</label>
                <span className="font-mono font-black text-emerald-400">
                  {perceivedDecline > 0 ? `+${perceivedDecline}` : perceivedDecline}
                </span>
              </div>
              <div className="grid grid-cols-5 gap-1 text-center font-bold">
                {[-2, -1, 0, 1, 2].map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => setPerceivedDecline(val)}
                    className={`py-2 rounded-lg border text-xs transition ${
                      perceivedDecline === val
                        ? 'bg-emerald-600 border-emerald-400 text-white'
                        : 'bg-zinc-950 border-zinc-800 text-zinc-400'
                    }`}
                  >
                    {val > 0 ? `+${val}` : val}
                    <span className="block text-[8px] font-normal opacity-80">
                      {val === -2 && 'Disparition'}
                      {val === -1 && 'Régression'}
                      {val === 0 && 'Stable'}
                      {val === 1 && 'Progression'}
                      {val === 2 && 'Expansion'}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Dieback and parasite */}
            <div className="grid grid-cols-2 gap-2 pt-2">
              <div>
                <label className="text-zinc-400 block mb-1">Dépérissement houppier (-2 à +2)</label>
                <select
                  value={diebackSeverity}
                  onChange={(e) => setDiebackSeverity(parseInt(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  <option value="-2">-2 : Mortalité massive / Cimes sèches</option>
                  <option value="-1">-1 : Dépérissement modéré</option>
                  <option value="0">0 : Aucun dépérissement anormal</option>
                  <option value="1">+1 : Faible mortalité</option>
                  <option value="2">+2 : Cimes denses & vigoureuses</option>
                </select>
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Pression parasitaire (Gui, chenilles)</label>
                <select
                  value={parasitePressure}
                  onChange={(e) => setParasitePressure(parseInt(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  <option value="-2">-2 : Attaques destructrices létales</option>
                  <option value="-1">-1 : Infestation sévère</option>
                  <option value="0">0 : Attaques ordinaires équilibrées</option>
                  <option value="1">+1 : Faibles attaques</option>
                  <option value="2">+2 : Absence totale de parasites</option>
                </select>
              </div>
            </div>
          </div>

          {/* M4 : SUIVI PHÉNOLOGIQUE */}
          <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3 shadow-md">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
              <span className="w-6 h-6 rounded-full bg-savanna-950 border border-savanna-700 flex items-center justify-center text-xs">
                M4
              </span>
              <span>Module M4 : Décalages Phénologiques & Calendrier Climatique</span>
            </div>

            <div className="flex items-center space-x-3">
              <span className="text-zinc-300 font-semibold">Décalage phénologique observé ?</span>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setPhenologyShiftObserved(true)}
                  className={`px-3 py-1 rounded-lg border font-bold transition ${
                    phenologyShiftObserved
                      ? 'bg-emerald-600 border-emerald-400 text-white'
                      : 'bg-zinc-950 border-zinc-800 text-zinc-400'
                  }`}
                >
                  Oui
                </button>
                <button
                  type="button"
                  onClick={() => setPhenologyShiftObserved(false)}
                  className={`px-3 py-1 rounded-lg border font-bold transition ${
                    !phenologyShiftObserved
                      ? 'bg-emerald-600 border-emerald-400 text-white'
                      : 'bg-zinc-950 border-zinc-800 text-zinc-400'
                  }`}
                >
                  Non
                </button>
              </div>
            </div>

            {phenologyShiftObserved && (
              <div className="space-y-2 pt-2 animate-fade-in">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-zinc-400 block mb-1">Décalage Floraison</label>
                    <select
                      value={floweringShift}
                      onChange={(e) => setFloweringShift(parseInt(e.target.value))}
                      className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                    >
                      <option value="-2">-2 : Très précoce (&gt;1 mois)</option>
                      <option value="-1">-1 : Légèrement précoce</option>
                      <option value="0">0 : Inchangé / Normal</option>
                      <option value="1">+1 : Légèrement tardive</option>
                      <option value="2">+2 : Très tardive / Erratique</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-zinc-400 block mb-1">Décalage Fructification</label>
                    <select
                      value={fruitingShift}
                      onChange={(e) => setFruitingShift(parseInt(e.target.value))}
                      className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                    >
                      <option value="-2">-2 : Très précoce (&gt;1 mois)</option>
                      <option value="-1">-1 : Légèrement précoce</option>
                      <option value="0">0 : Inchangé / Normal</option>
                      <option value="1">+1 : Légèrement tardive</option>
                      <option value="2">+2 : Très tardive / Erratique</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-zinc-400 block mb-1">Détails des observations</label>
                  <textarea
                    rows={2}
                    value={phenologyDetails}
                    onChange={(e) => setPhenologyDetails(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                  />
                </div>
              </div>
            )}
          </div>

          {/* M5 : PRESSIONS & RNA */}
          <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3 shadow-md">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
              <span className="w-6 h-6 rounded-full bg-savanna-950 border border-savanna-700 flex items-center justify-center text-xs">
                M5
              </span>
              <span>Module M5 : Pressions, Feux & Régénération Naturelle Assistée (RNA)</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-zinc-400 block mb-1">Score Émondage (0 à 4)</label>
                <select
                  value={loppingIntensity}
                  onChange={(e) => setLoppingIntensity(parseInt(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  <option value="0">0 : Nul (Arbres intacts)</option>
                  <option value="1">1 : Faible / Occasionnel</option>
                  <option value="2">2 : Modéré / Branches secondaires</option>
                  <option value="3">3 : Sévère / Écimage systématique</option>
                  <option value="4">4 : Destructif (Tronc mutilé)</option>
                </select>
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Fréquence Feux</label>
                <select
                  value={fireFrequency}
                  onChange={(e) => setFireFrequency(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                >
                  <option value="Feux annuels répétés">Feux annuels répétés</option>
                  <option value="Tous les 2 à 3 ans">Tous les 2 à 3 ans</option>
                  <option value="Feux rares (> 5 ans)">Feux rares (&gt; 5 ans)</option>
                  <option value="Aucun feu (Protégé)">Aucun feu (Protégé)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-zinc-400 block mb-1">Pratique de la RNA ?</label>
                <select
                  value={rnaPracticed ? 'yes' : 'no'}
                  onChange={(e) => setRnaPracticed(e.target.value === 'yes')}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-bold"
                >
                  <option value="yes">Oui (RNA pratiquée)</option>
                  <option value="no">Non (Absence de RNA)</option>
                </select>
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Rang Résilience Sécheresse</label>
                <select
                  value={droughtResilienceRank}
                  onChange={(e) => setDroughtResilienceRank(parseInt(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100 font-bold"
                >
                  <option value="1">Rang 1 : Résilience Exceptionnelle</option>
                  <option value="2">Rang 2 : Forte résilience</option>
                  <option value="3">Rang 3 : Résilience moyenne</option>
                  <option value="4">Rang 4 : Vulnérabilité marquée</option>
                  <option value="5">Rang 5 : Très vulnérable</option>
                </select>
              </div>
            </div>

            {rnaPracticed && (
              <div>
                <label className="text-zinc-400 block mb-1">Techniques de RNA appliquées</label>
                <input
                  type="text"
                  value={rnaTechniques}
                  onChange={(e) => setRnaTechniques(e.target.value)}
                  placeholder="Ex: Protection des rejets, zaï, taille de formation..."
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
                />
              </div>
            )}

            <div>
              <label className="text-zinc-400 block mb-1">Usages traditionnels valorisés</label>
              <textarea
                rows={2}
                value={traditionalUses}
                onChange={(e) => setTraditionalUses(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-zinc-100"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center justify-center space-x-2 shadow-xl active:scale-98"
          >
            <CheckCircle2 className="w-5 h-5" />
            <span>Valider et Enregistrer l'Enquête (Persistance Hors-Ligne)</span>
          </button>
        </form>
      )}

      {/* TAB 2: TRAME XLSFORM & KOBOTOOLBOX */}
      {activeTab === 'xlsform' && (
        <div className="space-y-4 text-xs">
          <div className="p-4 bg-zinc-900 border border-savanna-800 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-emerald-400 flex items-center">
                  <FileSpreadsheet className="w-4 h-4 mr-1.5" /> Fichier Standard XLSForm (KoboToolbox & ODK)
                </h2>
                <p className="text-zinc-400 text-[11px] mt-0.5">
                  Conforme aux standards pyxform et ODK XForms v1.0
                </p>
              </div>
              <button
                type="button"
                onClick={handleDownloadXLSForm}
                className="py-2 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center shadow active:scale-95"
              >
                <Download className="w-4 h-4 mr-1" /> Télécharger .xlsx
              </button>
            </div>

            <div className="p-3 bg-zinc-950 rounded-xl border border-zinc-800 space-y-2 text-[11px]">
              <div className="flex justify-between border-b border-zinc-800 pb-1.5 font-mono">
                <span className="text-zinc-400">form_id :</span>
                <span className="font-bold text-zinc-100">sahelfield_enquete_socioeco_v1</span>
              </div>
              <div className="flex justify-between border-b border-zinc-800 pb-1.5 font-mono">
                <span className="text-zinc-400">version :</span>
                <span className="font-bold text-zinc-100">2026111401</span>
              </div>
              <div className="flex justify-between border-b border-zinc-800 pb-1.5 font-mono">
                <span className="text-zinc-400">default_language :</span>
                <span className="font-bold text-zinc-100">French (fr)</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-zinc-400">Onglets Excel intégrés :</span>
                <span className="font-bold text-emerald-400">survey, choices, settings</span>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <h3 className="font-bold text-zinc-200">Procédure de déploiement KoboToolbox :</h3>
              <ol className="list-decimal list-inside space-y-1 text-zinc-300">
                <li>Télécharger le fichier <code className="bg-zinc-950 px-1.5 py-0.5 rounded text-emerald-300">sahelfield_enquete_socioeco.xlsx</code> ci-dessus.</li>
                <li>Se connecter au serveur KoboToolbox (<span className="text-emerald-400 underline">kf.kobotoolbox.org</span> ou serveur ICC-UJKZ).</li>
                <li>Cliquer sur <strong>Nouveau</strong> &gt; <strong>Téléverser un XLSForm</strong> &gt; Choisir le fichier.</li>
                <li>Vérifier la prévisualisation Enketo et cliquer sur <strong>Déployer</strong>.</li>
                <li>Configurer l'application mobile <strong>ODK Collect</strong> sur les tablettes Android des enquêteurs en scannant le QR code du projet Kobo.</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: LISTE DES ENQUÊTES ENREGISTRÉES */}
      {activeTab === 'list' && (
        <div className="space-y-4 text-xs">
          {/* Progress bar towards 450 respondents */}
          <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-2xl space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-bold text-zinc-200">Objectif Campagne Doctorat (450 Répondants)</span>
              <span className="font-mono font-bold text-emerald-400">
                {surveys.length} / 450 ({((surveys.length / 450) * 100).toFixed(1)}%)
              </span>
            </div>

            <div className="w-full bg-zinc-950 rounded-full h-2.5 overflow-hidden border border-zinc-800">
              <div
                className="bg-gradient-to-r from-emerald-600 to-sahel-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, (surveys.length / 450) * 100)}%` }}
              />
            </div>

            <div className="grid grid-cols-2 gap-2 text-center text-[11px] pt-1">
              <div className="bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                <span className="text-zinc-400 block">Volet A : Experts</span>
                <span className="font-bold text-emerald-400 font-mono">{countExperts} / 150</span>
              </div>
              <div className="bg-zinc-950 p-2 rounded-lg border border-zinc-800">
                <span className="text-zinc-400 block">Volet B : Riverains</span>
                <span className="font-bold text-sahel-400 font-mono">{countLocals} / 300</span>
              </div>
            </div>
          </div>

          {/* List */}
          <div className="space-y-2">
            {surveys.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 text-xs bg-zinc-900/50 rounded-2xl">
                Aucune enquête enregistrée. Utilisez l'onglet "Saisie M1-M5" pour débuter un entretien.
              </div>
            ) : (
              surveys.map((s) => (
                <div
                  key={s.survey_id}
                  className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl space-y-1 hover:border-savanna-800 transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-zinc-100 text-xs">
                      {s.scientific_name || s.taxon_id}
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                      s.respondent_type === 'Expert' ? 'bg-blue-950 text-blue-400' : 'bg-amber-950 text-amber-400'
                    }`}>
                      {s.respondent_type}
                    </span>
                  </div>

                  <div className="text-[11px] text-zinc-400">
                    Village : <strong>{s.village_name}</strong> ({s.climatic_zone}) • Déclin : {s.perceived_decline_score}
                  </div>

                  <div className="flex justify-between items-center text-[10px] text-zinc-500 pt-1 border-t border-zinc-800">
                    <span>Smith Rang #{s.smith_saliency_rank || 1}</span>
                    {s.sync_status === 'SYNCED' ? (
                      <span className="text-emerald-400 flex items-center font-semibold">
                        <CheckCircle2 className="w-3 h-3 mr-1" /> Synchronisé
                      </span>
                    ) : (
                      <span className="text-sahel-400 flex items-center font-bold">
                        <Clock className="w-3 h-3 mr-1" /> En attente sync
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
