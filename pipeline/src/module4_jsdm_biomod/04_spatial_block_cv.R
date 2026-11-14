# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 4 - VALIDATION CROISÉE SPATIALE EN BLOCS (blockCV)
# Couche 4a : Partitionnement Spatial Éliminant l'Autocorrélation
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
})

generate_spatial_blocks <- function(clean_occ_csv, output_dir, table_dir, n_blocks_x = 3, n_blocks_y = 3, k_folds = 5) {
  cat(sprintf("[Module 4.4] Cr\u00e9ation des blocs spatiaux de validation crois\u00e9e (k = %d folds)...\n", k_folds))
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  df <- read.csv(clean_occ_csv, stringsAsFactors = FALSE)
  
  # Délimitation du domaine
  xmin <- min(df$decimalLongitude)
  xmax <- max(df$decimalLongitude)
  ymin <- min(df$decimalLatitude)
  ymax <- max(df$decimalLatitude)
  
  # Création d'une grille régulière de blocs spatiaux (blockCV)
  dx <- (xmax - xmin) / n_blocks_x
  dy <- (ymax - ymin) / n_blocks_y
  
  col_idx <- pmin(n_blocks_x, pmax(1, ceiling((df$decimalLongitude - xmin) / dx)))
  row_idx <- pmin(n_blocks_y, pmax(1, ceiling((df$decimalLatitude - ymin) / dy)))
  
  block_id <- (row_idx - 1) * n_blocks_x + col_idx
  
  # Attribution des folds (1 à k_folds) aux blocs de manière équilibrée
  set.seed(20261114)
  unique_blocks <- unique(block_id)
  block_to_fold <- setNames(sample(rep_len(1:k_folds, length(unique_blocks))), unique_blocks)
  
  df$spatial_block_id <- block_id
  df$fold_cv <- block_to_fold[as.character(block_id)]
  
  out_csv <- file.path(table_dir, "module4_spatial_block_assignments.csv")
  write.csv(df, out_csv, row.names = FALSE)
  cat(sprintf("[Module 4.4] Affectations des blocs spatiaux export\u00e9es : %s\n", out_csv))
  
  # Figure ggplot2 : Cartographie des blocs de validation spatiale (300 dpi)
  p_block <- ggplot(df, aes(x = decimalLongitude, y = decimalLatitude, color = as.factor(fold_cv))) +
    geom_point(alpha = 0.7, size = 1.5) +
    scale_color_brewer(palette = "Set1", name = "Fold spatial CV") +
    labs(
      title = "Stratification Spatiale en Blocs pour la Validation Crois\u00e9e (blockCV)",
      subtitle = sprintf("Partitionnement en %d plis spatiaux ind\u00e9pendants r\u00e9duisant l'autocorr\u00e9lation", k_folds),
      x = "Longitude (WGS 84)",
      y = "Latitude (WGS 84)"
    ) +
    theme_bw(base_size = 11) +
    theme(
      legend.position = "right",
      plot.title = element_text(face = "bold", size = 12)
    )
  
  fig_path <- file.path(output_dir, "fig_module4_spatial_block_cv_folds.png")
  ggsave(fig_path, plot = p_block, width = 8.5, height = 6.5, dpi = 300)
  cat(sprintf("[Module 4.4] Carte des blocs spatiaux g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", fig_path))
  
  return(df)
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  occ_csv <- file.path(base_d, "data", "processed", "cleaned_occurrences.csv")
  out_d <- file.path(base_d, "outputs", "figures", "module4")
  tab_d <- file.path(base_d, "outputs", "tables")
  generate_spatial_blocks(occ_csv, out_d, tab_d)
}
