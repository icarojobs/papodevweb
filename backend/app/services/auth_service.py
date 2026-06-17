"""Regras de negócio de autenticação (cadastro, login, refresh)."""

from app.core.constants import TokenType
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.exceptions import (
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidTokenError,
)


class AuthService:
    """Orquestra o fluxo de autenticação sobre o repositório de usuários."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def register(self, payload: RegisterRequest) -> User:
        """Cadastra um novo usuário inativo (pendente de confirmação por e-mail)."""
        email = payload.email.lower()
        if await self._users.exists_by_email(email):
            raise EmailAlreadyRegisteredError

        # Conta nasce inativa: só é ativada após confirmação do e-mail.
        return await self._users.create(
            full_name=payload.full_name.strip(),
            email=email,
            hashed_password=hash_password(payload.password),
            is_active=False,
        )

    async def authenticate(self, payload: LoginRequest) -> User:
        """Valida credenciais e retorna o usuário autenticado (e ativo)."""
        user = await self._users.get_by_email(payload.email.lower())
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsError
        if not user.is_active:
            raise EmailNotVerifiedError
        return user

    async def verify_email(self, token: str) -> None:
        """Valida o token de confirmação e ativa a conta."""
        subject = decode_token(token, TokenType.VERIFY)
        if subject is None:
            raise InvalidTokenError
        activated = await self._users.activate_user(subject)
        if not activated:
            raise InvalidTokenError

    async def user_from_refresh_token(self, token: str) -> User:
        """Resolve o usuário a partir de um refresh token válido."""
        subject = decode_token(token, TokenType.REFRESH)
        if subject is None:
            raise InvalidTokenError
        user = await self._users.get_by_id(subject)
        if user is None:
            raise InvalidTokenError
        return user

    async def create_password_reset_token(self, email: str) -> str | None:
        """Gera um token de redefinição para o e-mail, ou None se não existir.

        Retornar None silenciosamente evita enumeração de usuários.
        """
        user = await self._users.get_by_email(email.lower())
        if user is None:
            return None
        return create_password_reset_token(user.id)

    async def reset_password(self, token: str, new_password: str) -> None:
        """Valida o token de redefinição e atualiza a senha do usuário."""
        subject = decode_token(token, TokenType.RESET)
        if subject is None:
            raise InvalidTokenError
        updated = await self._users.update_password(subject, hash_password(new_password))
        if not updated:
            raise InvalidTokenError

    @staticmethod
    def issue_email_verification_token(user: User) -> str:
        return create_email_verification_token(user.id)

    @staticmethod
    def issue_access_token(user: User) -> str:
        return create_access_token(user.id)

    @staticmethod
    def issue_refresh_token(user: User) -> str:
        return create_refresh_token(user.id)
