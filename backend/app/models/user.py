"""Modelo de domínio do usuário e conversões para/from documento Mongo."""

from datetime import UTC, datetime
from typing import Any

from app.schemas.user import UserPublic


class User:
    """Entidade de domínio do usuário."""

    def __init__(
        self,
        *,
        id: str,
        full_name: str,
        email: str,
        hashed_password: str,
        created_at: datetime,
        is_active: bool,
        is_admin: bool = False,
    ) -> None:
        self.id = id
        self.full_name = full_name
        self.email = email
        self.hashed_password = hashed_password
        self.created_at = created_at
        self.is_active = is_active
        self.is_admin = is_admin

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "User":
        return cls(
            id=str(document["_id"]),
            full_name=document["full_name"],
            email=document["email"],
            hashed_password=document["hashed_password"],
            created_at=document["created_at"],
            is_active=document.get("is_active", False),
            is_admin=document.get("is_admin", False),
        )

    @staticmethod
    def new_document(
        *, full_name: str, email: str, hashed_password: str, is_active: bool = False
    ) -> dict[str, Any]:
        """Monta o documento de um novo usuário pronto para inserção."""
        return {
            "full_name": full_name,
            "email": email,
            "hashed_password": hashed_password,
            "is_active": is_active,
            "is_admin": False,
            "created_at": datetime.now(UTC),
        }

    def to_public(self) -> UserPublic:
        return UserPublic(
            id=self.id,
            full_name=self.full_name,
            email=self.email,
            created_at=self.created_at,
            is_admin=self.is_admin,
        )
