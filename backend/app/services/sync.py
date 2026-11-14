from datetime import datetime, timezone
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.germination import SeedGermination
from app.models.individual import Individual
from app.models.site import SitePlot
from app.models.soil import EnvironmentSoil
from app.models.survey import EthnoSurvey
from app.models.trait import TraitMeasurement
from app.schemas.sync import SyncBatchRequest, SyncBatchResponse
from app.services.qc import QCService

logger = logging.getLogger(__name__)


class SyncService:
    """Service de synchronisation asynchrone des lots de collecte de terrain

    envoyés par l'application mobile hors-ligne.
    """

    @staticmethod
    def process_field_batch(
        db: Session,
        batch_data: SyncBatchRequest,
        operator_id: Optional[str] = None,
    ) -> SyncBatchResponse:
        errors = []
        plots_synced = 0
        individuals_synced = 0
        traits_synced = 0
        seed_trials_synced = 0
        soil_records_synced = 0
        surveys_synced = 0
        flagged_outliers_count = 0

        try:
            # 1. Traitement des placettes (dim_sites_plots)
            for p_in in batch_data.plots:
                try:
                    existing_plot = (
                        db.query(SitePlot)
                        .filter(SitePlot.plot_id == p_in.plot_id)
                        .first()
                    )
                    if existing_plot:
                        existing_plot.site_name = p_in.site_name
                        existing_plot.climatic_zone = p_in.climatic_zone
                        existing_plot.geom = p_in.geom
                        existing_plot.elevation_m = p_in.elevation_m
                        existing_plot.slope_deg = p_in.slope_deg
                        existing_plot.protection_status = p_in.protection_status
                        existing_plot.fire_frequency_20yr = (
                            p_in.fire_frequency_20yr
                        )
                    else:
                        new_plot = SitePlot(
                            plot_id=p_in.plot_id,
                            site_name=p_in.site_name,
                            climatic_zone=p_in.climatic_zone,
                            geom=p_in.geom,
                            elevation_m=p_in.elevation_m,
                            slope_deg=p_in.slope_deg,
                            protection_status=p_in.protection_status,
                            fire_frequency_20yr=p_in.fire_frequency_20yr,
                        )
                        db.add(new_plot)
                    plots_synced += 1
                except Exception as e:
                    errors.append(f"Erreur placette {p_in.plot_id}: {str(e)}")

            db.flush()

            # 2. Traitement des individus/arbres (fact_individuals)
            for ind_in in batch_data.individuals:
                try:
                    existing_ind = (
                        db.query(Individual)
                        .filter(
                            Individual.qr_code_tag == ind_in.qr_code_tag
                        )
                        .first()
                    )
                    if existing_ind:
                        existing_ind.plot_id = ind_in.plot_id
                        existing_ind.taxon_id = ind_in.taxon_id
                        existing_ind.dbh_cm = ind_in.dbh_cm
                        existing_ind.total_height_m = ind_in.total_height_m
                        existing_ind.crown_diameter_m = ind_in.crown_diameter_m
                        existing_ind.canopy_position = ind_in.canopy_position
                        existing_ind.health_status_score = (
                            ind_in.health_status_score
                        )
                        existing_ind.geom_tree = ind_in.geom_tree
                    else:
                        new_ind = Individual(
                            plot_id=ind_in.plot_id,
                            taxon_id=ind_in.taxon_id,
                            qr_code_tag=ind_in.qr_code_tag,
                            dbh_cm=ind_in.dbh_cm,
                            total_height_m=ind_in.total_height_m,
                            crown_diameter_m=ind_in.crown_diameter_m,
                            canopy_position=ind_in.canopy_position,
                            health_status_score=ind_in.health_status_score,
                            geom_tree=ind_in.geom_tree,
                        )
                        db.add(new_ind)
                    individuals_synced += 1
                except Exception as e:
                    errors.append(
                        f"Erreur individu QR {ind_in.qr_code_tag}: {str(e)}"
                    )

            db.flush()

            # 3. Traitement des mesures de traits (fact_traits_measurements) avec QC automatique 3-sigma
            for t_in in batch_data.traits:
                try:
                    # Évaluation statistique préalable des 3-sigmas
                    qc_flag, qc_notes = QCService.evaluate_measurement(
                        db=db,
                        ind_id=t_in.ind_id,
                        trait_name_ets=t_in.trait_name_ets,
                        trait_value=t_in.trait_value,
                    )

                    if qc_flag == "SUSPECT_OUTLIER_3SIGMA":
                        flagged_outliers_count += 1

                    new_trait = TraitMeasurement(
                        ind_id=t_in.ind_id,
                        trait_name_ets=t_in.trait_name_ets,
                        trait_value=t_in.trait_value,
                        unit=t_in.unit,
                        organ_sampled=t_in.organ_sampled,
                        measurement_protocol=t_in.measurement_protocol,
                        instrument_id=t_in.instrument_id,
                        measurement_date=t_in.measurement_date
                        or datetime.now(timezone.utc).date(),
                        operator_id=t_in.operator_id or operator_id,
                        qc_flag=qc_flag,
                        qc_notes=qc_notes,
                    )
                    db.add(new_trait)
                    traits_synced += 1
                except Exception as e:
                    errors.append(
                        f"Erreur mesure trait {t_in.trait_name_ets}: {str(e)}"
                    )

            # 4. Traitement des essais germinatifs (fact_seed_germination)
            for g_in in batch_data.seed_trials:
                try:
                    gp_pct = (
                        (g_in.germinated_count / g_in.total_seeds) * 100.0
                        if g_in.total_seeds > 0
                        else 0.0
                    )
                    new_germ = SeedGermination(
                        ind_id=g_in.ind_id,
                        seed_batch_qr=g_in.seed_batch_qr,
                        temp_regime_c=g_in.temp_regime_c,
                        osmotic_potential_mpa=g_in.osmotic_potential_mpa,
                        pretreatment_type=g_in.pretreatment_type,
                        total_seeds=g_in.total_seeds,
                        germinated_count=g_in.germinated_count,
                        t50_days=g_in.t50_days,
                        final_gp_pct=round(gp_pct, 2),
                    )
                    db.add(new_germ)
                    seed_trials_synced += 1
                except Exception as e:
                    errors.append(
                        f"Erreur germination lot {g_in.seed_batch_qr}: {str(e)}"
                    )

            # 5. Traitement des sols (fact_environment_soil)
            for s_in in batch_data.soil_records:
                try:
                    new_soil = EnvironmentSoil(
                        plot_id=s_in.plot_id,
                        depth_cm=s_in.depth_cm,
                        clay_pct=s_in.clay_pct,
                        silt_pct=s_in.silt_pct,
                        sand_pct=s_in.sand_pct,
                        ph_h2o=s_in.ph_h2o,
                        organic_carbon_gkg=s_in.organic_carbon_gkg,
                        total_n_gkg=s_in.total_n_gkg,
                        avail_p_mgkg=s_in.avail_p_mgkg,
                        cec_cmolkg=s_in.cec_cmolkg,
                        dry_season_moisture_pct=s_in.dry_season_moisture_pct,
                        sampling_date=s_in.sampling_date
                        or datetime.now(timezone.utc).date(),
                    )
                    db.add(new_soil)
                    soil_records_synced += 1
                except Exception as e:
                    errors.append(
                        f"Erreur sol placette {s_in.plot_id}: {str(e)}"
                    )

            # 6. Traitement des enquêtes ethno-écologiques (fact_surveys_ethno)
            for surv_in in batch_data.surveys:
                try:
                    new_survey = EthnoSurvey(
                        taxon_id=surv_in.taxon_id,
                        respondent_type=surv_in.respondent_type,
                        geom_village=surv_in.geom_village,
                        village_name=surv_in.village_name,
                        climatic_zone=surv_in.climatic_zone,
                        perceived_decline_score=surv_in.perceived_decline_score,
                        phenology_shift_observed=surv_in.phenology_shift_observed,
                        phenology_shift_details=surv_in.phenology_shift_details,
                        drought_resilience_rank=surv_in.drought_resilience_rank,
                        traditional_uses=surv_in.traditional_uses,
                        interviewer_id=surv_in.interviewer_id or operator_id,
                    )
                    db.add(new_survey)
                    surveys_synced += 1
                except Exception as e:
                    errors.append(
                        f"Erreur enquête taxon {surv_in.taxon_id}: {str(e)}"
                    )

            # Commit atomique
            db.commit()

            status = "SUCCESS" if not errors else "PARTIAL"
            message = (
                "Synchronisation du lot terrain effectuée avec succès."
                if status == "SUCCESS"
                else f"Synchronisation partielle : {len(errors)} anomalies rencontrées."
            )

            return SyncBatchResponse(
                batch_id=batch_data.batch_id,
                status=status,
                message=message,
                synced_at=datetime.now(timezone.utc),
                plots_synced=plots_synced,
                individuals_synced=individuals_synced,
                traits_synced=traits_synced,
                seed_trials_synced=seed_trials_synced,
                soil_records_synced=soil_records_synced,
                surveys_synced=surveys_synced,
                flagged_outliers_count=flagged_outliers_count,
                errors=errors,
            )

        except Exception as global_ex:
            db.rollback()
            logger.error(
                f"Échec critique du lot de synchronisation {batch_data.batch_id}: {global_ex}"
            )
            return SyncBatchResponse(
                batch_id=batch_data.batch_id,
                status="ERROR",
                message=f"Échec critique de transaction: {str(global_ex)}",
                synced_at=datetime.now(timezone.utc),
                errors=[str(global_ex)],
            )
