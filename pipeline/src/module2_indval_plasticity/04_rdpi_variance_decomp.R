# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 2 - INDICE RDPI & DÉCOMPOSITION DE VARIANCE
# Couche 4a : Pipeline Bio-statistique
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
})

compute_rdpi_variance <- function(traits_csv, output_dir, table_dir) {
  cat("[Module 2.4] Calcul de l'indice de plasticit\u00e9 ph\u00e9notypique RDPI et d\u00e9composition de variance...\n")
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  df <- read.csv(traits_csv, stringsAsFactors = FALSE)
  traits <- c("SLA", "LDMC", "Wood_density", "Leaf_thickness")
  species_vec <- unique(df$species)
  
  rdpi_records <- list()
  for (sp in species_vec) {
    sp_data <- df[df$species == sp, ]
    zones <- unique(sp_data$climatic_zone)
    
    for (tr in traits) {
      pairwise_rel_diffs <- numeric()
      for (z1_idx in 1:(length(zones) - 1)) {
        for (z2_idx in (z1_idx + 1):length(zones)) {
          vals_z1 <- sp_data[[tr]][sp_data$climatic_zone == zones[z1_idx]]
          vals_z2 <- sp_data[[tr]][sp_data$climatic_zone == zones[z2_idx]]
          for (v1 in vals_z1) {
            for (v2 in vals_z2) {
              if ((v1 + v2) > 0) {
                rel_d <- abs(v1 - v2) / (v1 + v2)
                pairwise_rel_diffs <- c(pairwise_rel_diffs, rel_d)
              }
            }
          }
        }
      }
      
      mean_rdpi <- if (length(pairwise_rel_diffs) > 0) mean(pairwise_rel_diffs) else 0
      se_rdpi <- if (length(pairwise_rel_diffs) > 1) sd(pairwise_rel_diffs)/sqrt(length(pairwise_rel_diffs)) else 0
      
      rdpi_records[[paste(sp, tr, sep = "_")]] <- data.frame(
        species = sp,
        trait = tr,
        RDPI_mean = round(mean_rdpi, 4),
        RDPI_se = round(se_rdpi, 4),
        n_comparisons = length(pairwise_rel_diffs)
      )
    }
  }
  
  rdpi_df <- do.call(rbind, rdpi_records)
  out_rdpi_csv <- file.path(table_dir, "module2_rdpi_plasticity_index.csv")
  write.csv(rdpi_df, out_rdpi_csv, row.names = FALSE)
  cat(sprintf("[Module 2.4] Indices RDPI export\u00e9s : %s\n", out_rdpi_csv))
  
  # D\u00e9composition de variance
  var_decomp <- list()
  for (tr in traits) {
    fit_aov <- aov(as.formula(sprintf("%s ~ species + climatic_zone", tr)), data = df)
    ss <- summary(fit_aov)[[1]]$`Sum Sq`
    total_ss <- sum(ss)
    pct_species <- round((ss[1] / total_ss) * 100, 2)
    pct_zone <- round((ss[2] / total_ss) * 100, 2)
    pct_res <- round((ss[3] / total_ss) * 100, 2)
    
    var_decomp[[tr]] <- data.frame(
      Trait = tr,
      Pct_Interspecific = pct_species,
      Pct_Climatic_Plasticity = pct_zone,
      Pct_Residual_Individual = pct_res
    )
  }
  var_df <- do.call(rbind, var_decomp)
  out_var_csv <- file.path(table_dir, "module2_variance_decomposition.csv")
  write.csv(var_df, out_var_csv, row.names = FALSE)
  cat(sprintf("[Module 2.4] D\u00e9composition de variance export\u00e9e : %s\n", out_var_csv))
  
  # Figure ggplot2 RDPI
  p_rdpi <- ggplot(rdpi_df, aes(x = reorder(species, RDPI_mean), y = RDPI_mean, fill = trait)) +
    geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7, color = "black", linewidth = 0.2) +
    geom_errorbar(aes(ymin = pmax(0, RDPI_mean - RDPI_se), ymax = RDPI_mean + RDPI_se),
                  position = position_dodge(0.8), width = 0.25) +
    coord_flip() +
    scale_fill_brewer(palette = "Set2", name = "Trait fonctionnel") +
    labs(
      title = "Indice Relatif de Plasticit\u00e9 Ph\u00e9notypique (RDPI) des Essences Sah\u00e9liennes",
      subtitle = "Comparaison bilat\u00e9rale des r\u00e9ponses foliaires et ligneuses aux gradients climatiques",
      x = "Esp\u00e8ce",
      y = "Indice RDPI (0 = Fixe, 1 = Plasticit\u00e9 maximale)"
    ) +
    theme_bw(base_size = 11) +
    theme(
      legend.position = "bottom",
      axis.text.y = element_text(face = "italic"),
      plot.title = element_text(face = "bold", size = 12)
    )
  
  fig_rdpi_path <- file.path(output_dir, "fig_module2_rdpi_plasticity.png")
  ggsave(fig_rdpi_path, plot = p_rdpi, width = 10, height = 7, dpi = 300)
  cat(sprintf("[Module 2.4] Figure RDPI g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", fig_rdpi_path))
  
  return(list(rdpi = rdpi_df, variance = var_df))
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  traits_csv <- file.path(base_d, "data", "raw", "traits", "harmonized_traits.csv")
  out_d <- file.path(base_d, "outputs", "figures", "module2")
  tab_d <- file.path(base_d, "outputs", "tables")
  compute_rdpi_variance(traits_csv, out_d, tab_d)
}
