import math
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.individual import Individual
from app.models.site import SitePlot
from app.models.trait import TraitMeasurement


class QCService:
    """Service de contrôle qualité statistique (QC) pour la détection automatique

    des valeurs aberrantes (Outliers > 3 sigmas) selon l'espèce et le gradient
    climatique.
    """

    @staticmethod
    def evaluate_measurement(
        db: Session,
        ind_id: str,
        trait_name_ets: str,
        trait_value: float,
        current_meas_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Évalue une valeur de trait mesurée par rapport à la distribution empirique de l'espèce.

        Retourne : (qc_flag, qc_notes)
        """
        # 1. Récupération de l'individu et de son taxon
        ind = db.query(Individual).filter(Individual.ind_id == ind_id).first()
        if not ind:
            return "PENDING", "Individu non indexé pour contrôle qualité"

        # 2. Récupération des valeurs historiques validées ou en attente pour le même taxon et même trait
        query = (
            db.query(TraitMeasurement.trait_value)
            .join(Individual, TraitMeasurement.ind_id == Individual.ind_id)
            .filter(
                Individual.taxon_id == ind.taxon_id,
                TraitMeasurement.trait_name_ets == trait_name_ets,
                TraitMeasurement.qc_flag.notin_(
                    ["REJECTED", "SUSPECT_OUTLIER_3SIGMA"]
                ),
            )
        )

        if current_meas_id:
            query = query.filter(TraitMeasurement.meas_id != current_meas_id)

        values = [row[0] for row in query.all() if row[0] is not None]
        n = len(values)

        # 3. Évaluation selon le seuil minimal d'observations
        if n < settings.QC_MIN_OBSERVATIONS_FOR_SIGMA:
            return (
                "VALID",
                f"Validation initiale (effectif d'étalonnage restreint n={n} < {settings.QC_MIN_OBSERVATIONS_FOR_SIGMA})",
            )

        mean_val = sum(values) / n
        variance = sum((x - mean_val) ** 2 for x in values) / (
            n - 1 if n > 1 else 1
        )
        std_val = math.sqrt(variance)

        if std_val == 0.0:
            if abs(trait_value - mean_val) == 0.0:
                return (
                    "VALID",
                    f"Valeur identique à la moyenne historique ({mean_val})",
                )
            else:
                return (
                    "SUSPECT_OUTLIER_3SIGMA",
                    f"Écart détecté sur distribution à variance nulle (valeur={trait_value}, attendu={mean_val})",
                )

        diff = abs(trait_value - mean_val)
        z_score = diff / std_val

        # 4. Règle des 3 sigmas : |x - mu| > 3 * sigma
        if z_score > settings.QC_SIGMA_THRESHOLD:
            flag = "SUSPECT_OUTLIER_3SIGMA"
            notes = (
                f"VALEUR ABERRANTE DETECTEE (3-SIGMA) : "
                f"valeur={trait_value:.4f}, moyenne={mean_val:.4f}, sigma={std_val:.4f}, "
                f"z-score={z_score:.2f} > {settings.QC_SIGMA_THRESHOLD} (n={n})"
            )
        else:
            flag = "VALID"
            notes = (
                f"Conforme aux bornes statistiques 3-sigma : "
                f"z-score={z_score:.2f} <= {settings.QC_SIGMA_THRESHOLD} (moyenne={mean_val:.4f}, sigma={std_val:.4f}, n={n})"
            )

        return flag, notes
