import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class EnvironmentSoil(Base):
    __tablename__ = "fact_environment_soil"

    env_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    plot_id = Column(
        String(50),
        ForeignKey("dim_sites_plots.plot_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    depth_cm = Column(
        String(30), nullable=False, index=True
    )  # '0-20', '20-40', '40-60'
    clay_pct = Column(Float, nullable=True)
    silt_pct = Column(Float, nullable=True)
    sand_pct = Column(Float, nullable=True)
    ph_h2o = Column(Float, nullable=True)
    organic_carbon_gkg = Column(Float, nullable=True)
    total_n_gkg = Column(Float, nullable=True)
    avail_p_mgkg = Column(Float, nullable=True)
    cec_cmolkg = Column(Float, nullable=True)
    dry_season_moisture_pct = Column(Float, nullable=True)
    sampling_date = Column(Date, default=date.today, nullable=False)
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
    plot = relationship("SitePlot", back_populates="soil_records")
