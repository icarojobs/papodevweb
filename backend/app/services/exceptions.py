"""Exceções de domínio — independentes do framework web."""


class DomainError(Exception):
    """Erro de regra de negócio."""


class EmailAlreadyRegisteredError(DomainError):
    """E-mail já existe na base."""


class InvalidCredentialsError(DomainError):
    """Credenciais de login inválidas."""


class EmailNotVerifiedError(DomainError):
    """Conta ainda não confirmada por e-mail."""


class InvalidTokenError(DomainError):
    """Token JWT inválido ou expirado."""
