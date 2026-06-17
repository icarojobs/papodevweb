"""Repositório de usuários — única camada que conhece detalhes do MongoDB."""

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.constants import USERS_COLLECTION
from app.models.user import User


class UserRepository:
    """Abstrai o acesso à coleção de usuários (padrão Repository)."""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[USERS_COLLECTION]

    async def get_by_email(self, email: str) -> User | None:
        document = await self._collection.find_one({"email": email})
        return User.from_document(document) if document else None

    async def get_by_id(self, user_id: str) -> User | None:
        try:
            object_id = ObjectId(user_id)
        except (InvalidId, TypeError):
            return None
        document = await self._collection.find_one({"_id": object_id})
        return User.from_document(document) if document else None

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
        try:
            object_id = ObjectId(user_id)
        except (InvalidId, TypeError):
            return False
        result = await self._collection.update_one(
            {"_id": object_id},
            {"$set": {"hashed_password": hashed_password}},
        )
        return result.modified_count == 1

    async def activate_user(self, user_id: str) -> bool:
        """Marca a conta como ativa. Retorna se o usuário foi encontrado."""
        try:
            object_id = ObjectId(user_id)
        except (InvalidId, TypeError):
            return False
        result = await self._collection.update_one(
            {"_id": object_id},
            {"$set": {"is_active": True}},
        )
        return result.matched_count == 1
