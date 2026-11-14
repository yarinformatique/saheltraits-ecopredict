# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : EXÉCUTION INTÉGRALE DU MODULE 2 (Couche 4a)
# Module 2 : Sélection IndVal & Plasticité Phénotypique
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

cat("=================================================================\n")
cat("D\u00c9MARRAGE DU MODULE 2 : INDVAL, PLASTICIT\u00c9 & GERMINATION (Couche 4a)\n")
cat("=================================================================\n")

# Détermination propre du répertoire de base
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

# Chargement des scripts du Module 2
source(file.path(base_dir, "src", "module2_indval_plasticity", "01_indval_smith.R"))
source(file.path(base_dir, "src", "module2_indval_plasticity", "02_lme4_glmm_plasticity.R"))
source(file.path(base_dir, "src", "module2_indval_plasticity", "03_dharma_diagnostics.R"))
source(file.path(base_dir, "src", "module2_indval_plasticity", "04_rdpi_variance_decomp.R"))
source(file.path(base_dir, "src", "module2_indval_plasticity", "05_germination_curves.R"))

sp_csv <- file.path(base_dir, "config", "species_list.csv")
occ_csv <- file.path(base_dir, "data", "processed", "cleaned_occurrences.csv")
traits_csv <- file.path(base_dir, "data", "raw", "traits", "harmonized_traits.csv")
out_fig_dir <- file.path(base_dir, "outputs", "figures", "module2")
out_tab_dir <- file.path(base_dir, "outputs", "tables")
models_rds <- file.path(out_tab_dir, "module2_fitted_lmer_models.rds")

# 1. IndVal & Smith Saliency
cat("\n--- [1/5] IndVal & Saillance de Smith ---\n")
compute_indval_smith(sp_csv, occ_csv, out_fig_dir, out_tab_dir)

# 2. Modèles Mixtes Hiérarchiques (lme4)
cat("\n--- [2/5] Mod\u00e8les Mixtes Hi\u00e9rarchiques (lme4) ---\n")
fit_hierarchical_models(traits_csv, out_fig_dir, out_tab_dir)

# 3. Diagnostic des Résidus (DHARMa)
cat("\n--- [3/5] Diagnostics DHARMa (Uniformit\u00e9 & Dispersion) ---\n")
run_dharma_diagnostics(models_rds, out_fig_dir, out_tab_dir)

# 4. Indice de Plasticité RDPI & Décomposition de Variance
cat("\n--- [4/5] Plasticit\u00e9 Ph\u00e9notypique RDPI & D\u00e9composition de Variance ---\n")
compute_rdpi_variance(traits_csv, out_fig_dir, out_tab_dir)

# 5. Courbes de Germination sous Stress
cat("\n--- [5/5] Courbes Temps-\u00c9v\u00e9nement & M\u00e9triques de Germination (drc) ---\n")
simulate_and_fit_germination(out_fig_dir, out_tab_dir)

cat("\n=================================================================\n")
cat("MODULE 2 TERMIN\u00c9 AVEC SUCC\u00c8S : TOUTES LES ANALYSES & FIGURES G\u00c9N\u00c9R\u00c9ES !\n")
cat("=================================================================\n")
