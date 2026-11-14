from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.spatial_types import SpatialGeometry


class SitePlot(Base):
    __tablename__ = "dim_sites_plots"

    plot_id = Column(
        String(50), primary_key=True
    )  # e.g., 'BF-DOR-01', 'BF-KAY-01'
    site_name = Column(String(150), nullable=False, index=True)
    climatic_zone = Column(
        String(50), nullable=False, index=True
    )  # 'Sahélienne', 'Soudano-Sahélienne', 'Soudanienne'
    geom = Column(
        SpatialGeometry(), nullable=False
    )  # Point centroid or 50x50m polygon
    elevation_m = Column(Float, nullable=True)
    slope_deg = Column(Float, nullable=True)
    protection_status = Column(String(100), nullable=True)
    fire_frequency_20yr = Column(Float, nullable=True)
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
    individuals = relationship(
        "Individual", back_populates="plot", cascade="all, delete-orphan"
    )
    soil_records = relationship(
        "EnvironmentSoil", back_populates="plot", cascade="all, delete-orphan"
    )
