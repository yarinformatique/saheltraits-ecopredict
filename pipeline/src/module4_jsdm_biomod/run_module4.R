# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : EXÉCUTION INTÉGRALE DU MODULE 4 (Couche 4a)
# Module 4 : Modélisation Conjointe (Trait-based JSDM) & Ensemble SDM (CMIP6)
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

cat("=================================================================\n")
cat("D\u00c9MARRAGE DU MODULE 4 : PHYLOG\u00c9NIE, JSDM Hmsc, biomod2 & CMIP6\n")
cat("=================================================================\n")

get_base_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("--file=", args, value = TRUE)
  if (length(file_arg) > 0) {
    script_p <- normalizePath(sub("--file=", "", file_arg))
    return(normalizePath(file.path(dirname(script_p), "..", "..")))
  }
  return(normalizePath(getwd()))
}

base_dir <- get_base_dir()

# Chargement des scripts du Module 4
source(file.path(base_dir, "src", "module4_jsdm_biomod", "01_phylogenetic_tree.R"))
source(file.path(base_dir, "src", "module4_jsdm_biomod", "02_hmsc_mcmc_calibration.R"))
source(file.path(base_dir, "src", "module4_jsdm_biomod", "03_hmsc_diagnostics_variance.R"))
source(file.path(base_dir, "src", "module4_jsdm_biomod", "04_spatial_block_cv.R"))
source(file.path(base_dir, "src", "module4_jsdm_biomod", "05_biomod2_ensemble_sdm.R"))
source(file.path(base_dir, "src", "module4_jsdm_biomod", "06_cmip6_vulnerability_projections.R"))

data_dir <- file.path(base_dir, "data")
sp_csv <- file.path(base_dir, "config", "species_list.csv")
occ_csv <- file.path(data_dir, "processed", "cleaned_occurrences.csv")
climate_dir <- file.path(data_dir, "climate")
out_fig_dir <- file.path(base_dir, "outputs", "figures", "module4")
out_tab_dir <- file.path(base_dir, "outputs", "tables")
out_rast_dir <- file.path(base_dir, "outputs", "rasters", "cmip6_projections")

# 1. Génération de l'Arbre Phylogénétique (ape / V.PhyloMaker2)
cat("\n--- [1/6] Arbre Phylog\u00e9n\u00e9tique & Matrice de Covariance C ---\n")
generate_phylogenetic_tree(sp_csv, out_fig_dir, out_tab_dir)

# 2. Calibration du modèle bayésien Hmsc (JSDM)
cat("\n--- [2/6] Calibration Bay\u00e9sienne Hmsc (MCMC Multi-cha\u00eenes) ---\n")
calibrate_hmsc_jsdm(data_dir, out_fig_dir, out_tab_dir, n_chains = 4, samples = 2500)

# 3. Diagnostics MCMC (PSRF < 1.05, ESS > 1000) & Partition de Variance
cat("\n--- [3/6] Diagnostics MCMC (Gelman-Rubin PSRF, ESS) & Partition de Variance ---\n")
model_rds <- file.path(out_tab_dir, "hmsc_jsdm_fitted_model.rds")
run_hmsc_diagnostics_and_variance(model_rds, out_fig_dir, out_tab_dir)

# 4. Stratification spatiale en blocs (blockCV)
cat("\n--- [4/6] Validation Crois\u00e9e Spatiale en Blocs (blockCV) ---\n")
generate_spatial_blocks(occ_csv, out_fig_dir, out_tab_dir, k_folds = 5)

# 5. Modélisation d'Ensemble biomod2 (GLM, GAM, MaxEnt, RF, GBM)
cat("\n--- [5/6] Mod\u00e9lisation d'Ensemble biomod2 (Filtres AUC > 0.85, TSS > 0.70) ---\n")
block_occ_csv <- file.path(out_tab_dir, "module4_spatial_block_assignments.csv")
run_biomod2_ensemble_sdm(block_occ_csv, sp_csv, out_fig_dir, out_tab_dir, min_auc = 0.85, min_tss = 0.70)

# 6. Projections CMIP6 & Cartes de Vulnérabilité 2050 / 2080
cat("\n--- [6/6] Projections CMIP6 (5 GCMs, SSP2-4.5, SSP5-8.5, Horizons 2050/2080) ---\n")
project_cmip6_vulnerability(sp_csv, climate_dir, out_rast_dir, out_fig_dir, out_tab_dir)

cat("\n=================================================================\n")
cat("MODULE 4 TERMIN\u00c9 AVEC SUCC\u00c8S : TOUTES LES PROJECTIONS ET MOD\u00c8LES SONT PR\u00caTS !\n")
cat("=================================================================\n")
