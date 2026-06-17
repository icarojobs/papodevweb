"""Constantes centrais da aplicação.

Concentra "magic numbers" e "magic strings" em um único lugar para evitar
duplicidade e facilitar manutenção (DRY).
"""

from enum import StrEnum

# ----- Coleções do MongoDB -----
USERS_COLLECTION = "users"

# ----- Autenticação / JWT -----
JWT_ALGORITHM = "HS256"
REFRESH_TOKEN_COOKIE_NAME = "papodevweb_refresh_token"
BEARER_SCHEME = "Bearer"

# ----- Regras de validação -----
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
MIN_FULL_NAME_LENGTH = 2
MAX_FULL_NAME_LENGTH = 120

# ----- Seed (usuário padrão para desenvolvimento/testes) -----
DEFAULT_USER_FULL_NAME = "Usuário Teste"
DEFAULT_USER_EMAIL = "teste@teste.com.br"
DEFAULT_USER_PASSWORD = "teste1234"  # noqa: S105 — apenas ambiente de desenvolvimento

# ----- Confirmação de e-mail (ativação de conta) -----
EMAIL_VERIFICATION_PATH = "/confirmar-email"
EMAIL_VERIFICATION_SUBJECT = "Confirme seu e-mail — Papo Dev Web"

# ----- Redefinição de senha -----
PASSWORD_RESET_PATH = "/redefinir-senha"
PASSWORD_RESET_EMAIL_SUBJECT = "Redefinição de senha — Papo Dev Web"

# ----- Mensagens de erro (pt-br) -----
ERR_EMAIL_ALREADY_REGISTERED = "E-mail já cadastrado."
ERR_INVALID_CREDENTIALS = "E-mail ou senha inválidos."
ERR_PASSWORDS_DO_NOT_MATCH = "As senhas não conferem."
ERR_INVALID_TOKEN = "Token inválido ou expirado."
ERR_USER_NOT_FOUND = "Usuário não encontrado."
ERR_EMAIL_NOT_VERIFIED = "Confirme seu e-mail antes de entrar. Verifique sua caixa de entrada."

# ----- Mensagens de sucesso (pt-br) -----
# Mensagem genérica: não revela se o e-mail existe (evita enumeração de usuários).
MSG_PASSWORD_RESET_SENT = "Se o e-mail estiver cadastrado, enviaremos um link de redefinição."
MSG_PASSWORD_RESET_SUCCESS = "Senha redefinida com sucesso."
MSG_REGISTER_CONFIRMATION_SENT = (
    "Cadastro realizado! Enviamos um link de confirmação para o seu e-mail. "
    "Confirme em até 24 horas para ativar a sua conta."
)
MSG_EMAIL_VERIFIED = "E-mail confirmado com sucesso. Você já pode entrar."


class TokenType(StrEnum):
    """Tipos de token JWT emitidos pela aplicação."""

    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFY = "verify"
