# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 3 - TESTS DU QUATRIÈME COIN (ade4)
# Couche 4a : Double Permutation (49 999 permutations) - Modèle 6
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(ade4)
  library(ggplot2)
  library(dplyr)
  library(tidyr)
})

run_fourth_corner_test <- function(data_dir, output_dir, table_dir, n_perm = 49999) {
  cat(sprintf("[Module 3.4] Ex\u00e9cution du test du Quatri\u00e8me Coin (ade4::fourthcorner) avec %d permutations (Mod\u00e8le 6)...\n", n_perm))
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  R_file <- file.path(data_dir, "processed", "environmental_matrix_R.csv")
  L_file <- file.path(data_dir, "processed", "community_matrix.csv")
  Q_file <- file.path(data_dir, "raw", "traits", "trait_matrix_Q.csv")
  
  R <- read.csv(R_file, row.names = 1, check.names = FALSE)
  L <- read.csv(L_file, row.names = 1, check.names = FALSE)
  Q <- read.csv(Q_file, row.names = 1, check.names = FALSE)
  
  R_num <- as.data.frame(lapply(R, as.numeric))
  rownames(R_num) <- rownames(R)
  Q_num <- as.data.frame(lapply(Q, as.numeric))
  rownames(Q_num) <- rownames(Q)
  
  # Exécution du test du Quatrième Coin (Modèle 6 : double permutation avec n_perm itérations)
  set.seed(20261114)
  fc_test <- fourthcorner(
    tabR = R_num,
    tabL = L,
    tabQ = Q_num,
    modeltype = 6,
    nrepet = n_perm,
    p.adjust.method.G = "fdr",
    p.adjust.method.D = "fdr"
  )
  
  # Extraction des résultats depuis l'objet krandtest tabD
  tabD <- fc_test$tabD
  obs_vals <- tabD$obs
  p_vals <- tabD$adj.pvalue
  comb_names <- tabD$names
  
  # Construction du data.frame des résultats
  results_list <- list()
  for (i in seq_along(obs_vals)) {
    c_name <- comb_names[i]
    parts <- unlist(strsplit(c_name, "[/x:]"))
    env_v <- trimws(parts[1])
    trait_v <- trimws(parts[2])
    
    r_val <- obs_vals[i]
    p_adj <- p_vals[i]
    sig <- ifelse(p_adj < 0.001, "***",
           ifelse(p_adj < 0.01, "**",
           ifelse(p_adj < 0.05, "*", "ns")))
    
    results_list[[i]] <- data.frame(
      Environmental_Factor = env_v,
      Functional_Trait = trait_v,
      Correlation_r = round(r_val, 4),
      p_adjusted_FDR = round(p_adj, 5),
      Significance = sig,
      Association = ifelse(p_adj < 0.05 & r_val > 0, "Positive (+)",
                    ifelse(p_adj < 0.05 & r_val < 0, "Negative (-)", "Non-significant")),
      stringsAsFactors = FALSE
    )
  }
  
  res_table <- do.call(rbind, results_list)
  out_csv <- file.path(table_dir, "module3_fourth_corner_results_49999perm.csv")
  write.csv(res_table, out_csv, row.names = FALSE)
  cat(sprintf("[Module 3.4] R\u00e9sultats du Quatri\u00e8me Coin export\u00e9s vers : %s\n", out_csv))
  
  # Figure heatmap ggplot2 (300 dpi)
  p_heat <- ggplot(res_table, aes(x = Functional_Trait, y = Environmental_Factor, fill = Correlation_r)) +
    geom_tile(color = "white", linewidth = 0.5) +
    geom_text(aes(label = sprintf("%.2f\n%s", Correlation_r, Significance)), size = 3.5, fontface = "bold") +
    scale_fill_gradient2(low = "#D73027", mid = "#FFFFBF", high = "#4575B4", midpoint = 0,
                         name = "Corr\u00e9lation (r)", limits = c(-1, 1)) +
    labs(
      title = "Test du Quatri\u00e8me Coin : Couplage Traits Fonctionnels - Environnement",
      subtitle = sprintf("ade4::fourthcorner - Mod\u00e8le 6 (Double Permutation, %s permutations, correction FDR)",
                         format(n_perm, big.mark = " ")),
      x = "Traits Fonctionnels (Table Q)",
      y = "Param\u00e8tres Environnementaux & P\u00e9dologiques (Table R)"
    ) +
    theme_minimal(base_size = 11) +
    theme(
      axis.text.x = element_text(angle = 30, hjust = 1, face = "bold"),
      axis.text.y = element_text(face = "bold"),
      plot.title = element_text(face = "bold", size = 12),
      panel.grid = element_blank()
    )
  
  fig_path <- file.path(output_dir, "fig_module3_fourth_corner_heatmap.png")
  ggsave(fig_path, plot = p_heat, width = 9, height = 7, dpi = 300)
  cat(sprintf("[Module 3.4] Heatmap Quatri\u00e8me Coin g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", fig_path))
  
  return(fc_test)
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  data_d <- file.path(base_d, "data")
  out_d <- file.path(base_d, "outputs", "figures", "module3")
  tab_d <- file.path(base_d, "outputs", "tables")
  run_fourth_corner_test(data_d, out_d, tab_d, n_perm = 49999)
}
