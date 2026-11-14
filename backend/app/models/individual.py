import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.spatial_types import SpatialPoint


class Individual(Base):
    __tablename__ = "fact_individuals"

    ind_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    plot_id = Column(
        String(50),
        ForeignKey("dim_sites_plots.plot_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    taxon_id = Column(
        String(36),
        ForeignKey("dim_taxonomy.taxon_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    qr_code_tag = Column(String(100), unique=True, nullable=False, index=True)
    dbh_cm = Column(Float, nullable=True)
    total_height_m = Column(Float, nullable=True)
    crown_diameter_m = Column(Float, nullable=True)
    canopy_position = Column(
        String(50), nullable=True
    )  # 'Dominant', 'Codominant', 'Intermédiaire', 'Sous-étage', 'Émergent'
    health_status_score = Column(
        Integer, nullable=False
    )  # 1 (dépérissant) à 5 (vigueur max)
    geom_tree = Column(SpatialPoint(), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    plot = relationship("SitePlot", back_populates="individuals")
    taxonomy = relationship("Taxonomy", back_populates="individuals")
    traits = relationship(
        "TraitMeasurement",
        back_populates="individual",
        cascade="all, delete-orphan",
    )
    seed_trials = relationship(
        "SeedGermination",
        back_populates="individual",
        cascade="all, delete-orphan",
    )
