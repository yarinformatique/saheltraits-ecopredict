export interface SpeciesInfo {
  id: string;
  scientific_name: string;
  accepted_name_gbif: string;
  gbif_usage_key: number;
  family: string;
  genus: string;
  vernacular_moore: string;
  vernacular_dioula: string;
  vernacular_fulfulde: string;
  functional_group: string;
  iucn_status: "LC" | "VU" | "EN" | "CR" | "NT";
  description: string;
  distribution_zone: string;
  photo_url: string;
  traits: {
    sla_mm2mg: number;          // Surface Foliaire Spécifique
    ldmc_mgg: number;           // Teneur en Matière Sèche Foliaire
    wood_density_gcm3: number;  // Densité du Bois
    seed_mass_mg: number;       // Masse de 100 graines
    p50_hydraulic_mpa: number;  // Vulnérabilité cavitation hydraulique
    leaf_thickness_um: number;  // Épaisseur foliaire
    drought_index: number;      // 0-100 Tolérance sécheresse
    fire_resistance: number;    // 0-100 Résistance aux feux
  };
  germination: {
    t50_days: number;
    gp_ctrl_pct: number;
    gp_peg_pct: number; // Taux sous -0.8 MPa PEG 6000
    regime: string;
  };
  projections: {
    ssp245_2050: { change_pct: number; vuln_idx: number; status: string };
    ssp245_2080: { change_pct: number; vuln_idx: number; status: string };
    ssp585_2050: { change_pct: number; vuln_idx: number; status: string };
    ssp585_2080: { change_pct: number; vuln_idx: number; status: string };
  };
  ethnobotany: {
    traditional_uses: string[];
    cultural_importance: string;
    medicinal_properties: string;
  };
}

export const SPECIES_CATALOG: SpeciesInfo[] = [
  {
    id: "b0000000-0000-0000-0000-000000000001",
    scientific_name: "Balanites aegyptiaca (L.) Delile",
    accepted_name_gbif: "Balanites aegyptiaca (L.) Delile",
    gbif_usage_key: 3152865,
    family: "Zygophyllaceae",
    genus: "Balanites",
    vernacular_moore: "Kieglga",
    vernacular_dioula: "Ségéné",
    vernacular_fulfulde: "Murtooki",
    functional_group: "Épineux xérophyte persistant",
    iucn_status: "LC",
    description: "Arbre emblématique du Sahel ('Dattier du désert') pourvu d'épines acérées photosynthétiques et d'un pivot racinaire dépassant 15 à 20 mètres de profondeur.",
    distribution_zone: "Zone Sahélienne & Soudano-Sahélienne (Dori, Oursi, Gorom, Kaya)",
    photo_url: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 9.85,
      ldmc_mgg: 425.4,
      wood_density_gcm3: 0.72,
      seed_mass_mg: 3200.0,
      p50_hydraulic_mpa: -4.8,
      leaf_thickness_um: 480,
      drought_index: 95,
      fire_resistance: 70,
    },
    germination: {
      t50_days: 4.2,
      gp_ctrl_pct: 92,
      gp_peg_pct: 64,
      regime: "Scarification mécanique",
    },
    projections: {
      ssp245_2050: { change_pct: 3.8, vuln_idx: 0.0, status: "Résiliente / Stable" },
      ssp245_2080: { change_pct: -4.8, vuln_idx: 4.8, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -10.6, vuln_idx: 10.6, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: 2.2, vuln_idx: 0.0, status: "Résiliente / Stable" },
    },
    ethnobotany: {
      traditional_uses: ["Fruits comestibles anti-diabétiques", "Huile cosmétique et pharmaceutique", "Fourrage aérien de saison sèche"],
      cultural_importance: "Arbre de sauvegarde anti-famine dans le Sahel pastoral burkinabé.",
      medicinal_properties: "Riche en saponines stéroïdiques, antiparasitaire contre la bilharziose."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000002",
    scientific_name: "Adansonia digitata L.",
    accepted_name_gbif: "Adansonia digitata L.",
    gbif_usage_key: 3152220,
    family: "Malvaceae",
    genus: "Adansonia",
    vernacular_moore: "Toèga",
    vernacular_dioula: "Sira",
    vernacular_fulfulde: "Boki",
    functional_group: "Méga-arbre réserve hydrique",
    iucn_status: "LC",
    description: "Le Baobab africain, méga-arbre pachycaulique capable d'emmagasiner jusqu'à 120 000 litres d'eau dans ses tissus fibreux spongieux.",
    distribution_zone: "Parcs agroforestiers de tout le Burkina Faso (Kaya, Ziniaré, Koudougou, Bobo)",
    photo_url: "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 14.20,
      ldmc_mgg: 295.0,
      wood_density_gcm3: 0.32,
      seed_mass_mg: 450.0,
      p50_hydraulic_mpa: -1.8,
      leaf_thickness_um: 320,
      drought_index: 80,
      fire_resistance: 85,
    },
    germination: {
      t50_days: 7.5,
      gp_ctrl_pct: 88,
      gp_peg_pct: 42,
      regime: "Ébouillantage ou scarification",
    },
    projections: {
      ssp245_2050: { change_pct: -13.2, vuln_idx: 13.2, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -16.0, vuln_idx: 16.0, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -23.6, vuln_idx: 23.6, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -34.7, vuln_idx: 34.7, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Feuilles en sauce glissante (Lalo)", "Pulpe de fruit riche en vitamine C (Pain de singe)", "Cordages à base d'écorce"],
      cultural_importance: "Arbre sacré abritant les esprits ancestraux et lieu de palabres villageoises.",
      medicinal_properties: "Fébrifuge puissant, anti-diarrhéique, antioxydant majeur."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000003",
    scientific_name: "Faidherbia albida (Delile) A.Chev.",
    accepted_name_gbif: "Faidherbia albida (Delile) A.Chev.",
    gbif_usage_key: 2977465,
    family: "Fabaceae",
    genus: "Faidherbia",
    vernacular_moore: "Zaanga",
    vernacular_dioula: "Balanzan",
    vernacular_fulfulde: "Caski",
    functional_group: "Fixateur azote phénologie inversée",
    iucn_status: "LC",
    description: "Espèce agroforestière par excellence à phénologie inversée : perd ses feuilles en saison des pluies (laissant passer la lumière) et reverdit en saison sèche.",
    distribution_zone: "Terroirs agricoles soudano-sahéliens (Kaya, Ouahigouya, Yako, Koudougou)",
    photo_url: "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 16.50,
      ldmc_mgg: 340.2,
      wood_density_gcm3: 0.58,
      seed_mass_mg: 180.0,
      p50_hydraulic_mpa: -3.2,
      leaf_thickness_um: 290,
      drought_index: 85,
      fire_resistance: 60,
    },
    germination: {
      t50_days: 3.5,
      gp_ctrl_pct: 95,
      gp_peg_pct: 58,
      regime: "H2SO4 98% 15min ou scarification",
    },
    projections: {
      ssp245_2050: { change_pct: -13.1, vuln_idx: 13.1, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -13.4, vuln_idx: 13.4, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -25.3, vuln_idx: 25.3, status: "Modérément Vulnérable" },
      ssp585_2080: { change_pct: -47.0, vuln_idx: 47.0, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Fertilisation des cultures de mil/sorgho", "Gousses hélicoïdales très nutritives pour le cheptel", "Bois d'artisanat"],
      cultural_importance: "Symbole de la fertilité agro-pastorale au Sahel.",
      medicinal_properties: "Écorce fébrifuge, traitement des douleurs articulaires et maux de dents."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000004",
    scientific_name: "Vachellia tortilis (Forssk.) Galasso & Banfi",
    accepted_name_gbif: "Vachellia tortilis (Forssk.) Galasso & Banfi",
    gbif_usage_key: 2978712,
    family: "Fabaceae",
    genus: "Vachellia",
    vernacular_moore: "Gom-peelga",
    vernacular_dioula: "Danba",
    vernacular_fulfulde: "Cilluki",
    functional_group: "Épineux sahélien hyper-xérique",
    iucn_status: "LC",
    description: "L'Acacia faux-pommier en parasol, champion de la survie en milieu hyper-aride (< 300 mm de pluie) et fixateur d'azote symbiotique.",
    distribution_zone: "Zone Sahélienne stricte (Oursi, Tin-Akoff, Dori, Markoye)",
    photo_url: "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 8.45,
      ldmc_mgg: 460.5,
      wood_density_gcm3: 0.78,
      seed_mass_mg: 45.0,
      p50_hydraulic_mpa: -5.2,
      leaf_thickness_um: 440,
      drought_index: 98,
      fire_resistance: 50,
    },
    germination: {
      t50_days: 4.8,
      gp_ctrl_pct: 90,
      gp_peg_pct: 68,
      regime: "Scarification mécanique",
    },
    projections: {
      ssp245_2050: { change_pct: -3.3, vuln_idx: 3.3, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: 3.6, vuln_idx: 0.0, status: "Résiliente / Stable" },
      ssp585_2050: { change_pct: -4.2, vuln_idx: 4.2, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -3.6, vuln_idx: 3.6, status: "Faiblement Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Fourrage de prédilection des dromadaires et caprins", "Gomme comestible", "Fixation des dunes de sable"],
      cultural_importance: "Espèce phare de la Grande Muraille Verte pour lutter contre la désertification.",
      medicinal_properties: "Gomme astringente contre les diarrhées et brûlures."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000005",
    scientific_name: "Combretum glutinosum Perr. ex DC.",
    accepted_name_gbif: "Combretum glutinosum Perr. ex DC.",
    gbif_usage_key: 3188540,
    family: "Combretaceae",
    genus: "Combretum",
    vernacular_moore: "Rambolga",
    vernacular_dioula: "Doki",
    vernacular_fulfulde: "Dooki",
    functional_group: "Arbuste pyrophyle résilient",
    iucn_status: "LC",
    description: "Arbuste très commun aux feuilles glutineuses brillantes, résistant remarquablement aux feux de brousse récurrents par rejet de souche vigoureux.",
    distribution_zone: "Soudano-Sahélien et Soudanien (Kaya, Manga, Zorgho, Fada)",
    photo_url: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 12.10,
      ldmc_mgg: 380.0,
      wood_density_gcm3: 0.64,
      seed_mass_mg: 120.0,
      p50_hydraulic_mpa: -3.6,
      leaf_thickness_um: 380,
      drought_index: 78,
      fire_resistance: 92,
    },
    germination: {
      t50_days: 6.2,
      gp_ctrl_pct: 85,
      gp_peg_pct: 38,
      regime: "Trempage 24h",
    },
    projections: {
      ssp245_2050: { change_pct: -11.2, vuln_idx: 11.2, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -9.0, vuln_idx: 9.0, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -18.9, vuln_idx: 18.9, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -43.8, vuln_idx: 43.8, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Bois de chauffe et charbon de haute qualité calorifique", "Colorant jaune pour textiles et cuirs"],
      cultural_importance: "Espèce stabilisatrice des sols dégradés et jachères anciennes.",
      medicinal_properties: "Infusion diurétique, hépatoprotectrice et traitement du paludisme."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000006",
    scientific_name: "Ziziphus mauritiana Lam.",
    accepted_name_gbif: "Ziziphus mauritiana Lam.",
    gbif_usage_key: 3039423,
    family: "Rhamnaceae",
    genus: "Ziziphus",
    vernacular_moore: "Moug-noaga",
    vernacular_dioula: "Tomboron",
    vernacular_fulfulde: "Jaabi",
    functional_group: "Arbuste fruitier résistant",
    iucn_status: "LC",
    description: "Le Jujubier sauvage, arbuste épineux touffu produisant des drupes comestibles très appréciées, supportant les sécheresses prolongées.",
    distribution_zone: "Tout le Sahel et les savanes sèches (Dori, Kaya, Ouahigouya)",
    photo_url: "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 11.30,
      ldmc_mgg: 410.0,
      wood_density_gcm3: 0.69,
      seed_mass_mg: 850.0,
      p50_hydraulic_mpa: -4.1,
      leaf_thickness_um: 390,
      drought_index: 90,
      fire_resistance: 65,
    },
    germination: {
      t50_days: 5.1,
      gp_ctrl_pct: 89,
      gp_peg_pct: 54,
      regime: "Concassage du noyau",
    },
    projections: {
      ssp245_2050: { change_pct: -10.0, vuln_idx: 10.0, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -15.3, vuln_idx: 15.3, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -16.5, vuln_idx: 16.5, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -40.2, vuln_idx: 40.2, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Fruits riches en sucres et vitamine C consommés frais ou séchés", "Haies vives défensives"],
      cultural_importance: "Source clé de revenus monétaires pour les femmes rurales sur les marchés locaux.",
      medicinal_properties: "Racines fébrifuges et écorce astringente."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000007",
    scientific_name: "Sclerocarya birrea (A.Rich.) Hochst.",
    accepted_name_gbif: "Sclerocarya birrea (A.Rich.) Hochst.",
    gbif_usage_key: 3190623,
    family: "Anacardiaceae",
    genus: "Sclerocarya",
    vernacular_moore: "Noabga",
    vernacular_dioula: "Kouna",
    vernacular_fulfulde: "Eeri",
    functional_group: "Arbre fruitier savanicole",
    iucn_status: "LC",
    description: "Le Marula d'Afrique occidentale, arbre dioïque à fûts robustes produisant des fruits juteux fermentescibles riches en acide ascorbique.",
    distribution_zone: "Savanes soudano-sahéliennes (Kaya, Koupéla, Manga, Fada)",
    photo_url: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 13.80,
      ldmc_mgg: 330.0,
      wood_density_gcm3: 0.54,
      seed_mass_mg: 2400.0,
      p50_hydraulic_mpa: -2.8,
      leaf_thickness_um: 310,
      drought_index: 75,
      fire_resistance: 70,
    },
    germination: {
      t50_days: 9.8,
      gp_ctrl_pct: 82,
      gp_peg_pct: 35,
      regime: "Extraction manuelle de l'opercule",
    },
    projections: {
      ssp245_2050: { change_pct: -10.6, vuln_idx: 10.6, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -8.3, vuln_idx: 8.3, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -23.6, vuln_idx: 23.6, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -35.9, vuln_idx: 35.9, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Boissons fermentées traditionnelles", "Amandes oléagineuses", "Sculpture d'ustensiles"],
      cultural_importance: "Arbre totémique et symbole de prospérité dans les terroirs mossi et gourmantché.",
      medicinal_properties: "Écorce utilisée contre le diabète et la dysenterie amibienne."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000008",
    scientific_name: "Tamarindus indica L.",
    accepted_name_gbif: "Tamarindus indica L.",
    gbif_usage_key: 2967926,
    family: "Fabaceae",
    genus: "Tamarindus",
    vernacular_moore: "Pusga",
    vernacular_dioula: "Tomi",
    vernacular_fulfulde: "Jatami",
    functional_group: "Légumineuse fruitière sempervirente",
    iucn_status: "LC",
    description: "Le Tamarinier, grand arbre à feuillage sempervirent dense, bois exceptionnellement dur et lourd, produisant des gousses acidulées.",
    distribution_zone: "Parcs boisés et berges du centre et sud (Ouagadougou, Pô, Bobo)",
    photo_url: "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 10.60,
      ldmc_mgg: 405.0,
      wood_density_gcm3: 0.75,
      seed_mass_mg: 650.0,
      p50_hydraulic_mpa: -3.9,
      leaf_thickness_um: 360,
      drought_index: 82,
      fire_resistance: 75,
    },
    germination: {
      t50_days: 6.0,
      gp_ctrl_pct: 91,
      gp_peg_pct: 48,
      regime: "Scarification mécanique",
    },
    projections: {
      ssp245_2050: { change_pct: -14.8, vuln_idx: 14.8, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -10.5, vuln_idx: 10.5, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -24.1, vuln_idx: 24.1, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -37.8, vuln_idx: 37.8, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Jus de tamarin rafraîchissant", "Acidifiant pour bouillies", "Ombrage bienfaiteur"],
      cultural_importance: "Arbre d'ombrage communautaire au centre des places de marché.",
      medicinal_properties: "Laxatif doux, fébrifuge, antiseptique intestinal."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000009",
    scientific_name: "Senegalia senegal (L.) Britton",
    accepted_name_gbif: "Senegalia senegal (L.) Britton",
    gbif_usage_key: 2979268,
    family: "Fabaceae",
    genus: "Senegalia",
    vernacular_moore: "Gom-vëre",
    vernacular_dioula: "Dounkouri",
    vernacular_fulfulde: "Patuki",
    functional_group: "Producteur gomme arabique",
    iucn_status: "LC",
    description: "Le Gommier blanc sahélien, arbuste épineux par excellence produisant la gomme arabique dure de première qualité commerciale.",
    distribution_zone: "Zone pastorale sahélienne septentrionale (Dori, Gorom, Djibo, Oursi)",
    photo_url: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 11.90,
      ldmc_mgg: 395.0,
      wood_density_gcm3: 0.71,
      seed_mass_mg: 85.0,
      p50_hydraulic_mpa: -4.5,
      leaf_thickness_um: 350,
      drought_index: 94,
      fire_resistance: 55,
    },
    germination: {
      t50_days: 3.8,
      gp_ctrl_pct: 94,
      gp_peg_pct: 62,
      regime: "Trempage eau tiède 12h",
    },
    projections: {
      ssp245_2050: { change_pct: -12.2, vuln_idx: 12.2, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -10.0, vuln_idx: 10.0, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -15.4, vuln_idx: 15.4, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -36.9, vuln_idx: 36.9, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Production et vente de gomme arabique", "Fourrage riche pour caprins", "Fixation du cordon dunaire"],
      cultural_importance: "Filière économique stratégique d'exportation pour les communautés du nord.",
      medicinal_properties: "Adoucissant pectoral, traitement des inflammations gastro-intestinales."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000010",
    scientific_name: "Parkia biglobosa (Jacq.) R.Br. ex G.Don",
    accepted_name_gbif: "Parkia biglobosa (Jacq.) R.Br. ex G.Don",
    gbif_usage_key: 2978931,
    family: "Fabaceae",
    genus: "Parkia",
    vernacular_moore: "Roaga",
    vernacular_dioula: "Néré",
    vernacular_fulfulde: "Narehi",
    functional_group: "Arbre agroforestier d'intérêt majeur",
    iucn_status: "LC",
    description: "Le Néré, pilier alimentaire de l'Afrique de l'Ouest dont les graines fermentées produisent le Soumbala, condiment nutritionnel d'une richesse exceptionnelle.",
    distribution_zone: "Parcs à karité et néré soudano-sahéliens et soudaniens (Koudougou, Manga, Pô, Bobo)",
    photo_url: "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 15.10,
      ldmc_mgg: 310.0,
      wood_density_gcm3: 0.52,
      seed_mass_mg: 280.0,
      p50_hydraulic_mpa: -2.5,
      leaf_thickness_um: 310,
      drought_index: 68,
      fire_resistance: 65,
    },
    germination: {
      t50_days: 5.5,
      gp_ctrl_pct: 90,
      gp_peg_pct: 32,
      regime: "H2SO4 ou incision du tégument",
    },
    projections: {
      ssp245_2050: { change_pct: -10.9, vuln_idx: 10.9, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -17.7, vuln_idx: 17.7, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -23.6, vuln_idx: 23.6, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -32.3, vuln_idx: 32.3, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Transformation des graines en Soumbala", "Pulpe jaune farineuse consommée fraîche", "Teinture des poteries"],
      cultural_importance: "Patrimoine gastronomique et agroforestier inaliénable du Burkina Faso.",
      medicinal_properties: "Écorce hypotensive contre l'hypertension artérielle et maux de dents."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000011",
    scientific_name: "Pterocarpus erinaceus Poir.",
    accepted_name_gbif: "Pterocarpus erinaceus Poir.",
    gbif_usage_key: 2964893,
    family: "Fabaceae",
    genus: "Pterocarpus",
    vernacular_moore: "Noèga",
    vernacular_dioula: "Guénou",
    vernacular_fulfulde: "Bane",
    functional_group: "Bois d'oeuvre noble menacé",
    iucn_status: "EN",
    description: "Le Bois de rose d'Afrique (Keno / Vène), essence noble décidue surexploitée pour son bois de résonance (fabrication des balafons) et menacée d'extinction.",
    distribution_zone: "Forêts claires et savanes soudaniennes (Pô, Kaboré Tambi, Nazinga, Léo, Gaoua)",
    photo_url: "https://images.unsplash.com/photo-1546842931-886c185b4c8c?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 14.60,
      ldmc_mgg: 325.0,
      wood_density_gcm3: 0.68,
      seed_mass_mg: 150.0,
      p50_hydraulic_mpa: -2.4,
      leaf_thickness_um: 300,
      drought_index: 50,
      fire_resistance: 70,
    },
    germination: {
      t50_days: 8.2,
      gp_ctrl_pct: 78,
      gp_peg_pct: 22,
      regime: "Extraction des samares épineuses",
    },
    projections: {
      ssp245_2050: { change_pct: -21.1, vuln_idx: 21.1, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -21.3, vuln_idx: 21.3, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -33.2, vuln_idx: 33.2, status: "Modérément Vulnérable" },
      ssp585_2080: { change_pct: -50.5, vuln_idx: 50.5, status: "Extrêmement Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Lames de balafons de tradition mandingue", "Ébénisterie de luxe", "Fourrage de grande valeur pour ovins"],
      cultural_importance: "Instrument fondamental de la musique traditionnelle et des rituels initiatiques.",
      medicinal_properties: "Exsudat rouge astringent (sang-dragon) anti-hémorragique."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000012",
    scientific_name: "Anogeissus leiocarpa (DC.) Guill. & Perr.",
    accepted_name_gbif: "Anogeissus leiocarpa (DC.) Guill. & Perr.",
    gbif_usage_key: 3188556,
    family: "Combretaceae",
    genus: "Anogeissus",
    vernacular_moore: "Siiga",
    vernacular_dioula: "Kérékété",
    vernacular_fulfulde: "Kojoli",
    functional_group: "Essence ripicole et savanicole dense",
    iucn_status: "LC",
    description: "Le Bouleau d'Afrique, grand arbre élancé à bois très dense (0.76 g/cm³), poussant préférentiellement dans les zones de transition et le long des cours d'eau.",
    distribution_zone: "Galeries ripicoles et forêts classées du centre et sud (Dem, Pô, Nazinga)",
    photo_url: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 12.80,
      ldmc_mgg: 365.0,
      wood_density_gcm3: 0.76,
      seed_mass_mg: 35.0,
      p50_hydraulic_mpa: -3.7,
      leaf_thickness_um: 340,
      drought_index: 76,
      fire_resistance: 60,
    },
    germination: {
      t50_days: 7.0,
      gp_ctrl_pct: 72,
      gp_peg_pct: 30,
      regime: "Trempage 24h",
    },
    projections: {
      ssp245_2050: { change_pct: -9.0, vuln_idx: 9.0, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -8.5, vuln_idx: 8.5, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -19.4, vuln_idx: 19.4, status: "Faiblement Vulnérable" },
      ssp585_2080: { change_pct: -39.8, vuln_idx: 39.8, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Poteaux de construction imputrescibles", "Teinture des tissus Bogolan (tanins)", "Frotte-dents hygiénique"],
      cultural_importance: "Utilisé pour la teinture traditionnelle du coton écru en jaune/kaki.",
      medicinal_properties: "Anthelminthique puissant, antibactérien pour l'hygiène buccodentaire."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000013",
    scientific_name: "Khaya senegalensis (Desr.) A.Juss.",
    accepted_name_gbif: "Khaya senegalensis (Desr.) A.Juss.",
    gbif_usage_key: 3190474,
    family: "Meliaceae",
    genus: "Khaya",
    vernacular_moore: "Kooko",
    vernacular_dioula: "Dialo",
    vernacular_fulfulde: "Cailcédrat",
    functional_group: "Grand arbre ripicole médicinal",
    iucn_status: "VU",
    description: "L'Acajou du Sénégal ou Cailcédrat, arbre majestueux des galeries forestières vulnérable à la fragmentation de son habitat et à l'écorçage médicinal intensif.",
    distribution_zone: "Ripisylves et forêts soudaniennes (Kou, Pô, Nazinga, Banfora)",
    photo_url: "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 15.80,
      ldmc_mgg: 305.0,
      wood_density_gcm3: 0.62,
      seed_mass_mg: 70.0,
      p50_hydraulic_mpa: -2.1,
      leaf_thickness_um: 330,
      drought_index: 52,
      fire_resistance: 60,
    },
    germination: {
      t50_days: 6.5,
      gp_ctrl_pct: 85,
      gp_peg_pct: 20,
      regime: "Semis direct après récolte",
    },
    projections: {
      ssp245_2050: { change_pct: -18.5, vuln_idx: 18.5, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -22.0, vuln_idx: 22.0, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -34.8, vuln_idx: 34.8, status: "Modérément Vulnérable" },
      ssp585_2080: { change_pct: -52.4, vuln_idx: 52.4, status: "Extrêmement Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Ébénisterie de grand luxe", "Fourrage de haute valeur", "Arbre d'alignement urbain ombragé"],
      cultural_importance: "L'écorce amère est la panacée la plus réputée de la médecine traditionnelle voltaïque.",
      medicinal_properties: "Antipaludique de référence (amertume due aux khayanolides)."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000014",
    scientific_name: "Vitellaria paradoxa C.F.Gaertn.",
    accepted_name_gbif: "Vitellaria paradoxa C.F.Gaertn.",
    gbif_usage_key: 2888636,
    family: "Sapotaceae",
    genus: "Vitellaria",
    vernacular_moore: "Taanga",
    vernacular_dioula: "Si",
    vernacular_fulfulde: "Karehi",
    functional_group: "Arbre oléagineux agroforestier clé",
    iucn_status: "VU",
    description: "Le Karité, arbre d'or vert d'Afrique de l'Ouest dont les noix fournissent le beurre de karité, ressource économique majeure du Burkina Faso.",
    distribution_zone: "Parcs agroforestiers du centre et du sud (Koudougou, Manga, Bobo, Fada)",
    photo_url: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 12.40,
      ldmc_mgg: 385.0,
      wood_density_gcm3: 0.70,
      seed_mass_mg: 9500.0,
      p50_hydraulic_mpa: -3.1,
      leaf_thickness_um: 390,
      drought_index: 65,
      fire_resistance: 80,
    },
    germination: {
      t50_days: 14.5,
      gp_ctrl_pct: 75,
      gp_peg_pct: 25,
      regime: "Semis immédiat (graines récalcitrantes)",
    },
    projections: {
      ssp245_2050: { change_pct: -15.4, vuln_idx: 15.4, status: "Faiblement Vulnérable" },
      ssp245_2080: { change_pct: -19.8, vuln_idx: 19.8, status: "Faiblement Vulnérable" },
      ssp585_2050: { change_pct: -28.6, vuln_idx: 28.6, status: "Modérément Vulnérable" },
      ssp585_2080: { change_pct: -46.2, vuln_idx: 46.2, status: "Modérément Vulnérable" },
    },
    ethnobotany: {
      traditional_uses: ["Fabrication artisanale du beurre de karité", "Alimentation et cosmétique mondiale", "Consommation du fruit mûr sucré"],
      cultural_importance: "Arbre protégé par le droit coutumier; pilier de l'autonomisation économique des femmes.",
      medicinal_properties: "Cicatrisant dermique d'exception, baume décongestionnant."
    }
  },
  {
    id: "b0000000-0000-0000-0000-000000000028",
    scientific_name: "Boscia senegalensis (Pers.) Lam.",
    accepted_name_gbif: "Boscia senegalensis (Pers.) Lam.",
    gbif_usage_key: 3054115,
    family: "Capparaceae",
    genus: "Boscia",
    vernacular_moore: "Vang-pelga",
    vernacular_dioula: "Bere",
    vernacular_fulfulde: "Gigli",
    functional_group: "Arbuste vivrier anti-famine hyper-aride",
    iucn_status: "LC",
    description: "Le Boscia du Sahel, arbuste sempervirent xérophyte extrême maintenant ses feuilles vertes même lors des pires sécheresses pluriannuelles.",
    distribution_zone: "Sahel septentrional dunaire et rocailleux (Oursi, Markoye, Tin-Akoff, Dori)",
    photo_url: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",
    traits: {
      sla_mm2mg: 7.90,
      ldmc_mgg: 480.0,
      wood_density_gcm3: 0.77,
      seed_mass_mg: 1200.0,
      p50_hydraulic_mpa: -6.0,
      leaf_thickness_um: 520,
      drought_index: 99,
      fire_resistance: 75,
    },
    germination: {
      t50_days: 4.0,
      gp_ctrl_pct: 94,
      gp_peg_pct: 78,
      regime: "Scarification légère",
    },
    projections: {
      ssp245_2050: { change_pct: 5.2, vuln_idx: 0.0, status: "Résiliente / Stable" },
      ssp245_2080: { change_pct: 8.1, vuln_idx: 0.0, status: "Expansion d'aire" },
      ssp585_2050: { change_pct: 4.6, vuln_idx: 0.0, status: "Résiliente / Stable" },
      ssp585_2080: { change_pct: 12.4, vuln_idx: 0.0, status: "Expansion d'aire" },
    },
    ethnobotany: {
      traditional_uses: ["Graines détoxifiées consommées comme céréale de substitution anti-famine", "Fourrage de soudure ultime"],
      cultural_importance: "L'arbuste qui sauve des vies lors des sécheresses dévastatrices au Sahel.",
      medicinal_properties: "Purification de l'eau trouble (graines coagulantes) et soin des ophtalmies."
    }
  }
];

export const FAMILIES_LIST = Array.from(new Set(SPECIES_CATALOG.map((s) => s.family))).sort();
export const FUNCTIONAL_GROUPS = Array.from(new Set(SPECIES_CATALOG.map((s) => s.functional_group))).sort();
