"""Schemas de exposição pública do usuário."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    """Representação segura do usuário (sem hash de senha)."""

    id: str
    full_name: str
    email: EmailStr
    created_at: datetime
