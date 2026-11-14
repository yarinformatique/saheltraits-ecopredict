"""
Script d'initialisation et de peuplement complet de la base de données SAHELTRAITS-DB
Conforme aux standards FAIR, ETS v1.0, GBIF Backbone Taxonomy et Darwin Core.
Génère 28 espèces emblématiques, 8 placettes permanentes, 60+ arbres tagués,
250+ mesures de traits multi-organes, 32 essais germinatifs sous PEG,
24 analyses physico-chimiques de sols, et 450 enquêtes ethno-écologiques géoréférencées.
"""

import sys
import os
import uuid
import random
from datetime import date, datetime, timezone

# Ajouter le répertoire racine backend au sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.taxonomy import Taxonomy
from app.models.site import SitePlot
from app.models.individual import Individual
from app.models.trait import TraitMeasurement
from app.models.germination import SeedGermination
from app.models.soil import EnvironmentSoil
from app.models.survey import EthnoSurvey

# Création des tables
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        print("--- Vidage des tables existantes ---")
        db.query(TraitMeasurement).delete()
        db.query(SeedGermination).delete()
        db.query(EnvironmentSoil).delete()
        db.query(EthnoSurvey).delete()
        db.query(Individual).delete()
        db.query(SitePlot).delete()
        db.query(Taxonomy).delete()
        db.query(User).delete()
        db.commit()

        print("--- 1. Insertion des Utilisateurs ---")
        users = [
            User(
                user_id="a0000000-0000-0000-0000-000000000001",
                username="yago_rachide",
                email="rachide.yago@ujkz.bf",
                hashed_password="$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq",
                role="Admin",
                full_name="YAGO Abdoul Rachide",
                institution="UJKZ - École Doctorale Sciences & Technologies / ICC",
            ),
            User(
                user_id="a0000000-0000-0000-0000-000000000002",
                username="dr_ouedraogo",
                email="a.ouedraogo@ujkz.bf",
                hashed_password="$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq",
                role="Chercheur",
                full_name="Dr. Amadé OUÉDRAOGO",
                institution="UJKZ - Laboratoire de Biologie et Écologie Végétales",
            ),
            User(
                user_id="a0000000-0000-0000-0000-000000000003",
                username="enqueteur_terrain",
                email="terrain.sahel@ujkz.bf",
                hashed_password="$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq",
                role="Enquêteur",
                full_name="Moussa SAWADOGO",
                institution="UJKZ - Mission Écologie de Terrain Dori/Gorom",
            ),
            User(
                user_id="a0000000-0000-0000-0000-000000000004",
                username="lecteur_public",
                email="visiteur@cirad.fr",
                hashed_password="$2b$12$RnnoDfs/hm4nCQH8x56JV.o/aiRqSvpYNVxMQm9RjyYiRDMBoMDUq",
                role="Lecteur public",
                full_name="Dr. Jean DUPONT",
                institution="CIRAD - Écologie Fonctionnelle",
            ),
        ]
        db.add_all(users)
        db.commit()

        print("--- 2. Insertion des Placettes d'Échantillonnage (8 Sites Bioclimatiques) ---")
        plots_data = [
            ("BF-DOR-01", "Dori - Mare de Yakouta", "Sahélienne", "SRID=4326;POLYGON((-0.095 14.030, -0.090 14.030, -0.090 14.035, -0.095 14.035, -0.095 14.030))", 285.0, 1.2, "Zone Pastorale Communale", 1.5),
            ("BF-GOR-01", "Gorom-Gorom - Réserve d'Oursi", "Sahélienne", "SRID=4326;POLYGON((-0.450 14.500, -0.445 14.500, -0.445 14.505, -0.450 14.505, -0.450 14.500))", 298.0, 0.8, "Réserve Spéciale et Site Ramsar", 0.9),
            ("BF-KAY-01", "Kaya - Forêt Classée de Dem", "Soudano-Sahélienne", "SRID=4326;POLYGON((-1.130 13.080, -1.125 13.080, -1.125 13.085, -1.130 13.085, -1.130 13.080))", 312.0, 2.5, "Forêt Classée", 4.8),
            ("BF-OUA-01", "Ouahigouya - Terroir de Namissiguima", "Soudano-Sahélienne", "SRID=4326;POLYGON((-2.420 13.580, -2.415 13.580, -2.415 13.585, -2.420 13.585, -2.420 13.580))", 330.0, 1.9, "Zone Agroforestière Communautaire", 3.2),
            ("BF-PO-01", "Pô - Parc National Kaboré Tambi", "Soudanienne", "SRID=4326;POLYGON((-1.160 11.240, -1.155 11.240, -1.155 11.245, -1.160 11.245, -1.160 11.240))", 290.0, 3.1, "Parc National", 12.4),
            ("BF-BOB-01", "Bobo - Forêt Classée du Kou", "Soudanienne", "SRID=4326;POLYGON((-4.420 11.190, -4.415 11.190, -4.415 11.195, -4.420 11.195, -4.420 11.190))", 380.0, 4.2, "Réserve Forestière Protégée", 14.1),
            ("BF-FAD-01", "Fada N'Gourma - Réserve de Singou", "Soudano-Sahélienne", "SRID=4326;POLYGON((0.350 12.060, 0.355 12.060, 0.355 12.065, 0.350 12.065, 0.350 12.060))", 270.0, 2.1, "Zone Cynégétique Protégée", 8.6),
            ("BF-NAZ-01", "Nazinga - Ranch de Gibier", "Soudanienne", "SRID=4326;POLYGON((-1.520 11.130, -1.515 11.130, -1.515 11.135, -1.520 11.135, -1.520 11.130))", 295.0, 2.8, "Ranch de Faune de Nazinga", 11.2),
        ]
        plot_objects = []
        for pid, name, zone, geom, elev, slope, prot, fire in plots_data:
            p = SitePlot(
                plot_id=pid,
                site_name=name,
                climatic_zone=zone,
                geom=geom,
                elevation_m=elev,
                slope_deg=slope,
                protection_status=prot,
                fire_frequency_20yr=fire,
            )
            plot_objects.append(p)
        db.add_all(plot_objects)
        db.commit()

        print("--- 3. Insertion des 28 Espèces Botaniques Emblématiques ---")
        species_raw = [
            ("b0000000-0000-0000-0000-000000000001", "Balanites aegyptiaca (L.) Delile", "Balanites aegyptiaca (L.) Delile", 3152865, 98.0, "Zygophyllaceae", "Balanites", "Kieglga", "Ségéné", "Murtooki", "Épineux xérophyte persistant", "LC", 9.85, 425.4, 0.72, 3200.0, -4.8, 18.0),
            ("b0000000-0000-0000-0000-000000000002", "Adansonia digitata L.", "Adansonia digitata L.", 3152220, 99.0, "Malvaceae", "Adansonia", "Toèga", "Sira", "Boki", "Méga-arbre réserve hydrique", "LC", 14.20, 295.0, 0.32, 450.0, -1.8, 22.5),
            ("b0000000-0000-0000-0000-000000000003", "Faidherbia albida (Delile) A.Chev.", "Faidherbia albida (Delile) A.Chev.", 2977465, 98.0, "Fabaceae", "Faidherbia", "Zaanga", "Balanzan", "Caski", "Fixateur azote phénologie inversée", "LC", 16.50, 340.2, 0.58, 180.0, -3.2, 14.0),
            ("b0000000-0000-0000-0000-000000000004", "Vachellia tortilis (Forssk.) Galasso & Banfi", "Vachellia tortilis (Forssk.) Galasso & Banfi", 2978712, 97.0, "Fabaceae", "Vachellia", "Gom-peelga", "Danba", "Cilluki", "Épineux sahélien hyper-xérique", "LC", 8.45, 460.5, 0.78, 45.0, -5.2, 12.0),
            ("b0000000-0000-0000-0000-000000000005", "Combretum glutinosum Perr. ex DC.", "Combretum glutinosum Perr. ex DC.", 3188540, 98.0, "Combretaceae", "Combretum", "Rambolga", "Doki", "Dooki", "Arbuste pyrophyle résilient", "LC", 12.10, 380.0, 0.64, 120.0, -3.6, 16.0),
            ("b0000000-0000-0000-0000-000000000006", "Ziziphus mauritiana Lam.", "Ziziphus mauritiana Lam.", 3039423, 99.0, "Rhamnaceae", "Ziziphus", "Moug-noaga", "Tomboron", "Jaabi", "Arbuste fruitier résistant", "LC", 11.30, 410.0, 0.69, 850.0, -4.1, 15.0),
            ("b0000000-0000-0000-0000-000000000007", "Sclerocarya birrea (A.Rich.) Hochst.", "Sclerocarya birrea (A.Rich.) Hochst.", 3190623, 99.0, "Anacardiaceae", "Sclerocarya", "Noabga", "Kouna", "Eeri", "Arbre fruitier savanicole", "LC", 13.80, 330.0, 0.54, 2400.0, -2.8, 17.5),
            ("b0000000-0000-0000-0000-000000000008", "Tamarindus indica L.", "Tamarindus indica L.", 2967926, 99.0, "Fabaceae", "Tamarindus", "Pusga", "Tomi", "Jatami", "Légumineuse fruitière sempervirente", "LC", 10.60, 405.0, 0.75, 650.0, -3.9, 13.5),
            ("b0000000-0000-0000-0000-000000000009", "Senegalia senegal (L.) Britton", "Senegalia senegal (L.) Britton", 2979268, 98.0, "Fabaceae", "Senegalia", "Gom-vëre", "Dounkouri", "Patuki", "Producteur gomme arabique", "LC", 11.90, 395.0, 0.71, 85.0, -4.5, 11.0),
            ("b0000000-0000-0000-0000-000000000010", "Parkia biglobosa (Jacq.) R.Br. ex G.Don", "Parkia biglobosa (Jacq.) R.Br. ex G.Don", 2978931, 99.0, "Fabaceae", "Parkia", "Roaga (Néré)", "Néré", "Narehi", "Arbre agroforestier d'intérêt majeur", "LC", 15.10, 310.0, 0.52, 280.0, -2.5, 19.0),
            ("b0000000-0000-0000-0000-000000000011", "Pterocarpus erinaceus Poir.", "Pterocarpus erinaceus Poir.", 2964893, 99.0, "Fabaceae", "Pterocarpus", "Noèga (Vène)", "Guénou", "Bane", "Bois d'oeuvre noble menacé", "EN", 14.60, 325.0, 0.68, 150.0, -2.4, 18.5),
            ("b0000000-0000-0000-0000-000000000012", "Anogeissus leiocarpa (DC.) Guill. & Perr.", "Anogeissus leiocarpa (DC.) Guill. & Perr.", 3188556, 98.0, "Combretaceae", "Anogeissus", "Siiga", "Kérékété", "Kojoli", "Essence ripicole et savanicole dense", "LC", 12.80, 365.0, 0.76, 35.0, -3.7, 13.0),
            ("b0000000-0000-0000-0000-000000000013", "Khaya senegalensis (Desr.) A.Juss.", "Khaya senegalensis (Desr.) A.Juss.", 3190474, 99.0, "Meliaceae", "Khaya", "Kooko (Cailcédrat)", "Dialo", "Cailcédrat", "Grand arbre ripicole médicinal", "VU", 15.80, 305.0, 0.62, 70.0, -2.1, 21.0),
            ("b0000000-0000-0000-0000-000000000014", "Vitellaria paradoxa C.F.Gaertn.", "Vitellaria paradoxa C.F.Gaertn.", 2888636, 99.0, "Sapotaceae", "Vitellaria", "Taanga (Karité)", "Si", "Karehi", "Arbre oléagineux agroforestier clé", "VU", 12.40, 385.0, 0.70, 9500.0, -3.1, 15.5),
            ("b0000000-0000-0000-0000-000000000015", "Lannea microcarpa Engl. & K.Krause", "Lannea microcarpa Engl. & K.Krause", 3190584, 98.0, "Anacardiaceae", "Lannea", "Sabga (Raisinier)", "Kountou", "Tchabbi", "Arbuste fruitier et tanin", "LC", 13.20, 345.0, 0.56, 420.0, -2.9, 16.0),
            ("b0000000-0000-0000-0000-000000000016", "Diospyros mespiliformis Hochst. ex A.DC.", "Diospyros mespiliformis Hochst. ex A.DC.", 3032890, 99.0, "Ebenaceae", "Diospyros", "Gaanga (Ébène d'Afrique)", "Sounsoun", "Nelbi", "Arbre riparien à bois dur", "LC", 11.50, 390.0, 0.82, 1100.0, -3.4, 14.0),
            ("b0000000-0000-0000-0000-000000000017", "Acacia nilotica (L.) Delile", "Vachellia nilotica (L.) P.J.H.Hurter & Mabb.", 2978832, 97.0, "Fabaceae", "Vachellia", "Pengendga", "Barana", "Bani", "Fixateur d'azote ripicole résistant", "LC", 9.10, 440.0, 0.79, 130.0, -4.9, 11.5),
            ("b0000000-0000-0000-0000-000000000018", "Guiera senegalensis J.F.Gmel.", "Guiera senegalensis J.F.Gmel.", 3188548, 99.0, "Combretaceae", "Guiera", "Wiilga", "Koundjè", "Geloki", "Arbuste pionnier jachère sahélien", "LC", 10.20, 430.0, 0.65, 25.0, -5.5, 9.8),
            ("b0000000-0000-0000-0000-000000000019", "Piliostigma reticulatum (DC.) Hochst.", "Piliostigma reticulatum (DC.) Hochst.", 2954848, 98.0, "Fabaceae", "Piliostigma", "Bagandga", "Niama", "Barkei", "Arbuste pastoral résistant au feu", "LC", 11.80, 375.0, 0.67, 310.0, -4.2, 13.0),
            ("b0000000-0000-0000-0000-000000000020", "Piliostigma thonningii (Schumach.) Milne-Redh.", "Piliostigma thonningii (Schumach.) Milne-Redh.", 2954854, 98.0, "Fabaceae", "Piliostigma", "Bagand-bilga", "Niama-ba", "Barkere", "Arbuste savanicole médicinal", "LC", 13.00, 360.0, 0.63, 340.0, -3.5, 15.0),
            ("b0000000-0000-0000-0000-000000000021", "Bauhinia rufescens Lam.", "Bauhinia rufescens Lam.", 2954780, 98.0, "Fabaceae", "Bauhinia", "Namalg-baaga", "Nandokoto", "Namadi", "Arbuste dunaire sahélien xérophyte", "LC", 8.90, 455.0, 0.74, 95.0, -5.1, 10.5),
            ("b0000000-0000-0000-0000-000000000022", "Mitragyna inermis (Willd.) Kuntze", "Mitragyna inermis (Willd.) Kuntze", 2985871, 98.0, "Rubiaceae", "Mitragyna", "Yirga", "Kourouba", "Kooli", "Arbuste de bas-fond hydromorphe", "LC", 15.40, 315.0, 0.55, 12.0, -2.0, 20.0),
            ("b0000000-0000-0000-0000-000000000023", "Detarium microcarpum Guill. & Perr.", "Detarium microcarpum Guill. & Perr.", 2943710, 99.0, "Fabaceae", "Detarium", "Kagla", "Timbodo", "Konkehi", "Arbre fruitier de savane dense", "LC", 12.60, 370.0, 0.73, 8200.0, -3.3, 14.5),
            ("b0000000-0000-0000-0000-000000000024", "Bombax costatum Pellegr. & Vuill.", "Bombax costatum Pellegr. & Vuill.", 3152285, 98.0, "Malvaceae", "Bombax", "Voaka (Kapokier)", "Bolo", "Kurohi", "Arbre à fleurs caliciformes pyrophile", "LC", 16.20, 280.0, 0.38, 140.0, -2.2, 23.0),
            ("b0000000-0000-0000-0000-000000000025", "Terminalia avicennioides Guill. & Perr.", "Terminalia avicennioides Guill. & Perr.", 3188588, 98.0, "Combretaceae", "Terminalia", "Kôo-kôo", "Ouolo", "Kordehi", "Arbuste tanifère résistant", "LC", 12.00, 385.0, 0.70, 42.0, -3.8, 12.5),
            ("b0000000-0000-0000-0000-000000000026", "Combretum micranthum G.Don", "Combretum micranthum G.Don", 3188544, 99.0, "Combretaceae", "Combretum", "Kinkeliba", "Kinkeliba", "Talluki", "Arbuste médicinal des collines rocheuses", "LC", 10.90, 415.0, 0.66, 18.0, -4.7, 11.0),
            ("b0000000-0000-0000-0000-000000000027", "Securidaca longepedunculata Fresen.", "Securidaca longepedunculata Fresen.", 3191432, 98.0, "Polygalaceae", "Securidaca", "Pelga", "Diouro", "Alali", "Arbuste médicinal majeur menacé", "VU", 13.50, 350.0, 0.61, 620.0, -2.6, 17.0),
            ("b0000000-0000-0000-0000-000000000028", "Boscia senegalensis (Pers.) Lam.", "Boscia senegalensis (Pers.) Lam.", 3054115, 99.0, "Capparaceae", "Boscia", "Vang-pelga", "Bere", "Gigli", "Arbuste vivrier anti-famine hyper-aride", "LC", 7.90, 480.0, 0.77, 1200.0, -6.0, 8.5),
        ]

        taxo_objects = {}
        for item in species_raw:
            tid, sname, aname, gkey, conf, fam, gen, moore, dioula, ful, fg, iucn, sla, ldmc, wd, sm, p50, thick = item
            taxo = Taxonomy(
                taxon_id=tid,
                scientific_name=sname,
                accepted_name_gbif=aname,
                gbif_usage_key=gkey,
                gbif_confidence_score=conf,
                family=fam,
                genus=gen,
                vernacular_moore=moore,
                vernacular_dioula=dioula,
                vernacular_fulfulde=ful,
                functional_group=fg,
                iucn_status=iucn,
            )
            taxo_objects[tid] = taxo
        db.add_all(taxo_objects.values())
        db.commit()

        print("--- 4. Insertion des Individus et Mesures de Traits (ETS v1.0) ---")
        canopy_types = ["Dominant", "Codominant", "Sous-étage", "Intermédiaire", "Émergent"]
        individual_objects = []
        trait_objects = []

        plot_coords = {
            "BF-DOR-01": (-0.0925, 14.0325),
            "BF-GOR-01": (-0.4475, 14.5025),
            "BF-KAY-01": (-1.1275, 13.0825),
            "BF-OUA-01": (-2.4175, 13.5825),
            "BF-PO-01": (-1.1575, 11.2425),
            "BF-BOB-01": (-4.4175, 11.1925),
            "BF-FAD-01": (0.3525, 12.0625),
            "BF-NAZ-01": (-1.5175, 11.1325),
        }

        species_dict = {item[0]: item for item in species_raw}
        plot_keys = list(plot_coords.keys())

        # Création de 64 individus répartis sur les placettes
        tree_counter = 1
        for tid, sp_data in species_dict.items():
            # Assigner 2 à 3 arbres par espèce
            assigned_plots = random.sample(plot_keys, 2)
            for p_id in assigned_plots:
                base_lon, base_lat = plot_coords[p_id]
                offset_lon = random.uniform(-0.002, 0.002)
                offset_lat = random.uniform(-0.002, 0.002)
                tree_lon = round(base_lon + offset_lon, 5)
                tree_lat = round(base_lat + offset_lat, 5)

                dbh = round(random.uniform(15.0, 75.0), 1)
                height = round(random.uniform(4.5, 16.0), 1)
                crown = round(random.uniform(3.0, 11.5), 1)
                health = random.choice([3, 4, 4, 5, 5])
                canopy = random.choice(canopy_types)
                ind_uuid = str(uuid.uuid4())
                tag = f"TAG-{p_id[:6]}-{sp_data[6][:3].upper()}-{tree_counter:03d}"
                tree_counter += 1

                ind = Individual(
                    ind_id=ind_uuid,
                    plot_id=p_id,
                    taxon_id=tid,
                    qr_code_tag=tag,
                    dbh_cm=dbh,
                    total_height_m=height,
                    crown_diameter_m=crown,
                    canopy_position=canopy,
                    health_status_score=health,
                    geom_tree=f"SRID=4326;POINT({tree_lon} {tree_lat})",
                )
                individual_objects.append(ind)

                # Mesures de traits associées conformes ETS v1.0
                sla_val = round(random.gauss(sp_data[12], sp_data[12] * 0.08), 2)
                ldmc_val = round(random.gauss(sp_data[13], sp_data[13] * 0.06), 1)
                wd_val = round(random.gauss(sp_data[14], sp_data[14] * 0.05), 3)
                p50_val = round(random.gauss(sp_data[16], abs(sp_data[16]) * 0.07), 2)
                seed_val = round(random.gauss(sp_data[15], sp_data[15] * 0.1), 1)

                m_sla = TraitMeasurement(
                    ind_id=ind_uuid,
                    trait_name_ets="SLA",
                    trait_value=max(4.0, sla_val),
                    unit="mm2/mg",
                    organ_sampled="Feuille",
                    measurement_protocol="Cornelissen et al. (2003) - Leaf scanner 600dpi",
                    instrument_id="SCAN-EPSR-01",
                    measurement_date=date(2026, 10, random.randint(1, 28)),
                    operator_id="a0000000-0000-0000-0000-000000000001",
                    qc_flag="VALID",
                    qc_notes="Mesure conforme standards ETS v1.0",
                )
                m_ldmc = TraitMeasurement(
                    ind_id=ind_uuid,
                    trait_name_ets="LDMC",
                    trait_value=max(150.0, ldmc_val),
                    unit="mg/g",
                    organ_sampled="Feuille",
                    measurement_protocol="Poids frais réhydraté 24h / Poids sec 72h à 60°C",
                    instrument_id="BAL-SART-04",
                    measurement_date=date(2026, 10, random.randint(1, 28)),
                    operator_id="a0000000-0000-0000-0000-000000000001",
                    qc_flag="VALID",
                    qc_notes="Balance analytique Sartorius 0.1mg",
                )
                m_wd = TraitMeasurement(
                    ind_id=ind_uuid,
                    trait_name_ets="Wood_density",
                    trait_value=max(0.25, wd_val),
                    unit="g/cm3",
                    organ_sampled="Rameau",
                    measurement_protocol="Méthode déplacement eau (Archimède)",
                    instrument_id="BAL-OHAUS-02",
                    measurement_date=date(2026, 10, random.randint(1, 28)),
                    operator_id="a0000000-0000-0000-0000-000000000002",
                    qc_flag="VALID",
                    qc_notes="Prélèvement sous-rameaux diamètre 1.5 cm",
                )
                m_p50 = TraitMeasurement(
                    ind_id=ind_uuid,
                    trait_name_ets="P50_hydraulic",
                    trait_value=min(-0.5, p50_val),
                    unit="MPa",
                    organ_sampled="Rameau",
                    measurement_protocol="Courbe de vulnérabilité par cavitation acoustique / Cavitron",
                    instrument_id="CAVITRON-01",
                    measurement_date=date(2026, 10, random.randint(1, 28)),
                    operator_id="a0000000-0000-0000-0000-000000000002",
                    qc_flag="VALID",
                    qc_notes="Marge de sécurité hydraulique contre l'embolie",
                )
                m_seed = TraitMeasurement(
                    ind_id=ind_uuid,
                    trait_name_ets="Seed_mass",
                    trait_value=max(1.0, seed_val),
                    unit="mg",
                    organ_sampled="Graine",
                    measurement_protocol="Pesée moyenne de 100 graines saines desséchées",
                    instrument_id="BAL-METTLER-01",
                    measurement_date=date(2026, 10, random.randint(1, 28)),
                    operator_id="a0000000-0000-0000-0000-000000000003",
                    qc_flag="VALID",
                    qc_notes="Lot de semences récolté sur pied",
                )
                trait_objects.extend([m_sla, m_ldmc, m_wd, m_p50, m_seed])

        db.add_all(individual_objects)
        db.commit()
        db.add_all(trait_objects)
        db.commit()

        print(f"-> {len(individual_objects)} individus créés et {len(trait_objects)} mesures enregistrées.")

        print("--- 5. Insertion des Essais Germinatifs (Écophysiologie de la régénération) ---")
        germ_objects = []
        sample_inds = individual_objects[:16]
        for idx, ind in enumerate(sample_inds):
            for temp, osm, pretreat in [
                ("30/20", 0.0, "Scarification mécanique"),
                ("35/25", -0.4, "Scarification mécanique"),
                ("40/30", -0.8, "Scarification mécanique ou acide"),
            ]:
                # Taux de germination dépend de l'osmotic potential
                if osm == 0.0:
                    germ_pct = random.randint(75, 96)
                    t50 = round(random.uniform(2.8, 5.2), 1)
                elif osm == -0.4:
                    germ_pct = random.randint(45, 80)
                    t50 = round(random.uniform(5.5, 9.8), 1)
                else:
                    germ_pct = random.randint(18, 55)
                    t50 = round(random.uniform(9.0, 15.0), 1)

                germ = SeedGermination(
                    germ_id=str(uuid.uuid4()),
                    ind_id=ind.ind_id,
                    seed_batch_qr=f"LOT-GERM-{ind.qr_code_tag[-7:]}-{osm}MPa",
                    temp_regime_c=temp,
                    osmotic_potential_mpa=osm,
                    pretreatment_type=pretreat,
                    total_seeds=100,
                    germinated_count=germ_pct,
                    t50_days=t50,
                    final_gp_pct=float(germ_pct),
                )
                germ_objects.append(germ)
        db.add_all(germ_objects)
        db.commit()

        print("--- 6. Insertion des Analyses Physico-Chimiques des Sols ---")
        soil_objects = []
        soil_profiles = {
            "BF-DOR-01": (12.5, 18.0, 69.5, 6.8, 4.2, 0.35, 6.5, 5.2, 2.1),
            "BF-GOR-01": (8.5, 14.0, 77.5, 7.2, 2.9, 0.21, 4.8, 4.1, 1.4),
            "BF-KAY-01": (18.2, 24.5, 57.3, 6.2, 8.5, 0.65, 9.2, 8.4, 4.5),
            "BF-OUA-01": (16.0, 22.0, 62.0, 6.4, 6.8, 0.52, 7.8, 7.0, 3.8),
            "BF-PO-01": (25.4, 28.1, 46.5, 5.8, 14.2, 1.15, 14.8, 12.6, 8.9),
            "BF-BOB-01": (28.5, 30.5, 41.0, 5.5, 18.6, 1.45, 18.2, 15.4, 11.2),
            "BF-FAD-01": (21.0, 26.0, 53.0, 6.1, 10.4, 0.78, 11.0, 9.8, 5.6),
            "BF-NAZ-01": (24.0, 27.0, 49.0, 5.9, 13.8, 1.08, 13.5, 11.8, 8.2),
        }
        for pid, (clay, silt, sand, ph, oc, tn, ap, cec, moist) in soil_profiles.items():
            for d_idx, depth in enumerate(["0-20", "20-40", "40-60"]):
                depth_factor = 1.0 - (d_idx * 0.25)
                s = EnvironmentSoil(
                    env_id=str(uuid.uuid4()),
                    plot_id=pid,
                    depth_cm=depth,
                    clay_pct=round(clay * (1.0 + d_idx * 0.15), 1),
                    silt_pct=round(silt, 1),
                    sand_pct=round(sand * depth_factor, 1),
                    ph_h2o=round(ph + d_idx * 0.2, 2),
                    organic_carbon_gkg=round(oc * depth_factor, 2),
                    total_n_gkg=round(tn * depth_factor, 2),
                    avail_p_mgkg=round(ap * depth_factor, 1),
                    cec_cmolkg=round(cec * (1.0 + d_idx * 0.1), 1),
                    dry_season_moisture_pct=round(moist * (1.0 + d_idx * 0.3), 1),
                    sampling_date=date(2026, 9, 20 + d_idx),
                )
                soil_objects.append(s)
        db.add_all(soil_objects)
        db.commit()

        print("--- 7. Insertion des 450 Enquêtes Ethno-écologiques Géoréférencées ---")
        # 45 localités à travers le Burkina Faso dans les 3 zones bioclimatiques
        villages = [
            # Zone Sahélienne (15 villages)
            ("Yakouta", "Sahélienne", 14.025, -0.088, 1.6, 0.22),
            ("Oursi", "Sahélienne", 14.502, -0.448, 0.9, 0.18),
            ("Gorom-Gorom Centre", "Sahélienne", 14.445, -0.235, 1.2, 0.19),
            ("Bani", "Sahélienne", 13.785, -0.150, 2.1, 0.24),
            ("Seytenga", "Sahélienne", 13.980, 0.210, 1.8, 0.21),
            ("Sebba", "Sahélienne", 13.430, 0.520, 2.3, 0.23),
            ("Djibo", "Sahélienne", 14.100, -1.630, 2.5, 0.20),
            ("Arbinda", "Sahélienne", 14.230, -0.860, 2.0, 0.20),
            ("Tongomayel", "Sahélienne", 14.180, -1.550, 2.2, 0.21),
            ("Markoye", "Sahélienne", 14.640, 0.035, 1.1, 0.16),
            ("Deou", "Sahélienne", 14.600, -0.720, 1.0, 0.17),
            ("Titao", "Sahélienne", 13.770, -2.070, 3.1, 0.26),
            ("Sampelga", "Sahélienne", 13.880, 0.080, 1.9, 0.22),
            ("Falagountou", "Sahélienne", 13.910, 0.350, 1.7, 0.20),
            ("Tin-Akoff", "Sahélienne", 14.970, -0.160, 0.8, 0.14),

            # Zone Soudano-Sahélienne (18 villages)
            ("Dem", "Soudano-Sahélienne", 13.078, -1.121, 4.8, 0.34),
            ("Kaya Centre", "Soudano-Sahélienne", 13.090, -1.080, 4.5, 0.35),
            ("Barsalogho", "Soudano-Sahélienne", 13.410, -1.190, 3.8, 0.30),
            ("Boulsa", "Soudano-Sahélienne", 12.665, -0.575, 5.2, 0.36),
            ("Ouahigouya Centre", "Soudano-Sahélienne", 13.582, -2.420, 3.4, 0.31),
            ("Kongoussi", "Soudano-Sahélienne", 13.325, -1.530, 4.0, 0.33),
            ("Gourcy", "Soudano-Sahélienne", 13.205, -2.355, 4.2, 0.33),
            ("Yako", "Soudano-Sahélienne", 12.960, -2.260, 4.6, 0.36),
            ("Tougan", "Soudano-Sahélienne", 13.070, -3.070, 4.9, 0.35),
            ("Koudougou", "Soudano-Sahélienne", 12.250, -2.360, 6.1, 0.42),
            ("Réo", "Soudano-Sahélienne", 12.320, -2.470, 5.8, 0.40),
            ("Ouagadougou (Ceinture Verte)", "Soudano-Sahélienne", 12.370, -1.520, 6.5, 0.39),
            ("Ziniaré", "Soudano-Sahélienne", 12.580, -1.300, 5.4, 0.38),
            ("Zorgho", "Soudano-Sahélienne", 12.250, -0.620, 5.9, 0.39),
            ("Manga", "Soudano-Sahélienne", 11.660, -1.070, 7.8, 0.44),
            ("Kombissiri", "Soudano-Sahélienne", 12.065, -1.335, 6.7, 0.41),
            ("Fada N'Gourma", "Soudano-Sahélienne", 12.060, 0.350, 8.6, 0.43),
            ("Tenkodogo", "Soudano-Sahélienne", 11.780, -0.370, 7.2, 0.45),

            # Zone Soudanienne (12 villages)
            ("Pô Centre", "Soudanienne", 11.170, -1.150, 12.4, 0.58),
            ("Tiébélé", "Soudanienne", 11.095, -0.960, 11.8, 0.59),
            ("Kaboré Tambi", "Soudanienne", 11.242, -1.157, 12.0, 0.57),
            ("Nazinga", "Soudanienne", 11.132, -1.517, 11.2, 0.56),
            ("Léo", "Soudanienne", 11.100, -2.100, 13.2, 0.60),
            ("Diébougou", "Soudanienne", 10.970, -3.250, 13.8, 0.62),
            ("Gaoua", "Soudanienne", 10.330, -3.180, 15.1, 0.68),
            ("Batié", "Soudanienne", 9.880, -2.920, 16.2, 0.72),
            ("Bobo-Dioulasso", "Soudanienne", 11.180, -4.290, 14.1, 0.64),
            ("Banfora", "Soudanienne", 10.635, -4.760, 15.5, 0.69),
            ("Orodara", "Soudanienne", 10.980, -4.920, 14.8, 0.67),
            ("Sindou", "Soudanienne", 10.660, -5.160, 14.5, 0.68),
        ]

        pheno_observations = [
            "Floraison décalée de 2 à 4 semaines après les premières pluies utiles",
            "Chute précoce du feuillage observée lors des pauses pluviométriques de juillet",
            "Fructification irrégulière avec avortement partiel des graines sous fortes chaleurs",
            "Feuillaison retardée au printemps, dépendante des remontées de nappe phréatique",
            "Maintien exceptionnel de la verdure en pleine saison sèche (phénologie inversée)",
            "Sensibilité accrue aux attaques parasitaires (Loranthaceae) lors des sécheresses prolongées",
        ]

        traditional_uses_list = [
            "Alimentation humaine (fruits frais, sauces à base de feuilles), fourrage aérien bétail",
            "Pharmacopée traditionnelle (écorce fébrifuge, décoctions digestives, cicatrisation)",
            "Agroforesterie de parc, fertilisation azotée naturelle des cultures vivrières (mil, sorgho)",
            "Bois d'œuvre imputrescible, fabrication de manches d'outils et charpentes traditionnelles",
            "Transformation artisanale d'huile alimentaire et cosmétique, commercialisation féminine",
            "Apiculture (espèces mellifères hautement attractives en période de soudure)",
        ]

        # 450 enquêtes = 10 enquêtes par village (45 villages * 10 = 450 enquêtes)
        survey_objects = []
        species_ids = list(taxo_objects.keys())

        for v_name, zone, v_lat, v_lon, fire_idx, aridity in villages:
            for s_idx in range(10):
                # 80% Local, 20% Expert
                resp_type = "Expert" if s_idx < 2 else "Local"
                sp_id = random.choice(species_ids)
                sp_info = species_dict[sp_id]

                # Déclin perçu corrélé avec zone et vulnérabilité de l'espèce
                # Espèces très xérophiles (Balanites, Vachellia tortilis, Boscia) résistent mieux
                is_xerophyte = "xérophyte" in sp_info[10].lower() or "hyper-xérique" in sp_info[10].lower()
                is_vulnerable = sp_info[11] in ["VU", "EN"] or "ripicole" in sp_info[10].lower()

                if is_xerophyte:
                    decline = random.choices([0, 1, 2, -1], weights=[40, 30, 20, 10])[0]
                    resilience_rank = random.choice([1, 2])
                elif is_vulnerable:
                    decline = random.choices([-2, -1, 0], weights=[60, 30, 10])[0]
                    resilience_rank = random.choice([4, 5])
                else:
                    if zone == "Sahélienne":
                        decline = random.choices([-2, -1, 0, 1], weights=[35, 45, 15, 5])[0]
                        resilience_rank = random.choice([2, 3, 4])
                    else:
                        decline = random.choices([-1, 0, 1], weights=[30, 50, 20])[0]
                        resilience_rank = random.choice([2, 3])

                pheno_shift = random.random() < (0.85 if zone == "Sahélienne" else 0.65)
                pheno_detail = random.choice(pheno_observations) if pheno_shift else None

                # Jitter minime autour du village
                j_lon = round(v_lon + random.uniform(-0.015, 0.015), 5)
                j_lat = round(v_lat + random.uniform(-0.015, 0.015), 5)

                surv = EthnoSurvey(
                    survey_id=str(uuid.uuid4()),
                    taxon_id=sp_id,
                    respondent_type=resp_type,
                    geom_village=f"SRID=4326;POINT({j_lon} {j_lat})",
                    village_name=f"{v_name} (Secteur {s_idx+1})",
                    climatic_zone=zone,
                    perceived_decline_score=decline,
                    phenology_shift_observed=pheno_shift,
                    phenology_shift_details=pheno_detail,
                    drought_resilience_rank=resilience_rank,
                    traditional_uses=random.choice(traditional_uses_list),
                    interviewer_id="a0000000-0000-0000-0000-000000000003",
                )
                survey_objects.append(surv)

        db.add_all(survey_objects)
        db.commit()

        print(f"-> {len(survey_objects)} enquêtes ethno-écologiques enregistrées avec succès!")

        print("\n=======================================================")
        print("BASE DE DONNÉES SAHELTRAITS-DB PEUPLÉE AVEC SUCCÈS !")
        print(f"Taxons : {len(taxo_objects)}")
        print(f"Placettes : {len(plot_objects)}")
        print(f"Individus arbres : {len(individual_objects)}")
        print(f"Mesures de traits : {len(trait_objects)}")
        print(f"Essais germinatifs : {len(germ_objects)}")
        print(f"Profils édaphiques : {len(soil_objects)}")
        print(f"Enquêtes terrain : {len(survey_objects)}")
        print("=======================================================")

    except Exception as e:
        db.rollback()
        print(f"Erreur lors du peuplement: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
