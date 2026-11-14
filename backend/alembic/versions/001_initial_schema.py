"""Initial schema creation for SAHELTRAITS-DB

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-14 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. app_users
    op.create_table(
        'app_users',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(30), nullable=False),
        sa.Column('full_name', sa.String(120), nullable=False),
        sa.Column('institution', sa.String(150), server_default='UJKZ-ICC (Ouagadougou)'),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_users_username', 'app_users', ['username'])
    op.create_index('idx_users_email', 'app_users', ['email'])

    # 1. dim_taxonomy
    op.create_table(
        'dim_taxonomy',
        sa.Column('taxon_id', sa.String(36), primary_key=True),
        sa.Column('scientific_name', sa.String(255), unique=True, nullable=False),
        sa.Column('accepted_name_gbif', sa.String(255), nullable=True),
        sa.Column('gbif_usage_key', sa.Integer(), nullable=True),
        sa.Column('gbif_confidence_score', sa.Float(), nullable=True),
        sa.Column('family', sa.String(100), nullable=False),
        sa.Column('genus', sa.String(100), nullable=False),
        sa.Column('vernacular_moore', sa.String(150), nullable=True),
        sa.Column('vernacular_dioula', sa.String(150), nullable=True),
        sa.Column('vernacular_fulfulde', sa.String(150), nullable=True),
        sa.Column('functional_group', sa.String(100), nullable=True),
        sa.Column('iucn_status', sa.String(20), server_default='LC', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_taxo_scientific_name', 'dim_taxonomy', ['scientific_name'])
    op.create_index('idx_taxo_family', 'dim_taxonomy', ['family'])

    # 2. dim_sites_plots
    op.create_table(
        'dim_sites_plots',
        sa.Column('plot_id', sa.String(50), primary_key=True),
        sa.Column('site_name', sa.String(150), nullable=False),
        sa.Column('climatic_zone', sa.String(50), nullable=False),
        sa.Column('geom', sa.Text(), nullable=False),
        sa.Column('elevation_m', sa.Float(), nullable=True),
        sa.Column('slope_deg', sa.Float(), nullable=True),
        sa.Column('protection_status', sa.String(100), nullable=True),
        sa.Column('fire_frequency_20yr', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_plots_climatic_zone', 'dim_sites_plots', ['climatic_zone'])

    # 3. fact_individuals
    op.create_table(
        'fact_individuals',
        sa.Column('ind_id', sa.String(36), primary_key=True),
        sa.Column('plot_id', sa.String(50), sa.ForeignKey('dim_sites_plots.plot_id', ondelete='CASCADE'), nullable=False),
        sa.Column('taxon_id', sa.String(36), sa.ForeignKey('dim_taxonomy.taxon_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('qr_code_tag', sa.String(100), unique=True, nullable=False),
        sa.Column('dbh_cm', sa.Float(), nullable=True),
        sa.Column('total_height_m', sa.Float(), nullable=True),
        sa.Column('crown_diameter_m', sa.Float(), nullable=True),
        sa.Column('canopy_position', sa.String(50), nullable=True),
        sa.Column('health_status_score', sa.Integer(), nullable=False),
        sa.Column('geom_tree', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_ind_qr_code', 'fact_individuals', ['qr_code_tag'])
    op.create_index('idx_ind_plot', 'fact_individuals', ['plot_id'])
    op.create_index('idx_ind_taxon', 'fact_individuals', ['taxon_id'])

    # 4. fact_traits_measurements
    op.create_table(
        'fact_traits_measurements',
        sa.Column('meas_id', sa.String(36), primary_key=True),
        sa.Column('ind_id', sa.String(36), sa.ForeignKey('fact_individuals.ind_id', ondelete='CASCADE'), nullable=False),
        sa.Column('trait_name_ets', sa.String(100), nullable=False),
        sa.Column('trait_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('organ_sampled', sa.String(50), nullable=False),
        sa.Column('measurement_protocol', sa.Text(), nullable=True),
        sa.Column('instrument_id', sa.String(100), nullable=True),
        sa.Column('measurement_date', sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column('operator_id', sa.String(36), sa.ForeignKey('app_users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('qc_flag', sa.String(50), server_default='PENDING', nullable=False),
        sa.Column('qc_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_traits_name', 'fact_traits_measurements', ['trait_name_ets'])
    op.create_index('idx_traits_qc', 'fact_traits_measurements', ['qc_flag'])

    # 5. fact_seed_germination
    op.create_table(
        'fact_seed_germination',
        sa.Column('germ_id', sa.String(36), primary_key=True),
        sa.Column('ind_id', sa.String(36), sa.ForeignKey('fact_individuals.ind_id', ondelete='CASCADE'), nullable=False),
        sa.Column('seed_batch_qr', sa.String(100), nullable=False),
        sa.Column('temp_regime_c', sa.String(50), nullable=False),
        sa.Column('osmotic_potential_mpa', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('pretreatment_type', sa.String(100), nullable=True),
        sa.Column('total_seeds', sa.Integer(), nullable=False),
        sa.Column('germinated_count', sa.Integer(), nullable=False),
        sa.Column('t50_days', sa.Float(), nullable=True),
        sa.Column('final_gp_pct', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 6. fact_environment_soil
    op.create_table(
        'fact_environment_soil',
        sa.Column('env_id', sa.String(36), primary_key=True),
        sa.Column('plot_id', sa.String(50), sa.ForeignKey('dim_sites_plots.plot_id', ondelete='CASCADE'), nullable=False),
        sa.Column('depth_cm', sa.String(30), nullable=False),
        sa.Column('clay_pct', sa.Float(), nullable=True),
        sa.Column('silt_pct', sa.Float(), nullable=True),
        sa.Column('sand_pct', sa.Float(), nullable=True),
        sa.Column('ph_h2o', sa.Float(), nullable=True),
        sa.Column('organic_carbon_gkg', sa.Float(), nullable=True),
        sa.Column('total_n_gkg', sa.Float(), nullable=True),
        sa.Column('avail_p_mgkg', sa.Float(), nullable=True),
        sa.Column('cec_cmolkg', sa.Float(), nullable=True),
        sa.Column('dry_season_moisture_pct', sa.Float(), nullable=True),
        sa.Column('sampling_date', sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 7. fact_surveys_ethno
    op.create_table(
        'fact_surveys_ethno',
        sa.Column('survey_id', sa.String(36), primary_key=True),
        sa.Column('taxon_id', sa.String(36), sa.ForeignKey('dim_taxonomy.taxon_id', ondelete='RESTRICT'), nullable=False),
        sa.Column('respondent_type', sa.String(50), nullable=False),
        sa.Column('geom_village', sa.Text(), nullable=False),
        sa.Column('village_name', sa.String(150), nullable=True),
        sa.Column('climatic_zone', sa.String(50), nullable=False),
        sa.Column('perceived_decline_score', sa.Integer(), nullable=False),
        sa.Column('phenology_shift_observed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('phenology_shift_details', sa.Text(), nullable=True),
        sa.Column('drought_resilience_rank', sa.Integer(), nullable=False),
        sa.Column('traditional_uses', sa.Text(), nullable=True),
        sa.Column('interviewer_id', sa.String(36), sa.ForeignKey('app_users.user_id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('fact_surveys_ethno')
    op.drop_table('fact_environment_soil')
    op.drop_table('fact_seed_germination')
    op.drop_table('fact_traits_measurements')
    op.drop_table('fact_individuals')
    op.drop_table('dim_sites_plots')
    op.drop_table('dim_taxonomy')
    op.drop_table('app_users')
