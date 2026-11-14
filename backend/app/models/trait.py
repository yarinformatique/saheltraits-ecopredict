import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class TraitMeasurement(Base):
    __tablename__ = "fact_traits_measurements"

    meas_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ind_id = Column(
        String(36),
        ForeignKey("fact_individuals.ind_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trait_name_ets = Column(
        String(100), nullable=False, index=True
    )  # e.g., 'SLA', 'LDMC', 'Leaf_N', 'Wood_density'
    trait_value = Column(Float, nullable=False)
    unit = Column(
        String(50), nullable=False
    )  # e.g., 'mm2/mg', 'mg/g', 'g/cm3', 'mm'
    organ_sampled = Column(
        String(50), nullable=False
    )  # 'Feuille', 'Rameau', 'Tronc', 'Écorce', 'Racine', etc.
    measurement_protocol = Column(Text, nullable=True)
    instrument_id = Column(String(100), nullable=True)
    measurement_date = Column(
        Date, default=date.today, nullable=False, index=True
    )
    operator_id = Column(
        String(36),
        ForeignKey("app_users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    qc_flag = Column(
        String(50), default="PENDING", nullable=False, index=True
    )  # 'PENDING', 'VALID', 'SUSPECT_OUTLIER_3SIGMA', 'FLAGGED_MANUAL', 'MANUALLY_APPROVED', 'REJECTED'
    qc_notes = Column(Text, nullable=True)
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
    individual = relationship("Individual", back_populates="traits")
    operator = relationship("User")
