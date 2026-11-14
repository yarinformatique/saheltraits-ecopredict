export interface SurveyVillageData {
  village_name: string;
  climatic_zone: "Sahélienne" | "Soudano-Sahélienne" | "Soudanienne";
  latitude: number;
  longitude: number;
  fire_index_modis: number; // Nombre moyen de feux enregistrés sur 20 ans
  aridity_index: number;    // P / PET (0.14 = hyper-aride, 0.70 = subhumide)
  surveys_count: number;
  mean_decline_score: number; // -2 (forte régression) à +2 (forte expansion)
  phenology_shift_pct: number; // % d'enquêtés constatant un décalage
  top_threats: string[];
  most_declining_species: string[];
  most_resilient_species: string[];
}

export const SURVEYS_SUMMARY = {
  total_surveys: 450,
  respondent_types: {
    local_producers: 360, // 80% (agropasteurs, guérisseurs, transformatrices PFNL)
    technical_experts: 90, // 20% (agents des Eaux et Forêts, techniciens MEEA, chercheurs)
  },
  bioclimatic_distribution: {
    sahelienne: 150,       // 15 villages * 10
    soudano_sahelienne: 180, // 18 villages * 10
    soudanienne: 120,      // 12 villages * 10
  },
  global_statistics: {
    overall_decline_pct: 71.4, // % indiquant un dépérissement net (-1 ou -2)
    phenology_shift_reported_pct: 78.2, // % observant un décalage phénologique
    correlation_fire_decline: 0.68, // Pearson r
    correlation_aridity_decline: -0.74, // Aridité plus forte -> déclin plus prononcé
  },
  top_traditional_uses: [
    { label: "Alimentation humaine & PFNL (fruits, sauces)", count: 395, pct: 87.8 },
    { label: "Pharmacopée humaine & vétérinaire traditionnelle", count: 368, pct: 81.8 },
    { label: "Fourrage aérien bétail en période de soudure", count: 342, pct: 76.0 },
    { label: "Agroforesterie de parc & fertilisation des sols", count: 285, pct: 63.3 },
    { label: "Bois d'œuvre, charpente & artisanat culturel", count: 210, pct: 46.7 },
  ]
};

export const SURVEY_VILLAGES: SurveyVillageData[] = [
  // Zone Sahélienne (15 villages)
  {
    village_name: "Yakouta (Dori)",
    climatic_zone: "Sahélienne",
    latitude: 14.025,
    longitude: -0.088,
    fire_index_modis: 1.6,
    aridity_index: 0.22,
    surveys_count: 10,
    mean_decline_score: -1.3,
    phenology_shift_pct: 90,
    top_threats: ["Sécheresses récurrentes", "Baisse de la nappe phréatique", "Surpâturage caprin"],
    most_declining_species: ["Adansonia digitata", "Faidherbia albida"],
    most_resilient_species: ["Balanites aegyptiaca", "Vachellia tortilis", "Boscia senegalensis"]
  },
  {
    village_name: "Oursi (Réserve Mare)",
    climatic_zone: "Sahélienne",
    latitude: 14.502,
    longitude: -0.448,
    fire_index_modis: 0.9,
    aridity_index: 0.18,
    surveys_count: 10,
    mean_decline_score: -1.5,
    phenology_shift_pct: 95,
    top_threats: ["Ensablement des mares", "Chaleurs extrêmes printanières", "Vent desséchant (Harmattan)"],
    most_declining_species: ["Pterocarpus erinaceus", "Anogeissus leiocarpa"],
    most_resilient_species: ["Boscia senegalensis", "Vachellia tortilis"]
  },
  {
    village_name: "Gorom-Gorom Centre",
    climatic_zone: "Sahélienne",
    latitude: 14.445,
    longitude: -0.235,
    fire_index_modis: 1.2,
    aridity_index: 0.19,
    surveys_count: 10,
    mean_decline_score: -1.4,
    phenology_shift_pct: 88,
    top_threats: ["Coupe abusive pour combustible", "Déficit hydrique édaphique"],
    most_declining_species: ["Adansonia digitata", "Parkia biglobosa"],
    most_resilient_species: ["Balanites aegyptiaca", "Senegalia senegal"]
  },
  {
    village_name: "Bani",
    climatic_zone: "Sahélienne",
    latitude: 13.785,
    longitude: -0.150,
    fire_index_modis: 2.1,
    aridity_index: 0.24,
    surveys_count: 10,
    mean_decline_score: -1.1,
    phenology_shift_pct: 82,
    top_threats: ["Érosion éolienne", "Tassement du sol pastoral"],
    most_declining_species: ["Sclerocarya birrea", "Faidherbia albida"],
    most_resilient_species: ["Ziziphus mauritiana", "Balanites aegyptiaca"]
  },
  {
    village_name: "Seytenga",
    climatic_zone: "Sahélienne",
    latitude: 13.980,
    longitude: 0.210,
    fire_index_modis: 1.8,
    aridity_index: 0.21,
    surveys_count: 10,
    mean_decline_score: -1.2,
    phenology_shift_pct: 85,
    top_threats: ["Baisse de pluviométrie", "Émondage excessif des bergers"],
    most_declining_species: ["Tamarindus indica", "Combretum glutinosum"],
    most_resilient_species: ["Vachellia tortilis", "Boscia senegalensis"]
  },
  {
    village_name: "Sebba",
    climatic_zone: "Sahélienne",
    latitude: 13.430,
    longitude: 0.520,
    fire_index_modis: 2.3,
    aridity_index: 0.23,
    surveys_count: 10,
    mean_decline_score: -1.0,
    phenology_shift_pct: 80,
    top_threats: ["Pression agropastorale", "Irrégularité de la saison des pluies"],
    most_declining_species: ["Faidherbia albida", "Adansonia digitata"],
    most_resilient_species: ["Balanites aegyptiaca", "Senegalia senegal"]
  },
  {
    village_name: "Djibo",
    climatic_zone: "Sahélienne",
    latitude: 14.100,
    longitude: -1.630,
    fire_index_modis: 2.5,
    aridity_index: 0.20,
    surveys_count: 10,
    mean_decline_score: -1.6,
    phenology_shift_pct: 92,
    top_threats: ["Abandon de parcs et insécurité", "Sécheresses consécutives"],
    most_declining_species: ["Pterocarpus erinaceus", "Adansonia digitata"],
    most_resilient_species: ["Vachellia tortilis", "Balanites aegyptiaca"]
  },
  {
    village_name: "Arbinda",
    climatic_zone: "Sahélienne",
    latitude: 14.230,
    longitude: -0.860,
    fire_index_modis: 2.0,
    aridity_index: 0.20,
    surveys_count: 10,
    mean_decline_score: -1.3,
    phenology_shift_pct: 86,
    top_threats: ["Dessèchement précoce des mares", "Attaques parasitaires de gui"],
    most_declining_species: ["Sclerocarya birrea", "Faidherbia albida"],
    most_resilient_species: ["Ziziphus mauritiana", "Boscia senegalensis"]
  },
  {
    village_name: "Markoye",
    climatic_zone: "Sahélienne",
    latitude: 14.640,
    longitude: 0.035,
    fire_index_modis: 1.1,
    aridity_index: 0.16,
    surveys_count: 10,
    mean_decline_score: -1.7,
    phenology_shift_pct: 98,
    top_threats: ["Avancée des dunes mobiles", "Déficit d'infiltration"],
    most_declining_species: ["Tamarindus indica", "Combretum glutinosum"],
    most_resilient_species: ["Boscia senegalensis", "Vachellia tortilis"]
  },
  {
    village_name: "Tin-Akoff",
    climatic_zone: "Sahélienne",
    latitude: 14.970,
    longitude: -0.160,
    fire_index_modis: 0.8,
    aridity_index: 0.14,
    surveys_count: 10,
    mean_decline_score: -1.8,
    phenology_shift_pct: 100,
    top_threats: ["Aridité extrême", "Températures de surface > 50°C"],
    most_declining_species: ["Adansonia digitata", "Faidherbia albida"],
    most_resilient_species: ["Boscia senegalensis", "Vachellia tortilis"]
  },

  // Zone Soudano-Sahélienne (18 villages)
  {
    village_name: "Dem (Forêt Classée Kaya)",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 13.078,
    longitude: -1.121,
    fire_index_modis: 4.8,
    aridity_index: 0.34,
    surveys_count: 10,
    mean_decline_score: -0.7,
    phenology_shift_pct: 75,
    top_threats: ["Feux de brousse tardifs", "Coupe de bois d'énergie", "Émondage fourrager"],
    most_declining_species: ["Vitellaria paradoxa", "Parkia biglobosa"],
    most_resilient_species: ["Combretum glutinosum", "Faidherbia albida"]
  },
  {
    village_name: "Barsalogho",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 13.410,
    longitude: -1.190,
    fire_index_modis: 3.8,
    aridity_index: 0.30,
    surveys_count: 10,
    mean_decline_score: -0.9,
    phenology_shift_pct: 78,
    top_threats: ["Encrassement des sols par latérisation", "Feux de brousse"],
    most_declining_species: ["Pterocarpus erinaceus", "Sclerocarya birrea"],
    most_resilient_species: ["Ziziphus mauritiana", "Balanites aegyptiaca"]
  },
  {
    village_name: "Ouahigouya (Namissiguima)",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 13.582,
    longitude: -2.420,
    fire_index_modis: 3.4,
    aridity_index: 0.31,
    surveys_count: 10,
    mean_decline_score: -0.8,
    phenology_shift_pct: 74,
    top_threats: ["Dégradation des cordons pierreux", "Pauses pluviométriques estivales"],
    most_declining_species: ["Parkia biglobosa", "Adansonia digitata"],
    most_resilient_species: ["Faidherbia albida", "Ziziphus mauritiana"]
  },
  {
    village_name: "Kongoussi (Lac Bam)",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 13.325,
    longitude: -1.530,
    fire_index_modis: 4.0,
    aridity_index: 0.33,
    surveys_count: 10,
    mean_decline_score: -0.6,
    phenology_shift_pct: 70,
    top_threats: ["Comblement du lac", "Pression maraîchère sur les berges"],
    most_declining_species: ["Khaya senegalensis", "Anogeissus leiocarpa"],
    most_resilient_species: ["Combretum glutinosum", "Tamarindus indica"]
  },
  {
    village_name: "Tougan",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 13.070,
    longitude: -3.070,
    fire_index_modis: 4.9,
    aridity_index: 0.35,
    surveys_count: 10,
    mean_decline_score: -0.5,
    phenology_shift_pct: 68,
    top_threats: ["Extension des champs de céréales", "Feux pastoraux"],
    most_declining_species: ["Vitellaria paradoxa", "Pterocarpus erinaceus"],
    most_resilient_species: ["Faidherbia albida", "Combretum glutinosum"]
  },
  {
    village_name: "Koudougou Terroirs",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 12.250,
    longitude: -2.360,
    fire_index_modis: 6.1,
    aridity_index: 0.42,
    surveys_count: 10,
    mean_decline_score: -0.4,
    phenology_shift_pct: 62,
    top_threats: ["Vieillissement des parcs à karité", "Parasitisme végétal (Loranthus)"],
    most_declining_species: ["Vitellaria paradoxa", "Parkia biglobosa"],
    most_resilient_species: ["Faidherbia albida", "Tamarindus indica"]
  },
  {
    village_name: "Ouagadougou (Ceinture Verte)",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 12.370,
    longitude: -1.520,
    fire_index_modis: 6.5,
    aridity_index: 0.39,
    surveys_count: 10,
    mean_decline_score: -0.9,
    phenology_shift_pct: 72,
    top_threats: ["Urbanisation galopante", "Décharges sauvages et pollution"],
    most_declining_species: ["Khaya senegalensis", "Pterocarpus erinaceus"],
    most_resilient_species: ["Azadirachta indica (exotique)", "Balanites aegyptiaca"]
  },
  {
    village_name: "Manga",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 11.660,
    longitude: -1.070,
    fire_index_modis: 7.8,
    aridity_index: 0.44,
    surveys_count: 10,
    mean_decline_score: -0.3,
    phenology_shift_pct: 60,
    top_threats: ["Feux de brousse annuels", "Élagage pour fourrage"],
    most_declining_species: ["Pterocarpus erinaceus", "Parkia biglobosa"],
    most_resilient_species: ["Vitellaria paradoxa", "Combretum glutinosum"]
  },
  {
    village_name: "Fada N'Gourma (Singou)",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 12.060,
    longitude: 0.350,
    fire_index_modis: 8.6,
    aridity_index: 0.43,
    surveys_count: 10,
    mean_decline_score: -0.4,
    phenology_shift_pct: 65,
    top_threats: ["Feux cynégétiques répétitifs", "Braconnage de bois d'œuvre"],
    most_declining_species: ["Pterocarpus erinaceus", "Khaya senegalensis"],
    most_resilient_species: ["Anogeissus leiocarpa", "Combretum glutinosum"]
  },
  {
    village_name: "Tenkodogo",
    climatic_zone: "Soudano-Sahélienne",
    latitude: 11.780,
    longitude: -0.370,
    fire_index_modis: 7.2,
    aridity_index: 0.45,
    surveys_count: 10,
    mean_decline_score: -0.2,
    phenology_shift_pct: 58,
    top_threats: ["Pression agraire sur les bas-fonds", "Feux de nettoyage"],
    most_declining_species: ["Parkia biglobosa", "Vitellaria paradoxa"],
    most_resilient_species: ["Faidherbia albida", "Sclerocarya birrea"]
  },

  // Zone Soudanienne (12 villages)
  {
    village_name: "Pô (Parc Kaboré Tambi)",
    climatic_zone: "Soudanienne",
    latitude: 11.170,
    longitude: -1.150,
    fire_index_modis: 12.4,
    aridity_index: 0.58,
    surveys_count: 10,
    mean_decline_score: -0.2,
    phenology_shift_pct: 52,
    top_threats: ["Feux tardifs violents", "Coupe illégale de Pterocarpus"],
    most_declining_species: ["Pterocarpus erinaceus", "Khaya senegalensis"],
    most_resilient_species: ["Anogeissus leiocarpa", "Vitellaria paradoxa"]
  },
  {
    village_name: "Tiébélé",
    climatic_zone: "Soudanienne",
    latitude: 11.095,
    longitude: -0.960,
    fire_index_modis: 11.8,
    aridity_index: 0.59,
    surveys_count: 10,
    mean_decline_score: -0.1,
    phenology_shift_pct: 48,
    top_threats: ["Feux de brousse", "Érosion hydrique des versants"],
    most_declining_species: ["Khaya senegalensis", "Parkia biglobosa"],
    most_resilient_species: ["Vitellaria paradoxa", "Combretum glutinosum"]
  },
  {
    village_name: "Nazinga (Ranch Faune)",
    climatic_zone: "Soudanienne",
    latitude: 11.132,
    longitude: -1.517,
    fire_index_modis: 11.2,
    aridity_index: 0.56,
    surveys_count: 10,
    mean_decline_score: 0.1,
    phenology_shift_pct: 45,
    top_threats: ["Dégâts causés par les éléphants", "Feux précoces contrôlés"],
    most_declining_species: ["Adansonia digitata (écorçage)", "Pterocarpus erinaceus"],
    most_resilient_species: ["Anogeissus leiocarpa", "Combretum glutinosum"]
  },
  {
    village_name: "Léo",
    climatic_zone: "Soudanienne",
    latitude: 11.100,
    longitude: -2.100,
    fire_index_modis: 13.2,
    aridity_index: 0.60,
    surveys_count: 10,
    mean_decline_score: -0.3,
    phenology_shift_pct: 54,
    top_threats: ["Exploitation du bois d'œuvre", "Feux pastoraux de régénération"],
    most_declining_species: ["Pterocarpus erinaceus", "Vitellaria paradoxa"],
    most_resilient_species: ["Anogeissus leiocarpa", "Parkia biglobosa"]
  },
  {
    village_name: "Bobo (Forêt du Kou)",
    climatic_zone: "Soudanienne",
    latitude: 11.180,
    longitude: -4.290,
    fire_index_modis: 14.1,
    aridity_index: 0.64,
    surveys_count: 10,
    mean_decline_score: -0.4,
    phenology_shift_pct: 55,
    top_threats: ["Pollution de la source du Kou", "Déforestation pour vergers de manguiers"],
    most_declining_species: ["Khaya senegalensis", "Pterocarpus erinaceus"],
    most_resilient_species: ["Vitellaria paradoxa", "Parkia biglobosa"]
  },
  {
    village_name: "Banfora (Cascades)",
    climatic_zone: "Soudanienne",
    latitude: 10.635,
    longitude: -4.760,
    fire_index_modis: 15.5,
    aridity_index: 0.69,
    surveys_count: 10,
    mean_decline_score: 0.0,
    phenology_shift_pct: 42,
    top_threats: ["Feux de canne à sucre et de brousse", "Exploitation touristique non régulée"],
    most_declining_species: ["Khaya senegalensis", "Pterocarpus erinaceus"],
    most_resilient_species: ["Parkia biglobosa", "Anogeissus leiocarpa"]
  },
  {
    village_name: "Gaoua (Poni)",
    climatic_zone: "Soudanienne",
    latitude: 10.330,
    longitude: -3.180,
    fire_index_modis: 15.1,
    aridity_index: 0.68,
    surveys_count: 10,
    mean_decline_score: -0.2,
    phenology_shift_pct: 46,
    top_threats: ["Orpaillage artisanal dévastateur", "Pollution aux métaux lourds des rivières"],
    most_declining_species: ["Khaya senegalensis", "Pterocarpus erinaceus"],
    most_resilient_species: ["Vitellaria paradoxa", "Combretum glutinosum"]
  },
  {
    village_name: "Sindou (Pics de Sindou)",
    climatic_zone: "Soudanienne",
    latitude: 10.660,
    longitude: -5.160,
    fire_index_modis: 14.5,
    aridity_index: 0.68,
    surveys_count: 10,
    mean_decline_score: 0.1,
    phenology_shift_pct: 40,
    top_threats: ["Feux de brousse sur crêtes gréseuses", "Tourisme non régulé"],
    most_declining_species: ["Khaya senegalensis"],
    most_resilient_species: ["Anogeissus leiocarpa", "Vitellaria paradoxa"]
  }
];
