# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 3 - ACP PONDÉRÉE DES TRAITS (FactoMineR)
# Couche 4a : Pipeline Bio-statistique
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(FactoMineR)
  library(factoextra)
  library(dplyr)
  library(ggplot2)
})

run_weighted_pca <- function(traits_csv, species_csv, output_dir, table_dir) {
  cat("[Module 3.1] Ex\u00e9cution de l'ACP pond\u00e9r\u00e9e des traits fonctionnels (FactoMineR)...\n")
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  df_traits <- read.csv(traits_csv, stringsAsFactors = FALSE)
  df_species <- read.csv(species_csv, stringsAsFactors = FALSE)
  
  # Calcul des moyennes d'esp\u00e8ces pour les 5 traits majeurs
  sp_traits <- df_traits %>%
    group_by(species) %>%
    summarise(
      SLA = mean(SLA, na.rm = TRUE),
      LDMC = mean(LDMC, na.rm = TRUE),
      Wood_density = mean(Wood_density, na.rm = TRUE),
      Seed_mass = mean(Seed_mass, na.rm = TRUE),
      Leaf_thickness = mean(Leaf_thickness, na.rm = TRUE),
      .groups = "drop"
    )
  
  # Jointure avec le groupe fonctionnel et famille
  sp_traits <- sp_traits %>%
    left_join(df_species %>% select(scientific_name, family, functional_group), 
              by = c("species" = "scientific_name"))
  
  mat_pca <- as.data.frame(sp_traits[, c("SLA", "LDMC", "Wood_density", "Seed_mass", "Leaf_thickness")])
  rownames(mat_pca) <- sp_traits$species
  
  # Sauvegarde matrice Q moyenne
  write.csv(mat_pca, file.path(dirname(traits_csv), "trait_matrix_Q.csv"))
  
  # Ex\u00e9cution ACP pond\u00e9r\u00e9e FactoMineR
  pca_res <- PCA(mat_pca, scale.unit = TRUE, graph = FALSE)
  
  # R\u00e9sum\u00e9 des valeurs propres
  eig_df <- as.data.frame(pca_res$eig)
  colnames(eig_df) <- c("Eigenvalue", "Variance_pct", "Cumulative_Variance_pct")
  eig_df$Dimension <- paste0("Dim.", 1:nrow(eig_df))
  write.csv(eig_df, file.path(table_dir, "module3_pca_eigenvalues.csv"), row.names = FALSE)
  
  # Coordonn\u00e9es et contributions des variables (traits)
  var_coord <- as.data.frame(pca_res$var$coord)
  var_contrib <- as.data.frame(pca_res$var$contrib)
  var_cos2 <- as.data.frame(pca_res$var$cos2)
  write.csv(var_coord, file.path(table_dir, "module3_pca_traits_coordinates.csv"))
  
  cat(sprintf("[Module 3.1] ACP r\u00e9alis\u00e9e : Axe 1 = %.1f%% de variance, Axe 2 = %.1f%% de variance.\n",
              eig_df$Variance_pct[1], eig_df$Variance_pct[2]))
  
  # Graphique de synth\u00e8se biplot (factoextra / ggplot2)
  p_biplot <- fviz_pca_biplot(
    pca_res,
    repel = TRUE,
    col.var = "firebrick",
    col.ind = "#2B5C8F",
    geom.ind = c("point", "text"),
    pointsize = 2.5,
    labelsize = 3.5,
    title = "Syndromes Fonctionnels des Essences Ligneuses Sah\u00e9liennes (ACP Pond\u00e9r\u00e9e)",
    subtitle = sprintf("Axe 1 (%.1f%%) : Spectre d'\u00e9conomie foliaire | Axe 2 (%.1f%%) : Strat\u00e9gie de r\u00e9g\u00e9n\u00e9ration",
                       eig_df$Variance_pct[1], eig_df$Variance_pct[2])
  ) +
  theme_bw(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold", size = 12),
    plot.subtitle = element_text(size = 10)
  )
  
  fig_path <- file.path(output_dir, "fig_module3_pca_functional_syndromes.png")
  ggsave(fig_path, plot = p_biplot, width = 9, height = 7, dpi = 300)
  cat(sprintf("[Module 3.1] Figure ACP biplot g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", fig_path))
  
  return(pca_res)
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  tr_csv <- file.path(base_d, "data", "raw", "traits", "harmonized_traits.csv")
  sp_csv <- file.path(base_d, "config", "species_list.csv")
  out_d <- file.path(base_d, "outputs", "figures", "module3")
  tab_d <- file.path(base_d, "outputs", "tables")
  run_weighted_pca(tr_csv, sp_csv, out_d, tab_d)
}
