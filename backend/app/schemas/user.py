from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(
        ...,
        pattern="^(Admin|Chercheur|Enqu[eê]teur|Lecteur public)$",
        description="Rôle de l'utilisateur",
    )
    full_name: str = Field(..., min_length=2, max_length=120)
    institution: Optional[str] = "UJKZ-ICC (Ouagadougou)"
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    institution: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserOut(UserBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
