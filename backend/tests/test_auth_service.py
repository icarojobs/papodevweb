"""Testes unitários do serviço de autenticação."""

import pytest

from app.core.constants import TokenType
from app.core.security import decode_token
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.services.exceptions import (
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidTokenError,
)


@pytest.fixture
def service(user_repository) -> AuthService:
    return AuthService(user_repository)


@pytest.fixture
def register_request() -> RegisterRequest:
    return RegisterRequest(
        full_name="João Souza",
        email="Joao@Example.com",
        password="senhaSegura123",
        confirm_password="senhaSegura123",
    )


async def _register_active(service: AuthService, request: RegisterRequest):
    """Cadastra e confirma o e-mail, deixando a conta ativa."""
    user = await service.register(request)
    await service.verify_email(service.issue_email_verification_token(user))
    return user


async def test_register_creates_inactive_user_with_normalized_email(service, register_request):
    user = await service.register(register_request)
    assert user.email == "joao@example.com"
    assert user.full_name == "João Souza"
    assert user.id
    assert user.is_active is False


async def test_register_duplicate_email_raises(service, register_request):
    await service.register(register_request)
    with pytest.raises(EmailAlreadyRegisteredError):
        await service.register(register_request)


async def test_authenticate_requires_verified_account(service, register_request):
    await service.register(register_request)
    with pytest.raises(EmailNotVerifiedError):
        await service.authenticate(
            LoginRequest(email="joao@example.com", password="senhaSegura123")
        )


async def test_authenticate_success_after_verification(service, register_request):
    await _register_active(service, register_request)
    user = await service.authenticate(
        LoginRequest(email="joao@example.com", password="senhaSegura123")
    )
    assert user.email == "joao@example.com"


async def test_verify_email_activates_account(service, register_request):
    user = await service.register(register_request)
    token = service.issue_email_verification_token(user)
    await service.verify_email(token)

    refreshed = await service.authenticate(
        LoginRequest(email="joao@example.com", password="senhaSegura123")
    )
    assert refreshed.is_active is True


async def test_verify_email_invalid_token_raises(service):
    with pytest.raises(InvalidTokenError):
        await service.verify_email("token-invalido")


async def test_verify_email_deleted_user_raises(service):
    from app.core.security import create_email_verification_token

    ghost_token = create_email_verification_token("64b7f9a2c1d2e3f4a5b6c7d8")
    with pytest.raises(InvalidTokenError):
        await service.verify_email(ghost_token)


async def test_issue_email_verification_token_is_valid(service, register_request):
    user = await service.register(register_request)
    token = service.issue_email_verification_token(user)
    assert decode_token(token, TokenType.VERIFY) == user.id


async def test_repository_activate_user_invalid_id_returns_false(user_repository):
    assert await user_repository.activate_user("id-invalido") is False


async def test_authenticate_wrong_password_raises(service, register_request):
    await service.register(register_request)
    with pytest.raises(InvalidCredentialsError):
        await service.authenticate(
            LoginRequest(email="joao@example.com", password="errada123")
        )


async def test_authenticate_unknown_email_raises(service):
    with pytest.raises(InvalidCredentialsError):
        await service.authenticate(
            LoginRequest(email="ninguem@example.com", password="qualquer123")
        )


async def test_refresh_token_flow(service, register_request):
    user = await service.register(register_request)
    token = service.issue_refresh_token(user)
    resolved = await service.user_from_refresh_token(token)
    assert resolved.id == user.id


async def test_refresh_with_invalid_token_raises(service):
    with pytest.raises(InvalidTokenError):
        await service.user_from_refresh_token("token-invalido")


async def test_refresh_with_access_token_raises(service, register_request):
    user = await service.register(register_request)
    access = service.issue_access_token(user)
    with pytest.raises(InvalidTokenError):
        await service.user_from_refresh_token(access)


async def test_refresh_for_deleted_user_raises(service):
    from app.core.security import create_refresh_token

    ghost_token = create_refresh_token("64b7f9a2c1d2e3f4a5b6c7d8")
    with pytest.raises(InvalidTokenError):
        await service.user_from_refresh_token(ghost_token)


async def test_issue_access_token_is_valid(service, register_request):
    user = await service.register(register_request)
    token = service.issue_access_token(user)
    assert decode_token(token, TokenType.ACCESS) == user.id


async def test_repository_get_by_id_with_invalid_id_returns_none(user_repository):
    assert await user_repository.get_by_id("id-invalido") is None


async def test_repository_update_password_invalid_id_returns_false(user_repository):
    assert await user_repository.update_password("id-invalido", "hash") is False


async def test_create_password_reset_token_for_existing_user(service, register_request):
    user = await service.register(register_request)
    token = await service.create_password_reset_token("joao@example.com")
    assert token is not None
    assert decode_token(token, TokenType.RESET) == user.id


async def test_create_password_reset_token_unknown_email_returns_none(service):
    assert await service.create_password_reset_token("ninguem@example.com") is None


async def test_reset_password_updates_hash(service, register_request):
    await _register_active(service, register_request)
    token = await service.create_password_reset_token("joao@example.com")
    assert token is not None

    await service.reset_password(token, "novaSenha123")

    user = await service.authenticate(
        LoginRequest(email="joao@example.com", password="novaSenha123")
    )
    assert user.email == "joao@example.com"


async def test_reset_password_invalid_token_raises(service):
    with pytest.raises(InvalidTokenError):
        await service.reset_password("token-invalido", "novaSenha123")


async def test_reset_password_deleted_user_raises(service):
    from app.core.security import create_password_reset_token

    ghost_token = create_password_reset_token("64b7f9a2c1d2e3f4a5b6c7d8")
    with pytest.raises(InvalidTokenError):
        await service.reset_password(ghost_token, "novaSenha123")
