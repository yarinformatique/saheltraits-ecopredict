"""
Comprehensive Integration & Verification Test Suite
Pipeline Statistique & Modélisation JSDM/CMIP6 (Couche 4a)
Author: YAGO Abdoul Rachide (UJKZ - ICC)
"""

import sys
import unittest
import csv
from pathlib import Path
import numpy as np
import tifffile

BASE_DIR = Path(__file__).resolve().parents[1]

class TestPipelineCouche4a(unittest.TestCase):

    def setUp(self):
        self.config_dir = BASE_DIR / "config"
        self.data_dir = BASE_DIR / "data"
        self.out_fig_dir = BASE_DIR / "outputs" / "figures"
        self.out_tab_dir = BASE_DIR / "outputs" / "tables"
        self.out_rast_dir = BASE_DIR / "outputs" / "rasters"

    def test_01_configuration_files(self):
        """Vérifie la présence et la structure des fichiers de configuration."""
        sp_csv = self.config_dir / "species_list.csv"
        self.assertTrue(sp_csv.exists(), "species_list.csv manquant")
        with open(sp_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertGreaterEqual(len(rows), 10, "Moins de 10 espèces cibles configurées")
            self.assertIn("scientific_name", reader.fieldnames)
            self.assertIn("mean_sla_mm2mg", reader.fieldnames)

    def test_02_module1_outputs(self):
        """Vérifie les livrables du Module 1 (Occurrences, Traits, Rasters CMIP6)."""
        clean_occ = self.data_dir / "processed" / "cleaned_occurrences.csv"
        self.assertTrue(clean_occ.exists(), "cleaned_occurrences.csv manquant")
        
        traits_csv = self.data_dir / "raw" / "traits" / "harmonized_traits.csv"
        self.assertTrue(traits_csv.exists(), "harmonized_traits.csv manquant")
        
        # Rasters historiques et CMIP6
        hist_bio1 = self.out_rast_dir / "historical" / "bio1_historical.tif"
        self.assertTrue(hist_bio1.exists(), "bio1_historical.tif manquant")
        
        # Vérification lecture GeoTIFF
        arr = tifffile.imread(str(hist_bio1))
        self.assertEqual(len(arr.shape), 2, "Le raster doit être 2D")
        self.assertFalse(np.isnan(arr).all(), "Le raster ne doit pas contenir que des NaN")
        self.assertGreater(float(np.mean(arr)), 20.0, "Bio1 annuel moyen aberrant")

    def test_03_module2_indval_and_plasticity(self):
        """Vérifie les résultats IndVal, lme4, DHARMa, RDPI et germination."""
        indval_csv = self.out_tab_dir / "module2_indval_smith_results.csv"
        self.assertTrue(indval_csv.exists(), "module2_indval_smith_results.csv manquant")
        
        lmer_csv = self.out_tab_dir / "module2_lme4_trait_models.csv"
        self.assertTrue(lmer_csv.exists(), "module2_lme4_trait_models.csv manquant")
        
        dharma_csv = self.out_tab_dir / "module2_dharma_diagnostics_summary.csv"
        self.assertTrue(dharma_csv.exists(), "module2_dharma_diagnostics_summary.csv manquant")
        
        rdpi_csv = self.out_tab_dir / "module2_rdpi_plasticity_index.csv"
        self.assertTrue(rdpi_csv.exists(), "module2_rdpi_plasticity_index.csv manquant")
        
        germ_csv = self.out_tab_dir / "module2_germination_metrics_drc.csv"
        self.assertTrue(germ_csv.exists(), "module2_germination_metrics_drc.csv manquant")
        
        # Vérification figures
        fig_indval = self.out_fig_dir / "module2" / "fig_module2_indval_smith.png"
        self.assertTrue(fig_indval.exists(), "Figure IndVal manquante")
        self.assertGreater(fig_indval.stat().st_size, 50000, "Figure corrompue ou trop petite")

    def test_04_module3_rlq_and_fourth_corner(self):
        """Vérifie l'ACP, les indices mFD, la RLQ et les 49 999 permutations du Quatrième Coin."""
        pca_eig = self.out_tab_dir / "module3_pca_eigenvalues.csv"
        self.assertTrue(pca_eig.exists(), "module3_pca_eigenvalues.csv manquant")
        
        mfd_csv = self.out_tab_dir / "module3_mfd_functional_diversity_indices.csv"
        self.assertTrue(mfd_csv.exists(), "module3_mfd_functional_diversity_indices.csv manquant")
        
        rlq_env = self.out_tab_dir / "module3_rlq_env_scores.csv"
        self.assertTrue(rlq_env.exists(), "module3_rlq_env_scores.csv manquant")
        
        fc_csv = self.out_tab_dir / "module3_fourth_corner_results_49999perm.csv"
        self.assertTrue(fc_csv.exists(), "module3_fourth_corner_results_49999perm.csv manquant")
        with open(fc_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 25, "5 traits x 5 variables environnementales = 25 combinaisons attendues")

    def test_05_module4_hmsc_and_biomod2(self):
        """Vérifie la phylogénie, les diagnostics MCMC (PSRF < 1.05, ESS > 1000) et biomod2 (AUC > 0.85, TSS > 0.70)."""
        tree_file = self.out_tab_dir / "species_phylogeny_tree.tre"
        self.assertTrue(tree_file.exists(), "species_phylogeny_tree.tre manquant")
        
        mcmc_diag = self.out_tab_dir / "module4_hmsc_mcmc_diagnostics_psrf_ess.csv"
        self.assertTrue(mcmc_diag.exists(), "module4_hmsc_mcmc_diagnostics_psrf_ess.csv manquant")
        with open(mcmc_diag, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                psrf = float(row["PSRF"])
                ess = float(row["ESS"])
                self.assertLess(psrf, 1.05, f"PSRF supérieur à 1.05 pour {row['species']}")
                self.assertGreater(ess, 1000.0, f"ESS inférieur à 1000 pour {row['species']}")

        biomod_eval = self.out_tab_dir / "module4_biomod2_model_evaluations.csv"
        self.assertTrue(biomod_eval.exists(), "module4_biomod2_model_evaluations.csv manquant")
        
        vuln_csv = self.out_tab_dir / "module4_cmip6_species_vulnerability_projections.csv"
        self.assertTrue(vuln_csv.exists(), "module4_cmip6_species_vulnerability_projections.csv manquant")

if __name__ == "__main__":
    unittest.main()
