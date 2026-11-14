#!/usr/bin/env Rscript
# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MASTER RUNNER R (Couche 4a)
# Exécute l'intégralité des modules statistiques de la thèse sous R
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

cat("\n================================================================================\n")
cat("   SAHELTRAITS-DB & ECOPREDICT : PIPELINE STATISTIQUE GLOBAL (Couche 4a R)      \n")
cat("   Thèse de Doctorat : Écologie Fonctionnelle & Bio-informatique (2026-2029)    \n")
cat("   Maître d'Ouvrage : YAGO Abdoul Rachide (UJKZ - ICC)                          \n")
cat("================================================================================\n\n")

get_base_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    script_p <- normalizePath(sub("--file=", "", file_arg))
    return(normalizePath(dirname(script_p)))
  }
  return(normalizePath(getwd()))
}

base_dir <- get_base_dir()

# Vérification et initialisation de l'environnement parallèle
source(file.path(base_dir, "src", "utils", "parallel_config.R"))
setup_parallel_backend()

# 1. Module 2 : IndVal, lme4, DHARMa, RDPI, Germination
cat("\n>>> EXÉCUTION DU MODULE 2 (IndVal, Plasticité & Germination) <<<\n")
source(file.path(base_dir, "src", "module2_indval_plasticity", "run_module2.R"))

# 2. Module 3 : ACP, mFD, RLQ, Quatrième Coin
cat("\n>>> EXÉCUTION DU MODULE 3 (Syndromes Fonctionnels, mFD & RLQ) <<<\n")
source(file.path(base_dir, "src", "module3_syndromes_rlq", "run_module3.R"))

# 3. Module 4 : Phylogénie, Hmsc JSDM, biomod2 & CMIP6
cat("\n>>> EXÉCUTION DU MODULE 4 (Trait-based JSDM, biomod2 & CMIP6) <<<\n")
source(file.path(base_dir, "src", "module4_jsdm_biomod", "run_module4.R"))

cat("\n================================================================================\n")
cat("   TOUS LES MODULES R ONT ÉTÉ EXÉCUTÉS AVEC SUCCÈS !                           \n")
cat("   Rapports et figures enregistrés dans 'outputs/'                             \n")
cat("================================================================================\n")
