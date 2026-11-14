import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class SeedGermination(Base):
    __tablename__ = "fact_seed_germination"

    germ_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ind_id = Column(
        String(36),
        ForeignKey("fact_individuals.ind_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seed_batch_qr = Column(String(100), nullable=False, index=True)
    temp_regime_c = Column(String(50), nullable=False)  # e.g., '25/15', '30/20'
    osmotic_potential_mpa = Column(
        Float, default=0.0, nullable=False
    )  # 0.0, -0.2, -0.4, -0.8 MPa
    pretreatment_type = Column(String(100), nullable=True)  # Scarification, etc.
    total_seeds = Column(Integer, nullable=False)
    germinated_count = Column(Integer, nullable=False)
    t50_days = Column(Float, nullable=True)
    final_gp_pct = Column(
        Float, nullable=True
    )  # (germinated_count / total_seeds) * 100
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
    individual = relationship("Individual", back_populates="seed_trials")
