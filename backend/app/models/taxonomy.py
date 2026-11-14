import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Taxonomy(Base):
    __tablename__ = "dim_taxonomy"

    taxon_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    scientific_name = Column(
        String(255), unique=True, nullable=False, index=True
    )
    accepted_name_gbif = Column(String(255), nullable=True, index=True)
    gbif_usage_key = Column(Integer, nullable=True)
    gbif_confidence_score = Column(Float, nullable=True)
    family = Column(String(100), nullable=False, index=True)
    genus = Column(String(100), nullable=False, index=True)
    vernacular_moore = Column(String(150), nullable=True)
    vernacular_dioula = Column(String(150), nullable=True)
    vernacular_fulfulde = Column(String(150), nullable=True)
    functional_group = Column(String(100), nullable=True, index=True)
    iucn_status = Column(String(20), default="LC", nullable=True)
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
        "Individual", back_populates="taxonomy", cascade="all, delete-orphan"
    )
    surveys = relationship(
        "EthnoSurvey", back_populates="taxonomy", cascade="all, delete-orphan"
    )
