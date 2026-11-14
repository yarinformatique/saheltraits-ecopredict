import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.spatial_types import SpatialPoint


class EthnoSurvey(Base):
    __tablename__ = "fact_surveys_ethno"

    survey_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    taxon_id = Column(
        String(36),
        ForeignKey("dim_taxonomy.taxon_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    respondent_type = Column(
        String(50), nullable=False, index=True
    )  # 'Expert', 'Local'
    geom_village = Column(SpatialPoint(), nullable=False)
    village_name = Column(String(150), nullable=True)
    climatic_zone = Column(
        String(50), nullable=False, index=True
    )  # 'Sahélienne', 'Soudano-Sahélienne', 'Soudanienne'
    perceived_decline_score = Column(
        Integer, nullable=False
    )  # -2 (forte régression) à +2 (expansion)
    phenology_shift_observed = Column(Boolean, default=False, nullable=False)
    phenology_shift_details = Column(Text, nullable=True)
    drought_resilience_rank = Column(Integer, nullable=False)  # 1, 2, 3...
    traditional_uses = Column(Text, nullable=True)
    interviewer_id = Column(
        String(36),
        ForeignKey("app_users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
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
    taxonomy = relationship("Taxonomy", back_populates="surveys")
    interviewer = relationship("User")
