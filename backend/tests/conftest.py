"""Fixtures compartilhadas dos testes."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.api.deps import (
    get_db,
    get_email_sender,
    get_media_service,
    get_presence_service,
    get_test_email_sender,
    get_verification_email_sender,
)
from app.main import fastapi_app
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService
from app.services.media_service import MediaService
from app.services.presence_service import PresenceService
from tests.fakes import FakePresenceStore, FakeStorage

_TEST_BUCKET = "papodevweb-test"


@pytest.fixture
def mongo_database():
    """Banco de dados MongoDB em memória (mongomock)."""
    client = AsyncMongoMockClient()
    return client["papodevweb_test"]


@pytest.fixture
def user_repository(mongo_database) -> UserRepository:
    return UserRepository(mongo_database)


@pytest.fixture
def conversation_repository(mongo_database) -> ConversationRepository:
    return ConversationRepository(mongo_database)


@pytest.fixture
def message_repository(mongo_database) -> MessageRepository:
    return MessageRepository(mongo_database)


@pytest.fixture
def presence_store() -> FakePresenceStore:
    return FakePresenceStore()


@pytest.fixture
def presence_service(presence_store) -> PresenceService:
    return PresenceService(presence_store)


@pytest.fixture
def media_storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture
def chat_service(
    conversation_repository, message_repository, user_repository, presence_service
) -> ChatService:
    return ChatService(
        conversations=conversation_repository,
        messages=message_repository,
        users=user_repository,
        presence=presence_service,
    )


@pytest.fixture
def sent_emails() -> list[tuple[str, str]]:
    """Coleta os e-mails "enviados" durante o teste (em vez de usar SMTP real)."""
    return []


@pytest.fixture
async def client(
    mongo_database, sent_emails, presence_service, media_storage
) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP de teste com banco, e-mail, presença e mídia substituídos."""

    async def fake_email_sender(to_email: str, link: str) -> None:
        sent_emails.append((to_email, link))

    media_service = MediaService(media_storage, bucket=_TEST_BUCKET)

    fastapi_app.dependency_overrides[get_db] = lambda: mongo_database
    fastapi_app.dependency_overrides[get_email_sender] = lambda: fake_email_sender
    async def fake_test_email_sender(to_email: str) -> None:
        sent_emails.append((to_email, "__test__"))

    fastapi_app.dependency_overrides[get_verification_email_sender] = lambda: fake_email_sender
    fastapi_app.dependency_overrides[get_test_email_sender] = lambda: fake_test_email_sender
    fastapi_app.dependency_overrides[get_presence_service] = lambda: presence_service
    fastapi_app.dependency_overrides[get_media_service] = lambda: media_service
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    fastapi_app.dependency_overrides.clear()


async def create_user_and_login(
    client: AsyncClient,
    sent_emails: list,
    *,
    full_name: str,
    email: str,
    password: str = "senhaSegura123",
) -> dict:
    """Cadastra, ativa e autentica um usuário; devolve id, token e headers."""
    await client.post(
        "/auth/register",
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    verify_token = sent_emails[-1][1].split("token=")[1]
    await client.post("/auth/verify-email", json={"token": verify_token})
    sent_emails.clear()
    response = await client.post("/auth/login", json={"email": email, "password": password})
    data = response.json()
    return {
        "id": data["user"]["id"],
        "token": data["access_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
    }


async def register_and_activate(client: AsyncClient, payload: dict, sent_emails: list) -> None:
    """Helper: cadastra e confirma o e-mail, deixando a conta ativa para login."""
    await client.post("/auth/register", json=payload)
    verify_token = sent_emails[-1][1].split("token=")[1]
    await client.post("/auth/verify-email", json={"token": verify_token})
    sent_emails.clear()


@pytest.fixture
def register_payload() -> dict[str, str]:
    return {
        "full_name": "Maria da Silva",
        "email": "maria@example.com",
        "password": "senhaSegura123",
        "confirm_password": "senhaSegura123",
    }
