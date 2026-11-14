import datetime
from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.germination import SeedGermination
from app.models.individual import Individual
from app.models.site import SitePlot
from app.models.soil import EnvironmentSoil
from app.models.survey import EthnoSurvey
from app.models.taxonomy import Taxonomy
from app.models.trait import TraitMeasurement
from app.models.user import User

# Base de données de test en mémoire isolée
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_users(db_session):
    """Crée les comptes de base pour les tests RBAC."""
    users = [
        User(
            user_id="u001",
            username="admin_user",
            email="admin@test.bf",
            hashed_password=get_password_hash("AdminPass123!"),
            role="Admin",
            full_name="Admin Test",
            institution="UJKZ-ICC",
        ),
        User(
            user_id="u002",
            username="researcher_user",
            email="chercheur@test.bf",
            hashed_password=get_password_hash("ResearcherPass123!"),
            role="Chercheur",
            full_name="Chercheur Test",
            institution="UJKZ-ICC",
        ),
        User(
            user_id="u003",
            username="operator_user",
            email="enqueteur@test.bf",
            hashed_password=get_password_hash("OperatorPass123!"),
            role="Enquêteur",
            full_name="Enquêteur Test",
            institution="UJKZ Terrain",
        ),
        User(
            user_id="u004",
            username="public_user",
            email="public@test.bf",
            hashed_password=get_password_hash("PublicPass123!"),
            role="Lecteur public",
            full_name="Lecteur Public Test",
            institution="Externe",
        ),
    ]
    for u in users:
        existing = (
            db_session.query(User).filter(User.username == u.username).first()
        )
        if not existing:
            db_session.add(u)
    db_session.commit()


@pytest.fixture
def admin_headers(seed_users) -> dict:
    token = create_access_token(subject="admin_user", role="Admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def researcher_headers(seed_users) -> dict:
    token = create_access_token(subject="researcher_user", role="Chercheur")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def operator_headers(seed_users) -> dict:
    token = create_access_token(subject="operator_user", role="Enquêteur")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def public_headers(seed_users) -> dict:
    token = create_access_token(subject="public_user", role="Lecteur public")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_ecological_data(db_session, seed_users):
    """Peuple la base de données avec des placettes, taxons et individus de référence."""
    # 1. Taxons
    tax1 = Taxonomy(
        taxon_id="tax001",
        scientific_name="Balanites aegyptiaca (L.) Delile",
        accepted_name_gbif="Balanites aegyptiaca (L.) Delile",
        gbif_usage_key=3152865,
        gbif_confidence_score=98.0,
        family="Zygophyllaceae",
        genus="Balanites",
        vernacular_moore="Kieglga",
        vernacular_dioula="Ségéné",
        vernacular_fulfulde="Murtooki",
        functional_group="Épineux xérophyte persistant",
        iucn_status="LC",
    )
    tax2 = Taxonomy(
        taxon_id="tax002",
        scientific_name="Faidherbia albida (Delile) A.Chev.",
        accepted_name_gbif="Faidherbia albida (Delile) A.Chev.",
        gbif_usage_key=2977465,
        gbif_confidence_score=98.0,
        family="Fabaceae",
        genus="Faidherbia",
        vernacular_moore="Zaanga",
        vernacular_dioula="Balanzan",
        vernacular_fulfulde="Caski",
        functional_group="Fixateur azote phénologie inversée",
        iucn_status="LC",
    )
    db_session.add_all([tax1, tax2])
    db_session.commit()

    # 2. Placettes
    plot1 = SitePlot(
        plot_id="BF-DOR-01",
        site_name="Dori - Yakouta",
        climatic_zone="Sahélienne",
        geom="POINT(-0.0925 14.0325)",
        elevation_m=285.0,
        slope_deg=1.2,
        protection_status="Zone Pastorale Communale",
        fire_frequency_20yr=1.5,
    )
    plot2 = SitePlot(
        plot_id="BF-KAY-01",
        site_name="Kaya - Dem",
        climatic_zone="Soudano-Sahélienne",
        geom="POINT(-1.1275 13.0825)",
        elevation_m=312.0,
        slope_deg=2.5,
        protection_status="Forêt Classée",
        fire_frequency_20yr=4.8,
    )
    db_session.add_all([plot1, plot2])
    db_session.commit()

    # 3. Individus
    ind1 = Individual(
        ind_id="ind001",
        plot_id="BF-DOR-01",
        taxon_id="tax001",
        qr_code_tag="QR-BAL-DOR-001",
        dbh_cm=32.5,
        total_height_m=7.8,
        crown_diameter_m=5.4,
        canopy_position="Dominant",
        health_status_score=5,
        geom_tree="POINT(-0.0925 14.0325)",
    )
    ind2 = Individual(
        ind_id="ind002",
        plot_id="BF-KAY-01",
        taxon_id="tax002",
        qr_code_tag="QR-FAI-KAY-001",
        dbh_cm=48.0,
        total_height_m=11.2,
        crown_diameter_m=8.5,
        canopy_position="Dominant",
        health_status_score=4,
        geom_tree="POINT(-1.1280 13.0830)",
    )
    db_session.add_all([ind1, ind2])
    db_session.commit()

    # 4. Trait measurements historiques pour calibrer 3-sigma (Balanites SLA ~ 10.0, std ~ 0.5)
    historical_traits = [
        TraitMeasurement(
            meas_id=f"meas_hist_{i}",
            ind_id="ind001",
            trait_name_ets="SLA",
            trait_value=val,
            unit="mm2/mg",
            organ_sampled="Feuille",
            measurement_date=datetime.date(2026, 10, i + 1),
            qc_flag="VALID",
        )
        for i, val in enumerate([9.8, 10.2, 9.9, 10.1, 10.0, 9.7])
    ]
    db_session.add_all(historical_traits)
    db_session.commit()
