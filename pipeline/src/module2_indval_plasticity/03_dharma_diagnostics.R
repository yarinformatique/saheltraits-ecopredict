# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MODULE 2 - DIAGNOSTIC DES RÉSIDUS (DHARMa)
# Couche 4a : Pipeline Bio-statistique
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(DHARMa)
  library(lme4)
  library(ggplot2)
})

run_dharma_diagnostics <- function(models_rds_path, output_dir, table_dir) {
  cat("[Module 2.3] Ex\u00e9cution du diagnostic des r\u00e9sidus DHARMa sur les mod\u00e8les lme4...\n")
  
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  dir.create(table_dir, recursive = TRUE, showWarnings = FALSE)
  
  if (!file.exists(models_rds_path)) {
    stop("Mod\u00e8les sauvegard\u00e9s introuvables : ", models_rds_path)
  }
  
  models_list <- readRDS(models_rds_path)
  diag_summary <- list()
  
  # Diagnostic pour SLA
  m_sla <- models_list[["SLA"]]
  set.seed(20261114)
  res_sim <- simulateResiduals(fittedModel = m_sla, n = 1000, plot = FALSE)
  
  test_ks <- testUniformity(res_sim, plot = FALSE)
  test_disp <- testDispersion(res_sim, plot = FALSE)
  test_outl <- testOutliers(res_sim, plot = FALSE)
  
  diag_summary[["SLA"]] <- data.frame(
    Model = "SLA ~ Zone + (1|species)",
    KS_Statistic = round(test_ks$statistic, 4),
    KS_p_value = round(test_ks$p.value, 4),
    Dispersion_Ratio = round(test_disp$statistic, 4),
    Dispersion_p_value = round(test_disp$p.value, 4),
    Outliers_Count = test_outl$statistic,
    Outliers_p_value = round(test_outl$p.value, 4),
    Status = ifelse(test_ks$p.value > 0.05 & test_disp$p.value > 0.05, "VALIDATED (Homoscedastic & Uniform)", "FLAGGED")
  )
  
  # Diagnostic pour Wood_density
  if ("Wood_density" %in% names(models_list)) {
    m_wd <- models_list[["Wood_density"]]
    res_wd <- simulateResiduals(fittedModel = m_wd, n = 1000, plot = FALSE)
    ks_wd <- testUniformity(res_wd, plot = FALSE)
    disp_wd <- testDispersion(res_wd, plot = FALSE)
    outl_wd <- testOutliers(res_wd, plot = FALSE)
    diag_summary[["Wood_density"]] <- data.frame(
      Model = "Wood_density ~ Zone + (1|species)",
      KS_Statistic = round(ks_wd$statistic, 4),
      KS_p_value = round(ks_wd$p.value, 4),
      Dispersion_Ratio = round(disp_wd$statistic, 4),
      Dispersion_p_value = round(disp_wd$p.value, 4),
      Outliers_Count = outl_wd$statistic,
      Outliers_p_value = round(outl_wd$p.value, 4),
      Status = ifelse(ks_wd$p.value > 0.05 & disp_wd$p.value > 0.05, "VALIDATED (Homoscedastic & Uniform)", "FLAGGED")
    )
  }
  
  summary_df <- do.call(rbind, diag_summary)
  out_csv <- file.path(table_dir, "module2_dharma_diagnostics_summary.csv")
  write.csv(summary_df, out_csv, row.names = FALSE)
  cat(sprintf("[Module 2.3] Synth\u00e8se des diagnostics r\u00e9sidus export\u00e9e : %s\n", out_csv))
  
  png_path <- file.path(output_dir, "fig_module2_dharma_residuals_diagnostic.png")
  png(png_path, width = 10, height = 5, units = "in", res = 300)
  par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3, 2))
  plotQQunif(res_sim, main = "DHARMa Residuals Q-Q Plot (SLA Model)")
  plotResiduals(res_sim, main = "Residuals vs Predicted (SLA Model)")
  dev.off()
  
  cat(sprintf("[Module 2.3] Figure DHARMa g\u00e9n\u00e9r\u00e9e : %s (300 dpi)\n", png_path))
  return(summary_df)
}

if (sys.nframe() == 0L) {
  base_d <- normalizePath(file.path(getwd(), "..", ".."))
  models_p <- file.path(base_d, "outputs", "tables", "module2_fitted_lmer_models.rds")
  out_d <- file.path(base_d, "outputs", "figures", "module2")
  tab_d <- file.path(base_d, "outputs", "tables")
  run_dharma_diagnostics(models_p, out_d, tab_d)
}
