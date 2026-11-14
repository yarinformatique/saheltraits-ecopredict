# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 2 - MODÈLES MIXTES HIÉRARCHIQUES (lme4/glmmTMB)
# Couche 4a : Pipeline Bio-statistique
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(lme4)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
})

fit_hierarchical_models <- function(traits_csv, output_dir, table_dir) {
  cat("[Module 2.2] Ajustement des mod\u00e8les mixtes hi\u00e9rarchiques (lme4)...\n")
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  df <- read.csv(traits_csv, stringsAsFactors = FALSE)
  df$climatic_zone <- factor(df$climatic_zone, levels = c("Soudanienne", "Soudano-Sah\u00e9lienne", "Sah\u00e9lienne"))
  df$species <- factor(df$species)
  df$plot_id <- factor(df$plot_id)
  
  traits <- c("SLA", "LDMC", "Wood_density", "Leaf_thickness")
  models_list <- list()
  summary_rows <- list()
  
  for (tr in traits) {
    cat(sprintf("[Module 2.2] Traitement du trait fonctionnel : %s\n", tr))
    form <- as.formula(sprintf("%s ~ climatic_zone + (1 | species)", tr))
    m <- lmer(form, data = df, REML = TRUE)
    models_list[[tr]] <- m
    
    fix <- fixef(m)
    vc <- as.data.frame(VarCorr(m))
    var_species <- vc$vcov[vc$grp == "species"]
    var_residual <- vc$vcov[vc$grp == "Residual"]
    total_var <- var_species + var_residual
    
    pct_inter <- round((var_species / total_var) * 100, 2)
    pct_intra <- round((var_residual / total_var) * 100, 2)
    
    summary_rows[[tr]] <- data.frame(
      Trait = tr,
      Intercept_Soudanienne = round(fix["(Intercept)"], 3),
      Effect_Soudano_Sahelienne = round(fix["climatic_zoneSoudano-Sah\u00e9lienne"], 3),
      Effect_Sahelienne = round(fix["climatic_zoneSah\u00e9lienne"], 3),
      Var_Interspecific = round(var_species, 4),
      Var_Intraspecific = round(var_residual, 4),
      Pct_Interspecific_Variance = pct_inter,
      Pct_Intraspecific_Variance = pct_intra,
      AIC = round(AIC(m), 1),
      BIC = round(BIC(m), 1)
    )
  }
  
  res_table <- do.call(rbind, summary_rows)
  out_csv <- file.path(table_dir, "module2_lme4_trait_models.csv")
  write.csv(res_table, out_csv, row.names = FALSE)
  cat(sprintf("[Module 2.2] Table synth\u00e9tique des mod\u00e8les lme4 export\u00e9e : %s\n", out_csv))
  
  rdata_path <- file.path(table_dir, "module2_fitted_lmer_models.rds")
  saveRDS(models_list, rdata_path)
  
  df_long <- df %>%
    pivot_longer(cols = c("SLA", "LDMC", "Wood_density", "Leaf_thickness"), 
                 names_to = "Trait", values_to = "Value")
  
  p <- ggplot(df_long, aes(x = climatic_zone, y = Value, fill = climatic_zone)) +
    geom_boxplot(alpha = 0.8, outlier.size = 1) +
    geom_jitter(width = 0.2, alpha = 0.25, size = 0.8) +
    facet_wrap(~ Trait, scales = "free_y", ncol = 2) +
    scale_fill_manual(values = c("Soudanienne" = "#1B9E77", 
                                 "Soudano-Sah\u00e9lienne" = "#E6AB02", 
                                 "Sah\u00e9lienne" = "#D95F02")) +
    labs(
      title = "R\u00e9ponse Plastique des Traits Fonctionnels au Gradient d'Aridit\u00e9 Sah\u00e9lien",
      subtitle = "Mod\u00e8les Hi\u00e9rarchiques lme4 (360 individus, 12 esp\u00e8ces ligneuses)",
      x = "Zone Bioclimatique",
      y = "Valeur du Trait (Unit\u00e9 ETS v1.0)"
    ) +
    theme_bw(base_size = 11) +
    theme(
      legend.position = "none",
      strip.background = element_rect(fill = "#EFEFEF"),
      strip.text = element_text(face = "bold"),
      plot.title = element_text(face = "bold", size = 12)
    )
  
  fig_path <- file.path(output_dir, "fig_module2_traits_gradient_boxplot.png")
  ggsave(fig_path, plot = p, width = 9, height = 7, dpi = 300)
  cat(sprintf("[Module 2.2] Figure g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", fig_path))
  
  return(models_list)
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  traits_csv <- file.path(base_d, "data", "raw", "traits", "harmonized_traits.csv")
  out_d <- file.path(base_d, "outputs", "figures", "module2")
  tab_d <- file.path(base_d, "outputs", "tables")
  fit_hierarchical_models(traits_csv, out_d, tab_d)
}
