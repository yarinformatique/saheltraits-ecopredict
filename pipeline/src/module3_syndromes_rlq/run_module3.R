# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : EXÉCUTION INTÉGRALE DU MODULE 3 (Couche 4a)
# Module 3 : Syndromes Fonctionnels & Couplage RLQ
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

cat("=================================================================\n")
cat("D\u00c9MARRAGE DU MODULE 3 : ACP POND\u00c9R\u00c9E, mFD, RLQ & QUATRI\u00c8ME COIN\n")
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

# Chargement des scripts du Module 3
source(file.path(base_dir, "src", "module3_syndromes_rlq", "01_weighted_pca.R"))
source(file.path(base_dir, "src", "module3_syndromes_rlq", "02_functional_diversity_mfd.R"))
source(file.path(base_dir, "src", "module3_syndromes_rlq", "03_rlq_ordination.R"))
source(file.path(base_dir, "src", "module3_syndromes_rlq", "04_fourth_corner_test.R"))

data_dir <- file.path(base_dir, "data")
traits_csv <- file.path(data_dir, "raw", "traits", "harmonized_traits.csv")
sp_csv <- file.path(base_dir, "config", "species_list.csv")
out_fig_dir <- file.path(base_dir, "outputs", "figures", "module3")
out_tab_dir <- file.path(base_dir, "outputs", "tables")

# 1. ACP Pondérée des Traits Fonctionnels (FactoMineR)
cat("\n--- [1/4] ACP Pond\u00e9r\u00e9e des Traits Fonctionnels (FactoMineR) ---\n")
run_weighted_pca(traits_csv, sp_csv, out_fig_dir, out_tab_dir)

# 2. Diversité Fonctionnelle Multidimensionnelle (mFD)
cat("\n--- [2/4] Diversit\u00e9 Fonctionnelle Multidimensionnelle (mFD : FRic, FEve, FDiv, FDis, RaoQ) ---\n")
tr_q_csv <- file.path(data_dir, "raw", "traits", "trait_matrix_Q.csv")
com_csv <- file.path(data_dir, "processed", "community_matrix.csv")
compute_mfd_indices(tr_q_csv, com_csv, out_fig_dir, out_tab_dir)

# 3. Couplage Multivarié RLQ (ade4)
cat("\n--- [3/4] Couplage Multivari\u00e9 RLQ (Tables R, L, Q) ---\n")
run_rlq_analysis(data_dir, out_fig_dir, out_tab_dir)

# 4. Test du Quatrième Coin (ade4 - Double Permutation 49 999 itérations)
cat("\n--- [4/4] Test du Quatri\u00e8me Coin (ade4::fourthcorner - 49 999 permutations) ---\n")
run_fourth_corner_test(data_dir, out_fig_dir, out_tab_dir, n_perm = 49999)

cat("\n=================================================================\n")
cat("MODULE 3 TERMIN\u00c9 AVEC SUCC\u00c8S : ACP, mFD, RLQ & QUATRI\u00c8ME COIN VALID\u00c9S !\n")
cat("=================================================================\n")
