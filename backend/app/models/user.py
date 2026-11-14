import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, String
from app.core.database import Base


class User(Base):
    __tablename__ = "app_users"

    user_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(30), nullable=False, index=True
    )  # 'Admin', 'Chercheur', 'Enquêteur', 'Lecteur public'
    full_name = Column(String(120), nullable=False)
    institution = Column(String(150), default="UJKZ-ICC (Ouagadougou)")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
