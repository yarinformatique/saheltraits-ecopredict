// SahelField - Générateur et Exportateur officiel de Trame XLSForm (KoboToolbox & ODK Collect)
import * as XLSX from 'xlsx';

export interface XLSFormDefinition {
  survey: Array<Record<string, string>>;
  choices: Array<Record<string, string>>;
  settings: Array<Record<string, string>>;
}

export function buildSahelFieldXLSFormData(): XLSFormDefinition {
  const survey: Array<Record<string, string>> = [
    // Métadonnées système
    { type: 'start', name: 'start', label: '' },
    { type: 'end', name: 'end', label: '' },
    { type: 'today', name: 'today', label: '' },
    { type: 'deviceid', name: 'deviceid', label: '' },

    // MODULE M1 : ANCRAGE
    { type: 'begin_group', name: 'group_m1', label: 'Module M1 : Ancrage Géographique & Profil Répondant', appearance: 'field-list' },
    { type: 'text', name: 'interviewer_code', label: 'Code / Nom de l\'enquêteur terrain', hint: 'Ex: ENQ-01 / Moussa SAWADOGO', required: 'yes' },
    { type: 'select_one respondent_type_list', name: 'respondent_type', label: 'Type de répondant', hint: 'Volet A: 150 experts | Volet B: 300 riverains locaux', required: 'yes' },
    { type: 'text', name: 'village_name', label: 'Nom du terroir villageois ou commune', hint: 'Ex: Yakouta, Dem, Pô', required: 'yes' },
    { type: 'select_one climatic_zone_list', name: 'climatic_zone', label: 'Zone bioclimatique au Burkina Faso', required: 'yes' },
    { type: 'geopoint', name: 'geom_village', label: 'Localisation GPS de l\'enquête (Point SRID 4326)', hint: 'Attendre précision < 5m', required: 'yes' },
    { type: 'select_one socio_profile_list', name: 'socio_profile', label: 'Profil socioprofessionnel du répondant', required: 'yes' },
    { type: 'select_one gender_list', name: 'gender', label: 'Genre du répondant', required: 'yes' },
    { type: 'select_one age_category_list', name: 'age_category', label: 'Tranche d\'âge', required: 'yes' },
    { type: 'integer', name: 'seniority_years', label: 'Ancienneté d\'habitation ou d\'activité dans la localité (années)', constraint: '. >= 0 and . <= 120', constraint_message: 'L\'ancienneté doit être comprise entre 0 et 120 ans.', required: 'yes' },
    { type: 'end_group', name: 'group_m1', label: '' },

    // MODULE M2 : FREE-LISTING
    { type: 'begin_group', name: 'group_m2', label: 'Module M2 : Free-Listing Ethnobotanique & Indice de Smith', appearance: 'field-list' },
    { type: 'note', name: 'm2_note', label: 'Énumération spontanée des espèces ligneuses les plus résilientes face au climat sahélien.' },
    { type: 'integer', name: 'species_count', label: 'Nombre d\'espèces citées par le répondant (1 à 10)', hint: 'Recommandé: au moins 3 à 5 espèces', constraint: '. >= 1 and . <= 10', constraint_message: 'Veuillez saisir un nombre entre 1 et 10.', required: 'yes' },
    { type: 'begin_repeat', name: 'species_repeat', label: 'Espèce citée n°${pos}', appearance: 'field-list', parameters: 'count=${species_count}' },
    { type: 'calculate', name: 'pos', calculation: 'position(..)' },
    { type: 'select_one species_list', name: 'taxon_key', label: 'Nom de l\'espèce ligneuse (Scientifique / Mooré / Dioula / Fulfuldé)', required: 'yes' },
    { type: 'text', name: 'other_species_name', label: 'Préciser le nom scientifique ou vernaculaire si absent de la liste', relevant: '${taxon_key} = "other"', required: 'yes' },
    { type: 'select_one use_list', name: 'primary_use', label: 'Usage prioritaire pour la communauté', required: 'yes' },
    { type: 'calculate', name: 'smith_rank', calculation: '${pos}' },
    { type: 'calculate', name: 'smith_saliency_item', calculation: '(${species_count} - ${pos} + 1) div ${species_count}' },
    { type: 'end_repeat', name: 'species_repeat', label: '' },
    { type: 'end_group', name: 'group_m2', label: '' },

    // MODULE M3 : DIAGNOSTIC SANITAIRE
    { type: 'begin_group', name: 'group_m3', label: 'Module M3 : Diagnostic Sanitaire & Déclin (-2 à +2)', appearance: 'field-list' },
    { type: 'note', name: 'm3_note', label: 'Échelle de Likert : -2 = Régression très forte, -1 = Régression modérée, 0 = Stable, +1 = Progression légère, +2 = Forte expansion' },
    { type: 'select_one likert_5', name: 'perceived_decline_score', label: 'Tendance perçue des populations d\'arbres sur les 20 dernières années', appearance: 'likert', required: 'yes' },
    { type: 'select_one likert_5', name: 'dieback_severity', label: 'Sévérité du dépérissement foliaire et mortalité anormale', appearance: 'likert', required: 'yes' },
    { type: 'select_one likert_5', name: 'parasite_pressure', label: 'Attaques parasitaires (Loranthaceae/gui, chenilles défoliatrices)', appearance: 'likert', required: 'yes' },
    { type: 'end_group', name: 'group_m3', label: '' },

    // MODULE M4 : PHÉNOLOGIE
    { type: 'begin_group', name: 'group_m4', label: 'Module M4 : Suivi Phénologique & Décalages Climatiques', appearance: 'field-list' },
    { type: 'select_one yes_no', name: 'phenology_shift_observed', label: 'Avez-vous observé un décalage du cycle de floraison ou de fructification ?', required: 'yes' },
    { type: 'select_one shift_scale', name: 'phenology_flowering_shift', label: 'Décalage observé de la date de floraison', relevant: '${phenology_shift_observed} = "yes"', appearance: 'likert' },
    { type: 'select_one shift_scale', name: 'phenology_fruiting_shift', label: 'Décalage observé de la date de maturité des fruits', relevant: '${phenology_shift_observed} = "yes"', appearance: 'likert' },
    { type: 'text', name: 'phenology_shift_details', label: 'Observations détaillées sur les anomalies saisonnières', hint: 'Ex: Floraison tardive, avortement des fleurs sous vague de chaleur', relevant: '${phenology_shift_observed} = "yes"', appearance: 'multiline' },
    { type: 'end_group', name: 'group_m4', label: '' },

    // MODULE M5 : PRESSIONS & PRATIQUES DE RNA
    { type: 'begin_group', name: 'group_m5', label: 'Module M5 : Pressions Anthropiques & Pratiques de RNA', appearance: 'field-list' },
    { type: 'select_one lopping_scale', name: 'lopping_intensity', label: 'Intensité de l\'émondage pour le fourrage aérien', required: 'yes' },
    { type: 'select_one fire_scale', name: 'fire_frequency', label: 'Fréquence et impact des feux de brousse', required: 'yes' },
    { type: 'select_one grazing_scale', name: 'overgrazing_level', label: 'Pression du surpâturage sur la régénération naturelle', required: 'yes' },
    { type: 'select_one yes_no', name: 'rna_practiced', label: 'Pratique de la Régénération Naturelle Assistée (RNA) dans les parcelles ?', required: 'yes' },
    { type: 'select_multiple rna_tech_list', name: 'rna_techniques', label: 'Techniques de RNA appliquées par les exploitants', relevant: '${rna_practiced} = "yes"' },
    { type: 'select_one resilience_rank_list', name: 'drought_resilience_rank', label: 'Rang global de résistance à la sécheresse extrême', required: 'yes' },
    { type: 'text', name: 'traditional_uses', label: 'Usages traditionnels et savoirs endogènes valorisés', appearance: 'multiline' },
    { type: 'text', name: 'recommendations', label: 'Recommandations pour la conservation et l\'agroforesterie', appearance: 'multiline' },
    { type: 'end_group', name: 'group_m5', label: '' },
  ];

  const choices: Array<Record<string, string>> = [
    // respondent_type_list
    { list_name: 'respondent_type_list', name: 'Expert', label: 'Volet A : Expert / Chercheur / Cadre environnement' },
    { list_name: 'respondent_type_list', name: 'Local', label: 'Volet B : Riverain local / Producteur / Éleveur' },

    // climatic_zone_list
    { list_name: 'climatic_zone_list', name: 'Sahélienne', label: 'Sahélienne (< 600 mm/an)' },
    { list_name: 'climatic_zone_list', name: 'Soudano-Sahélienne', label: 'Soudano-Sahélienne (600 - 900 mm/an)' },
    { list_name: 'climatic_zone_list', name: 'Soudanienne', label: 'Soudanienne (> 900 mm/an)' },

    // socio_profile_list
    { list_name: 'socio_profile_list', name: 'agriculteur', label: 'Agriculteur sédentaire' },
    { list_name: 'socio_profile_list', name: 'eleveur', label: 'Éleveur transhumant / Pasteur' },
    { list_name: 'socio_profile_list', name: 'agropasteur', label: 'Agropasteur (mixte)' },
    { list_name: 'socio_profile_list', name: 'traditherapeute', label: 'Tradithérapeute / Tradipraticien' },
    { list_name: 'socio_profile_list', name: 'coutumier', label: 'Chef coutumier / Maître de la terre' },
    { list_name: 'socio_profile_list', name: 'forestier', label: 'Agent des Eaux et Forêts / Conservateur' },
    { list_name: 'socio_profile_list', name: 'chercheur', label: 'Chercheur / Enseignant-chercheur' },

    // gender_list
    { list_name: 'gender_list', name: 'homme', label: 'Homme' },
    { list_name: 'gender_list', name: 'femme', label: 'Femme' },

    // age_category_list
    { list_name: 'age_category_list', name: 'age_lt25', label: 'Moins de 25 ans' },
    { list_name: 'age_category_list', name: 'age_25_40', label: '25 à 40 ans' },
    { list_name: 'age_category_list', name: 'age_41_60', label: '41 à 60 ans' },
    { list_name: 'age_category_list', name: 'age_gt60', label: 'Plus de 60 ans' },

    // species_list (10 essences clés du Burkina Faso)
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000001', label: 'Balanites aegyptiaca (Kieglga / Ségéné / Murtooki)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000002', label: 'Adansonia digitata (Toèga / Sira / Boki)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000003', label: 'Faidherbia albida (Zaanga / Balanzan / Caski)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000004', label: 'Vachellia tortilis (Gom-peelga / Danba / Cilluki)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000005', label: 'Combretum glutinosum (Rambolga / Doki / Dooki)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000006', label: 'Ziziphus mauritiana (Moug-noaga / Tomboron / Jaabi)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000007', label: 'Senegalia senegal (Gom-sablga / Danba-fiman / Pattuki)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000008', label: 'Sclerocarya birrea (Nobga / Nouna / Eeri)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000009', label: 'Tamarindus indica (Pusga / Tomi / Jaammi)' },
    { list_name: 'species_list', name: 'b0000000-0000-0000-0000-000000000010', label: 'Parkia biglobosa (Roanga / Néré / Narehi)' },
    { list_name: 'species_list', name: 'other', label: 'Autre essence sahélienne non listée' },

    // use_list
    { list_name: 'use_list', name: 'alim', label: 'Alimentation humaine & PFNL (fruits, feuilles, huile)' },
    { list_name: 'use_list', name: 'pharma', label: 'Pharmacopée & Médecine traditionnelle' },
    { list_name: 'use_list', name: 'fourrage', label: 'Fourrage aérien bétail en saison sèche' },
    { list_name: 'use_list', name: 'bois_energie', label: 'Bois de chauffe et charbonnage' },
    { list_name: 'use_list', name: 'bois_oeuvre', label: 'Bois d\'œuvre, clôture et construction' },
    { list_name: 'use_list', name: 'ombrage_haie', label: 'Ombrage de repos, haie vive et brise-vent' },
    { list_name: 'use_list', name: 'sol_rna', label: 'Fertilisation du sol et lutte anti-érosive' },
    { list_name: 'use_list', name: 'rituel', label: 'Valeurs culturelles, rituelles et sacrées' },

    // likert_5
    { list_name: 'likert_5', name: '-2', label: '-2 : Régression très forte / Risque de disparition locale' },
    { list_name: 'likert_5', name: '-1', label: '-1 : Régression modérée' },
    { list_name: 'likert_5', name: '0', label: '0 : Population stable' },
    { list_name: 'likert_5', name: '1', label: '+1 : Légère progression' },
    { list_name: 'likert_5', name: '2', label: '+2 : Forte expansion / Régénération abondante' },

    // yes_no
    { list_name: 'yes_no', name: 'yes', label: 'Oui' },
    { list_name: 'yes_no', name: 'no', label: 'Non' },

    // shift_scale
    { list_name: 'shift_scale', name: '-2', label: '-2 : Très précoce (> 1 mois d\'avance)' },
    { list_name: 'shift_scale', name: '-1', label: '-1 : Modérément précoce' },
    { list_name: 'shift_scale', name: '0', label: '0 : Calendrier saisonnier normal' },
    { list_name: 'shift_scale', name: '1', label: '+1 : Modérément tardif' },
    { list_name: 'shift_scale', name: '2', label: '+2 : Très tardif / Erratique' },

    // lopping_scale
    { list_name: 'lopping_scale', name: '0', label: '0 : Nul / Branches intactes' },
    { list_name: 'lopping_scale', name: '1', label: '1 : Faible / Émondage occasionnel' },
    { list_name: 'lopping_scale', name: '2', label: '2 : Modéré / Branches secondaires' },
    { list_name: 'lopping_scale', name: '3', label: '3 : Sévère / Écimage systématique' },
    { list_name: 'lopping_scale', name: '4', label: '4 : Destructif / Tronc mutilé' },

    // fire_scale
    { list_name: 'fire_scale', name: 'annuel', label: 'Feux annuels répétés' },
    { list_name: 'fire_scale', name: 'biennal', label: 'Feux tous les 2 à 3 ans' },
    { list_name: 'fire_scale', name: 'rare', label: 'Feux rares (> 5 ans)' },
    { list_name: 'fire_scale', name: 'jamais', label: 'Parcelle protégée (aucun feu)' },

    // grazing_scale
    { list_name: 'grazing_scale', name: '0', label: 'Nulle / Parcelle exempte de bétail' },
    { list_name: 'grazing_scale', name: '1', label: 'Faible / Pâture légère' },
    { list_name: 'grazing_scale', name: '2', label: 'Forte / Broutage régulier' },
    { list_name: 'grazing_scale', name: '3', label: 'Très forte / Surpâturage critique' },

    // rna_tech_list
    { list_name: 'rna_tech_list', name: 'protege_jeunes', label: 'Protection des jeunes rejets contre la dent du bétail' },
    { list_name: 'rna_tech_list', name: 'taille_formation', label: 'Taille de formation et sélection des tiges vigoureuses' },
    { list_name: 'rna_tech_list', name: 'zai_demilune', label: 'Aménagements CES associés (Zaï, Demi-lunes, Cordons)' },
    { list_name: 'rna_tech_list', name: 'cloture_defens', label: 'Mise en défens et clôtures épineuses' },
    { list_name: 'rna_tech_list', name: 'conservation_champs', label: 'Épargne systématique des semenciers lors des labours' },

    // resilience_rank_list
    { list_name: 'resilience_rank_list', name: '1', label: 'Rang 1 : Résilience exceptionnelle (Survie aux pires sécheresses)' },
    { list_name: 'resilience_rank_list', name: '2', label: 'Rang 2 : Forte résilience' },
    { list_name: 'resilience_rank_list', name: '3', label: 'Rang 3 : Résilience modérée' },
    { list_name: 'resilience_rank_list', name: '4', label: 'Rang 4 : Vulnérabilité marquée' },
    { list_name: 'resilience_rank_list', name: '5', label: 'Rang 5 : Très vulnérable (Forte mortalité)' },
  ];

  const settings: Array<Record<string, string>> = [
    {
      form_title: 'SahelField — Enquête Socio-Écologique & Ethnobotanique (Doctorat 2026-2029)',
      form_id: 'sahelfield_enquete_socioeco_v1',
      version: '2026111401',
      default_language: 'French (fr)',
    },
  ];

  return { survey, choices, settings };
}

// Export XLSForm as Uint8Array (binary XLSX) for download or deployment
export function generateXLSFormWorkbook(): Uint8Array {
  const { survey, choices, settings } = buildSahelFieldXLSFormData();

  const wb = XLSX.utils.book_new();

  const wsSurvey = XLSX.utils.json_to_sheet(survey, {
    header: [
      'type',
      'name',
      'label',
      'hint',
      'required',
      'relevant',
      'constraint',
      'constraint_message',
      'calculation',
      'appearance',
      'parameters',
    ],
  });

  const wsChoices = XLSX.utils.json_to_sheet(choices, {
    header: ['list_name', 'name', 'label'],
  });

  const wsSettings = XLSX.utils.json_to_sheet(settings, {
    header: ['form_title', 'form_id', 'version', 'default_language'],
  });

  XLSX.utils.book_append_sheet(wb, wsSurvey, 'survey');
  XLSX.utils.book_append_sheet(wb, wsChoices, 'choices');
  XLSX.utils.book_append_sheet(wb, wsSettings, 'settings');

  const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  return new Uint8Array(buf);
}
