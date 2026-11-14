-- ==============================================================================
-- TRIGGERS DE CONTRÔLE QUALITÉ (QC) — SAHELTRAITS-DB
-- Détection automatique des valeurs aberrantes (> 3 sigmas) à l'insertion
-- et à la mise à jour des mesures de traits fonctionnels.
-- ==============================================================================

CREATE OR REPLACE FUNCTION fn_check_trait_outlier_3sigma()
RETURNS TRIGGER AS $$
DECLARE
    v_taxon_id UUID;
    v_mean DOUBLE PRECISION;
    v_stddev DOUBLE PRECISION;
    v_count INTEGER;
    v_diff DOUBLE PRECISION;
BEGIN
    -- 1. Récupération du taxon_id associé à l'individu mesuré
    SELECT taxon_id INTO v_taxon_id
    FROM fact_individuals
    WHERE ind_id = NEW.ind_id;

    IF v_taxon_id IS NULL THEN
        -- Individu non trouvé, laisser la validation de clé étrangère opérer
        RETURN NEW;
    END IF;

    -- 2. Calcul des statistiques historiques pour la même espèce et le même trait
    -- On exclut les valeurs déjà rejetées ('REJECTED')
    SELECT 
        COUNT(*),
        AVG(trait_value),
        COALESCE(STDDEV_SAMP(trait_value), 0.0)
    INTO v_count, v_mean, v_stddev
    FROM fact_traits_measurements m
    JOIN fact_individuals i ON m.ind_id = i.ind_id
    WHERE i.taxon_id = v_taxon_id
      AND m.trait_name_ets = NEW.trait_name_ets
      AND m.qc_flag NOT IN ('REJECTED');

    -- 3. Si l'échantillon historique est suffisant (>= 5 mesures) et l'écart-type > 0
    IF v_count >= 5 AND v_stddev > 0.0 THEN
        v_diff := ABS(NEW.trait_value - v_mean);
        
        -- Détection de la règle des 3 sigmas : |x - mu| > 3 * sigma
        IF v_diff > (3.0 * v_stddev) THEN
            NEW.qc_flag := 'SUSPECT_OUTLIER_3SIGMA';
            NEW.qc_notes := format(
                'VALEUR ABERRANTE DETECTEE (3-SIGMA) : valeur=%.4f, moyenne=%.4f, sigma=%.4f (n=%s, z-score=%.2f)',
                NEW.trait_value, v_mean, v_stddev, v_count, (v_diff / v_stddev)
            );
        ELSIF NEW.qc_flag = 'PENDING' THEN
            -- Échantillon suffisant et valeur conforme aux bornes statistiques
            NEW.qc_flag := 'VALID';
            NEW.qc_notes := format('Validation automatique (n=%s, moyenne=%.4f, sigma=%.4f)', v_count, v_mean, v_stddev);
        END IF;
    ELSE
        -- Nombre de mesures insuffisant pour un calcul d'écart-type représentatif
        IF NEW.qc_flag = 'PENDING' THEN
            NEW.qc_notes := format('En attente de calibration statistique (n actuel = %s < 5)', v_count);
        END IF;
    END IF;

    -- Mettre à jour l'horodatage
    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Suppression préalable du trigger s'il existe
DROP TRIGGER IF EXISTS trg_traits_qc_outlier ON fact_traits_measurements;

-- Création du trigger AVANT insertion ou modification
CREATE TRIGGER trg_traits_qc_outlier
BEFORE INSERT OR UPDATE OF trait_value, trait_name_ets
ON fact_traits_measurements
FOR EACH ROW
EXECUTE FUNCTION fn_check_trait_outlier_3sigma();

COMMENT ON FUNCTION fn_check_trait_outlier_3sigma() IS 'Fonction trigger évaluant les bornes statistiques 3-sigma pour la détection automatique des valeurs aberrantes de traits';
