# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : PARALLEL & HPC CONFIGURATION (Couche 4a)
# ==============================================================================

setup_parallel_backend <- function(n_cores = NULL) {
  if (is.null(n_cores)) {
    avail_cores <- parallel::detectCores()
    n_cores <- max(1, avail_cores - 1)
  }
  
  cat(sprintf("[HPC] Initialisation du calcul parall\u00e8le sur %d c\u0153urs...\n", n_cores))
  
  # Configuration future
  if (requireNamespace("future", quietly = TRUE)) {
    if (.Platform$OS.type == "windows") {
      future::plan(future::multisession, workers = n_cores)
    } else {
      future::plan(future::multicore, workers = n_cores)
    }
    cat(sprintf("[HPC] Backend 'future' configur\u00e9 en mode %s avec %d workers.\n", 
                if (.Platform$OS.type == "windows") "multisession" else "multicore", n_cores))
  }
  
  return(n_cores)
}
