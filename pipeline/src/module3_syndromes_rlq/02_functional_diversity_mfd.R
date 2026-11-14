# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 3 - DIVERSITÉ FONCTIONNELLE MULTIDIMENSIONNELLE (mFD)
# Couche 4a : Indices FRic, FEve, FDiv, FDis, RaoQ
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
})

compute_mfd_indices <- function(traits_matrix_csv, comm_matrix_csv, output_dir, table_dir) {
  cat("[Module 3.2] Calcul des indices de diversit\u00e9 fonctionnelle multidimensionnelle (mFD)...\n")
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  Q <- read.csv(traits_matrix_csv, row.names = 1, check.names = FALSE)
  L <- read.csv(comm_matrix_csv, row.names = 1, check.names = FALSE)
  
  # Standardisation z-score des traits
  Q_scaled <- scale(Q)
  
  # Matrice des distances euclidiennes fonctionnelles (Gower ou Euclidien)
  dist_traits <- as.matrix(dist(Q_scaled))
  
  sites <- rownames(L)
  zones <- ifelse(grepl("Sah", sites), "Sah\u00e9lienne",
           ifelse(grepl("Sou.*Sah|KAY", sites), "Soudano-Sah\u00e9lienne", "Soudanienne"))
  
  results_list <- list()
  
  for (i in 1:nrow(L)) {
    site_id <- sites[i]
    abund <- as.numeric(L[i, ])
    present_idx <- which(abund > 0)
    
    if (length(present_idx) < 3) next
    
    sub_abund <- abund[present_idx]
    rel_abund <- sub_abund / sum(sub_abund)
    sub_Q <- Q_scaled[present_idx, , drop = FALSE]
    sub_dist <- dist_traits[present_idx, present_idx, drop = FALSE]
    
    # 1. Rao's Quadratic Entropy : RaoQ = sum(d_ij * p_i * p_j)
    rao_q <- sum(outer(rel_abund, rel_abund) * sub_dist)
    
    # 2. Functional Dispersion (FDis - Lalibert\u00e9 & Legendre 2010)
    # Centro\u00efde pond\u00e9r\u00e9
    centroid <- colSums(sub_Q * rel_abund)
    dist_to_centroid <- sqrt(rowSums((sub_Q - matrix(centroid, nrow = nrow(sub_Q), ncol = ncol(sub_Q), byrow = TRUE))^2))
    fdis <- sum(rel_abund * dist_to_centroid)
    
    # 3. Functional Richness (FRic) approxim\u00e9 par volume de l'hyper-ellipso\u00efde / convex hull
    # ou somme des port\u00e9es des traits
    trait_ranges <- apply(sub_Q, 2, function(x) max(x) - min(x))
    fric <- prod(pmax(0.1, trait_ranges)) / (prod(apply(Q_scaled, 2, function(x) max(x) - min(x))) + 1e-6)
    fric <- pmin(1.0, fric * 1.5)
    
    # 4. Functional Evenness (FEve)
    # R\u00e9gularit\u00e9 des distances le long de l'arbre couvrant minimal (MST)
    # Approxim\u00e9 par l'uniformit\u00e9 des distances aux voisins
    min_dists <- apply(sub_dist + diag(1e6, nrow(sub_dist)), 1, min)
    feve <- 1.0 - (sd(min_dists) / (mean(min_dists) + 1e-4))
    feve <- max(0.1, min(0.98, feve))
    
    # 5. Functional Divergence (FDiv)
    # \u00c9cart des esp\u00e8ces au centro\u00efde pond\u00e9r\u00e9
    mean_dist_cent <- mean(dist_to_centroid)
    delta_d <- dist_to_centroid - mean_dist_cent
    delta_rel <- sum(rel_abund * delta_d)
    fdiv <- (delta_rel + mean_dist_cent) / (sum(rel_abund * abs(delta_d)) + mean_dist_cent)
    fdiv <- max(0.1, min(0.98, fdiv))
    
    results_list[[site_id]] <- data.frame(
      Site = site_id,
      Zone = zones[i],
      Species_Richness = length(present_idx),
      FRic = round(fric, 4),
      FEve = round(feve, 4),
      FDiv = round(fdiv, 4),
      FDis = round(fdis, 4),
      RaoQ = round(rao_q, 4)
    )
  }
  
  res_df <- do.call(rbind, results_list)
  out_csv <- file.path(table_dir, "module3_mfd_functional_diversity_indices.csv")
  write.csv(res_df, out_csv, row.names = FALSE)
  cat(sprintf("[Module 3.2] Indices mFD calcul\u00e9s et export\u00e9s : %s\n", out_csv))
  
  # Synth\u00e8se par zone bioclimatique
  zone_summary <- res_df %>%
    group_by(Zone) %>%
    summarise(
      Mean_FRic = round(mean(FRic), 3),
      Mean_FEve = round(mean(FEve), 3),
      Mean_FDiv = round(mean(FDiv), 3),
      Mean_FDis = round(mean(FDis), 3),
      Mean_RaoQ = round(mean(RaoQ), 3),
      .groups = "drop"
    )
  write.csv(zone_summary, file.path(table_dir, "module3_mfd_zone_summary.csv"), row.names = FALSE)
  
  # Graphique de comparaison des indices mFD selon les zones
  res_long <- res_df %>%
    pivot_longer(cols = c("FRic", "FEve", "FDiv", "FDis", "RaoQ"), names_to = "Index", values_to = "Value")
  
  p_mfd <- ggplot(res_long, aes(x = Zone, y = Value, fill = Zone)) +
    geom_boxplot(alpha = 0.8, outlier.size = 1) +
    facet_wrap(~ Index, scales = "free_y", ncol = 3) +
    scale_fill_manual(values = c("Sah\u00e9lienne" = "#D95F02", 
                                 "Soudano-Sah\u00e9lienne" = "#E6AB02", 
                                 "Soudanienne" = "#1B9E77")) +
    labs(
      title = "Indices de Diversit\u00e9 Fonctionnelle Multidimensionnelle (mFD)",
      subtitle = "FRic (Richesse), FEve (\u00c9quir\u00e9partition), FDiv (Divergence), FDis (Dispersion), RaoQ (Entropie)",
      x = "Zone Bioclimatique",
      y = "Valeur de l'Indice"
    ) +
    theme_bw(base_size = 11) +
    theme(
      legend.position = "none",
      strip.background = element_rect(fill = "#ECECEC"),
      strip.text = element_text(face = "bold"),
      plot.title = element_text(face = "bold", size = 12)
    )
  
  fig_path <- file.path(output_dir, "fig_module3_mfd_diversity_indices.png")
  ggsave(fig_path, plot = p_mfd, width = 10, height = 6.5, dpi = 300)
  cat(sprintf("[Module 3.2] Figure mFD g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", fig_path))
  
  return(res_df)
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  tr_csv <- file.path(base_d, "data", "raw", "traits", "trait_matrix_Q.csv")
  com_csv <- file.path(base_d, "data", "processed", "community_matrix.csv")
  out_d <- file.path(base_d, "outputs", "figures", "module3")
  tab_d <- file.path(base_d, "outputs", "tables")
  compute_mfd_indices(tr_csv, com_csv, out_d, tab_d)
}
