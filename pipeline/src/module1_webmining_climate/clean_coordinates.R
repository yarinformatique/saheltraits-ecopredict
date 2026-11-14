# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : SPATIAL DATA CLEANING (CoordinateCleaner)
# Module 1 : Web-Mining & Climat (Couche 4a)
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
})

clean_coordinates_pipeline <- function(input_csv, output_csv, summary_csv) {
  cat("[CoordinateCleaner] D\u00e9but du nettoyage spatial des occurrences...\n")
  
  if (!file.exists(input_csv)) {
    stop(paste("Fichier d'entr\u00e9e introuvable :", input_csv))
  }
  
  df <- read.csv(input_csv, stringsAsFactors = FALSE)
  n_initial <- nrow(df)
  cat(sprintf("[CoordinateCleaner] Total enregistrements bruts re\u00e7us : %d\n", n_initial))
  
  # 1. Validation de base : Lat/Lon non nulles et num\u00e9riques
  df <- df %>% filter(!is.na(decimalLatitude) & !is.na(decimalLongitude))
  df$decimalLatitude <- as.numeric(df$decimalLatitude)
  df$decimalLongitude <- as.numeric(df$decimalLongitude)
  
  # 2. Test Z\u00e9ro Coordinates (cc_zer)
  # Coordonn\u00e9es (0, 0) ou lat == 0 ou lon == 0
  flag_zero <- (abs(df$decimalLatitude) < 0.001 & abs(df$decimalLongitude) < 0.001) |
               (abs(df$decimalLatitude) < 0.001) | (abs(df$decimalLongitude) < 0.001)
  
  # 3. Test Capitales d'\u00c9tats (cc_cap)
  # Ouagadougou: 12.3714, -1.5197 (rayon ~15 km)
  # Bamako: 12.6392, -8.0029
  # Niamey: 13.5116, 2.1254
  capitals <- data.frame(
    name = c("Ouagadougou", "Bamako", "Niamey"),
    lat = c(12.3714, 12.6392, 13.5116),
    lon = c(-1.5197, -8.0029, 2.1254)
  )
  flag_capital <- rep(FALSE, nrow(df))
  for (i in 1:nrow(capitals)) {
    dist <- sqrt((df$decimalLatitude - capitals$lat[i])^2 + (df$decimalLongitude - capitals$lon[i])^2)
    # ~0.15 deg ~ 16 km
    flag_capital <- flag_capital | (dist < 0.12)
  }
  
  # 4. Test Milieu Marin / Hors Domaine Terrestre Sah\u00e9lien (cc_sea / bounding box)
  # Domaine d'\u00e9tude Sahel / Afrique de l'Ouest : Lat [8.0, 16.5], Lon [-6.0, 3.5]
  flag_sea_or_outside <- (df$decimalLatitude < 8.0) | (df$decimalLatitude > 16.5) |
                         (df$decimalLongitude < -6.0) | (df$decimalLongitude > 3.5)
  
  # 5. Test Doublons Spatiaux stricts par esp\u00e8ce (cc_dupl)
  df$coord_key <- paste(df$species, round(df$decimalLatitude, 4), round(df$decimalLongitude, 4), sep = "_")
  flag_dupl <- duplicated(df$coord_key)
  
  # 6. Test Valeurs Aberrantes Spatiales (cc_outl - 3-sigma / IQR par esp\u00e8ce)
  df$flag_outlier <- FALSE
  species_vec <- unique(df$species)
  for (sp in species_vec) {
    idx <- which(df$species == sp & !flag_zero & !flag_sea_or_outside)
    if (length(idx) > 10) {
      sub_lat <- df$decimalLatitude[idx]
      sub_lon <- df$decimalLongitude[idx]
      med_lat <- median(sub_lat)
      med_lon <- median(sub_lon)
      dist_from_med <- sqrt((sub_lat - med_lat)^2 + (sub_lon - med_lon)^2)
      iqr_dist <- IQR(dist_from_med)
      q3_dist <- quantile(dist_from_med, 0.75)
      cutoff <- q3_dist + 2.5 * iqr_dist
      outliers <- idx[dist_from_med > cutoff]
      df$flag_outlier[outliers] <- TRUE
    }
  }
  
  # Attribution des drapeaux
  df$flag_zero <- flag_zero
  df$flag_capital <- flag_capital
  df$flag_sea <- flag_sea_or_outside
  df$flag_dupl <- flag_dupl
  
  # Crit\u00e8re global de validit\u00e9 (conforme CoordinateCleaner: .summary == TRUE)
  df$is_valid <- !(df$flag_zero | df$flag_capital | df$flag_sea | df$flag_dupl | df$flag_outlier)
  
  # Synth\u00e8se des tests
  summary_df <- data.frame(
    Test = c("Total initial", "Coordonn\u00e9es nulles (cc_zer)", "Centro\u00efdes capitales (cc_cap)", 
             "Hors zone terrestre/mer (cc_sea)", "Doublons spatiaux (cc_dupl)", 
             "Aberrations g\u00e9ographiques (cc_outl)", "Occurrences valid\u00e9es conserv\u00e9es"),
    Count = c(n_initial, sum(flag_zero), sum(flag_capital), sum(flag_sea_or_outside), 
              sum(flag_dupl), sum(df$flag_outlier), sum(df$is_valid)),
    Pct = round(c(100, sum(flag_zero)/n_initial*100, sum(flag_capital)/n_initial*100, 
                  sum(flag_sea_or_outside)/n_initial*100, sum(flag_dupl)/n_initial*100, 
                  sum(df$flag_outlier)/n_initial*100, sum(df$is_valid)/n_initial*100), 2)
  )
  
  cat("[CoordinateCleaner] R\u00e9capitulatif du filtrage spatial :\n")
  print(summary_df)
  
  # Sauvegarde des r\u00e9sultats
  clean_df <- df %>% filter(is_valid) %>% select(species, decimalLatitude, decimalLongitude, year, basisOfRecord, coordinateUncertaintyInMeters, datasetKey, source)
  
  dir.create(dirname(output_csv), recursive = TRUE, showWarnings = FALSE)
  write.csv(clean_df, output_csv, row.names = FALSE)
  write.csv(summary_df, summary_csv, row.names = FALSE)
  
  cat(sprintf("[CoordinateCleaner] %d occurrences valides enregistr\u00e9es sous '%s'.\n", nrow(clean_df), output_csv))
  return(clean_df)
}

# Ex\u00e9cution autonome si invoqu\u00e9 en script
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 2) {
  clean_coordinates_pipeline(args[1], args[2], if (length(args) >= 3) args[3] else "cleaning_summary.csv")
} else {
  base_dir <- normalizePath(file.path(dirname(normalizePath(sys.frame(1)$ofile)), "..", ".."))
  in_f <- file.path(base_dir, "data", "raw", "occurrences", "gbif_raw_occurrences.csv")
  out_f <- file.path(base_dir, "data", "processed", "cleaned_occurrences.csv")
  sum_f <- file.path(base_dir, "outputs", "tables", "module1_cleaning_summary.csv")
  if (file.exists(in_f)) {
    clean_coordinates_pipeline(in_f, out_f, sum_f)
  }
}
