import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PROJECT_NAME: str = "SAHELTRAITS-DB & ECOPREDICT REST API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "saheltraits_user"
    POSTGRES_PASSWORD: str = "SecureSahelDB_Password2027!"
    POSTGRES_DB: str = "saheltraits_db"
    DATABASE_URL: str = "sqlite:///./saheltraits_dev.db"

    # Security & JWT
    SECRET_KEY: str = "e83a4bf92a5b1129fbb9389201476db5ce8d93b3f29088198f82811a4cf13a52"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # GBIF API
    GBIF_BACKBONE_API_URL: str = "https://api.gbif.org/v1/species/match"
    GBIF_API_TIMEOUT_SECONDS: float = 10.0

    # Quality Control (QC)
    QC_SIGMA_THRESHOLD: float = 3.0
    QC_MIN_OBSERVATIONS_FOR_SIGMA: int = 5

    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "https://saheltraits.ujkz.bf",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
