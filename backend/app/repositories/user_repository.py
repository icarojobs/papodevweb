"""Repositório de usuários — única camada que conhece detalhes do MongoDB."""

import re

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import MAX_SEARCH_RESULTS, USERS_COLLECTION
from app.models.user import User
from app.repositories.object_id import to_object_id, to_object_ids


class UserRepository:
    """Abstrai o acesso à coleção de usuários (padrão Repository)."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[USERS_COLLECTION]

    async def get_by_email(self, email: str) -> User | None:
        document = await self._collection.find_one({"email": email})
        return User.from_document(document) if document else None

    async def get_by_id(self, user_id: str) -> User | None:
        object_id = to_object_id(user_id)
        if object_id is None:
            return None
        document = await self._collection.find_one({"_id": object_id})
        return User.from_document(document) if document else None

    async def get_by_ids(self, user_ids: list[str]) -> list[User]:
        """Busca vários usuários por id (usado para hidratar participantes)."""
        object_ids = to_object_ids(user_ids)
        if not object_ids:
            return []
        cursor = self._collection.find({"_id": {"$in": object_ids}})
        return [User.from_document(document) async for document in cursor]

    async def search(
        self, query: str, *, exclude_id: str, limit: int = MAX_SEARCH_RESULTS
    ) -> list[User]:
        """Busca usuários ativos por nome ou e-mail (parcial, case-insensitive)."""
        pattern = re.escape(query.strip())
        filters = {
            "is_active": True,
            "$or": [
                {"full_name": {"$regex": pattern, "$options": "i"}},
                {"email": {"$regex": pattern, "$options": "i"}},
            ],
        }
        exclude_object_id = to_object_id(exclude_id)
        if exclude_object_id is not None:
            filters["_id"] = {"$ne": exclude_object_id}
        cursor = self._collection.find(filters).limit(limit)
        return [User.from_document(document) async for document in cursor]

    async def create(
        self, *, full_name: str, email: str, hashed_password: str, is_active: bool = False
    ) -> User:
        document = User.new_document(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
        )
        result = await self._collection.insert_one(document)
        document["_id"] = result.inserted_id
        return User.from_document(document)

    async def exists_by_email(self, email: str) -> bool:
        return await self._collection.count_documents({"email": email}, limit=1) > 0

    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """Atualiza o hash de senha de um usuário. Retorna se houve alteração."""
        object_id = to_object_id(user_id)
        if object_id is None:
            return False
        result = await self._collection.update_one(
            {"_id": object_id},
            {"$set": {"hashed_password": hashed_password}},
        )
        return result.modified_count == 1

    async def activate_user(self, user_id: str) -> bool:
        """Marca a conta como ativa. Retorna se o usuário foi encontrado."""
        object_id = to_object_id(user_id)
        if object_id is None:
            return False
        result = await self._collection.update_one(
            {"_id": object_id},
            {"$set": {"is_active": True}},
        )
        return result.matched_count == 1

    async def set_admin(self, user_id: str, *, is_admin: bool) -> bool:
        """Concede ou revoga o acesso administrativo. Retorna se o usuário existe."""
        object_id = to_object_id(user_id)
        if object_id is None:
            return False
        result = await self._collection.update_one(
            {"_id": object_id},
            {"$set": {"is_admin": is_admin}},
        )
        return result.matched_count == 1
