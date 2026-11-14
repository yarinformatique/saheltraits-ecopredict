#!/usr/bin/env python3
"""
SahelTraits-DB & EcoPredict : Master Pipeline Orchestrator (Couche 4a)
Projet de Recherche : Thèse de Doctorat (2026-2029)
Maître d'ouvrage : YAGO Abdoul Rachide (UJKZ - ICC)

CLI Usage:
    python run_pipeline.py --all
    python run_pipeline.py --module 1
    python run_pipeline.py --module 2
    python run_pipeline.py --module 3
    python run_pipeline.py --module 4
    python run_pipeline.py --test
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.utils.logger import get_logger

logger = get_logger("Master_Pipeline")

def find_rscript() -> str:
    candidates = [
        "C:\\Program Files\\R\\R-4.5.1\\bin\\Rscript.exe",
        "C:\\Program Files\\R\\R-4.4.1\\bin\\Rscript.exe",
        "Rscript"
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return "Rscript"

def run_cmd(cmd, desc):
    logger.info(f"==> Démarrage : {desc}")
    res = subprocess.run(cmd, check=True)
    logger.info(f"==> Succès : {desc}\n")
    return res

def main():
    parser = argparse.ArgumentParser(
        description="SahelTraits-DB & EcoPredict Couche 4a Reproducible Bio-Statistical Pipeline"
    )
    parser.add_argument("--all", action="store_true", help="Exécuter tous les modules (1 à 4) de bout en bout")
    parser.add_argument("--module", type=int, choices=[1, 2, 3, 4], help="Exécuter un module spécifique (1, 2, 3, ou 4)")
    parser.add_argument("--test", action="store_true", help="Exécuter la suite de tests automatisés pytest & testthat")
    parser.add_argument("--rscript", type=str, default=None, help="Chemin spécifique vers l'exécutable Rscript")

    args = parser.parse_args()
    
    rscript_exe = args.rscript or find_rscript()
    python_exe = sys.executable

    logger.info("================================================================================")
    logger.info("   SAHELTRAITS-DB & ECOPREDICT : PIPELINE STATISTIQUE & JSDM/CMIP6 (Couche 4a)  ")
    logger.info("   Thèse de Doctorat : Écologie Fonctionnelle & Bio-informatique (2026-2029)     ")
    logger.info("   Doctorant / Maître d'Ouvrage : YAGO Abdoul Rachide (UJKZ - ICC)              ")
    logger.info("================================================================================")
    logger.info(f"Environnement Python : {python_exe}")
    logger.info(f"Environnement R      : {rscript_exe}")
    logger.info(f"Répertoire racine   : {BASE_DIR}")
    logger.info("--------------------------------------------------------------------------------\n")

    if args.test:
        logger.info("Lancement de la suite de tests d'intégration...")
        test_script = BASE_DIR / "tests" / "test_integration_pipeline.py"
        run_cmd([python_exe, str(test_script)], "Tests d'intégration du pipeline")
        return

    run_all = args.all or (args.module is None)

    # MODULE 1
    if run_all or args.module == 1:
        mod1_script = BASE_DIR / "src" / "module1_webmining_climate" / "run_module1.py"
        run_cmd([python_exe, str(mod1_script)], "Module 1 : Web-Mining, Traits & Climat CMIP6")

    # MODULE 2
    if run_all or args.module == 2:
        mod2_script = BASE_DIR / "src" / "module2_indval_plasticity" / "run_module2.R"
        run_cmd([rscript_exe, str(mod2_script)], "Module 2 : IndVal, Modèles Mixtes lme4, DHARMa, RDPI & Germination")

    # MODULE 3
    if run_all or args.module == 3:
        mod3_script = BASE_DIR / "src" / "module3_syndromes_rlq" / "run_module3.R"
        run_cmd([rscript_exe, str(mod3_script)], "Module 3 : Syndromes Fonctionnels ACP, mFD, Couplage RLQ & Quatrième Coin")

    # MODULE 4
    if run_all or args.module == 4:
        mod4_script = BASE_DIR / "src" / "module4_jsdm_biomod" / "run_module4.R"
        run_cmd([rscript_exe, str(mod4_script)], "Module 4 : Phylogénie, JSDM Hmsc, biomod2 & Vulnérabilité CMIP6")

    logger.info("================================================================================")
    logger.info("   EXÉCUTION DU PIPELINE COUCHE 4a ACHEVÉE AVEC SUCCÈS À 100 % (REPRODUCIBLE)  ")
    logger.info("   Figures haute résolution (300 dpi) : outputs/figures/                        ")
    logger.info("   Rasters GeoTIFF pour le portail web : outputs/rasters/                       ")
    logger.info("   Tables statistiques exportées       : outputs/tables/                        ")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()
