"""Fixtures compartilhadas dos testes."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.api.deps import get_db, get_email_sender, get_verification_email_sender
from app.main import fastapi_app
from app.repositories.user_repository import UserRepository


@pytest.fixture
def mongo_database():
    """Banco de dados MongoDB em memória (mongomock)."""
    client = AsyncMongoMockClient()
    return client["papodevweb_test"]


@pytest.fixture
def user_repository(mongo_database) -> UserRepository:
    return UserRepository(mongo_database)


@pytest.fixture
def sent_emails() -> list[tuple[str, str]]:
    """Coleta os e-mails "enviados" durante o teste (em vez de usar SMTP real)."""
    return []


@pytest.fixture
async def client(mongo_database, sent_emails) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP de teste com banco e envio de e-mail substituídos."""

    async def fake_email_sender(to_email: str, link: str) -> None:
        sent_emails.append((to_email, link))

    fastapi_app.dependency_overrides[get_db] = lambda: mongo_database
    fastapi_app.dependency_overrides[get_email_sender] = lambda: fake_email_sender
    fastapi_app.dependency_overrides[get_verification_email_sender] = lambda: fake_email_sender
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    fastapi_app.dependency_overrides.clear()


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
