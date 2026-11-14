"""
Module 1 Orchestrator: Web-Mining, Trait Harmonization & CMIP6 Climate Processing
Couche 4a : SahelTraits-DB & EcoPredict
Author: YAGO Abdoul Rachide (UJKZ - ICC)
"""

import sys
import subprocess
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.utils.logger import get_logger
from src.module1_webmining_climate.gbif_harvester import run_harvest
from src.module1_webmining_climate.try_bien_inat_harvester import build_harmonized_traits_dataset
from src.module1_webmining_climate.cmip6_raster_processor import process_and_export_rasters

logger = get_logger("Module1_Runner")

def run_module1(rscript_path: str = "Rscript"):
    logger.info("=================================================================")
    logger.info("DÉMARRAGE DU MODULE 1 : WEB-MINING, TRAITS & CLIMAT (Couche 4a)")
    logger.info("=================================================================")
    
    # Paths
    species_csv = BASE_DIR / "config" / "species_list.csv"
    raw_occ_csv = BASE_DIR / "data" / "raw" / "occurrences" / "gbif_raw_occurrences.csv"
    clean_occ_csv = BASE_DIR / "data" / "processed" / "cleaned_occurrences.csv"
    cleaning_summary_csv = BASE_DIR / "outputs" / "tables" / "module1_cleaning_summary.csv"
    traits_csv = BASE_DIR / "data" / "raw" / "traits" / "harmonized_traits.csv"
    db_path = BASE_DIR.parent / "backend" / "saheltraits_dev.db"
    climate_dir = BASE_DIR / "data" / "climate"
    rasters_out = BASE_DIR / "outputs" / "rasters"
    clean_r_script = BASE_DIR / "src" / "module1_webmining_climate" / "clean_coordinates.R"
    
    # 1. Harvest GBIF occurrences
    logger.info("[Step 1/4] Moissonnage des occurrences GBIF & iNaturalist...")
    run_harvest(species_csv, raw_occ_csv)
    
    # 2. Harmonize multi-source trait database
    logger.info("[Step 2/4] Harmonisation des traits fonctionnels (TRY, BIEN, SahelTraits-DB)...")
    build_harmonized_traits_dataset(species_csv, traits_csv, db_path)
    
    # 3. Clean occurrences with CoordinateCleaner R script
    logger.info("[Step 3/4] Nettoyage spatial des occurrences sous R (CoordinateCleaner)...")
    cmd = [
        rscript_path,
        str(clean_r_script),
        str(raw_occ_csv),
        str(clean_occ_csv),
        str(cleaning_summary_csv)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(res.stdout)
    except Exception as e:
        logger.warning(f"R CoordinateCleaner execution notice: {e}")
        # Run python fallback if Rscript fails
        import pandas as pd
        df = pd.read_csv(raw_occ_csv)
        valid = (df['decimalLatitude'] > 8.0) & (df['decimalLatitude'] < 16.5) & \
                (df['decimalLongitude'] > -6.0) & (df['decimalLongitude'] < 3.5) & \
                (df['decimalLatitude'] != 0.0) & (df['decimalLongitude'] != 0.0)
        clean_df = df[valid]
        clean_occ_csv.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(clean_occ_csv, index=False)
        logger.info(f"Fallback cleaner retained {len(clean_df)} occurrences.")
        
    # 4. Extract and process Historical & CMIP6 Future Climate Rasters
    logger.info("[Step 4/4] Traitement et extraction des rasters climatiques historiques et CMIP6...")
    process_and_export_rasters(climate_dir, rasters_out)
    
    logger.info("=================================================================")
    logger.info("MODULE 1 EXÉCUTÉ AVEC SUCCÈS : DONNÉES CLIMATIQUES & OCCURRENCES PRÊTES")
    logger.info("=================================================================")

if __name__ == "__main__":
    r_exe = "C:\\Program Files\\R\\R-4.5.1\\bin\\Rscript.exe"
    if not Path(r_exe).exists():
        r_exe = "Rscript"
    run_module1(r_exe)
