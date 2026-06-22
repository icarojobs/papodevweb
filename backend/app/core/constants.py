"""Constantes centrais da aplicação.

Concentra "magic numbers" e "magic strings" em um único lugar para evitar
duplicidade e facilitar manutenção (DRY).
"""

from enum import StrEnum

# ----- Coleções do MongoDB -----
USERS_COLLECTION = "users"
CONVERSATIONS_COLLECTION = "conversations"
MESSAGES_COLLECTION = "messages"
SETTINGS_COLLECTION = "settings"

# Chave (singleton) do documento de configuração de e-mail de disparo (SMTP).
EMAIL_SETTINGS_KEY = "email"

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
ERR_ADMIN_REQUIRED = "Acesso restrito a administradores."
ERR_EMAIL_SETTINGS_NOT_CONFIGURED = (
    "Configure o e-mail de disparo (servidor SMTP) antes de enviar e-mails."
)
ERR_TEST_EMAIL_FAILED = "Falha ao enviar o e-mail de teste. Verifique as configurações de SMTP."

# ----- E-mail de disparo (configuração administrativa) -----
TEST_EMAIL_SUBJECT = "E-mail de teste — Papo Dev Web"
MSG_EMAIL_SETTINGS_SAVED = "Configurações de e-mail salvas com sucesso."
MSG_TEST_EMAIL_SENT = "E-mail de teste enviado com sucesso."

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


# ----- Chat: regras e limites -----
MIN_SEARCH_QUERY_LENGTH = 1
MAX_MESSAGE_LENGTH = 4096
MAX_GROUP_NAME_LENGTH = 100
MIN_GROUP_NAME_LENGTH = 1
DEFAULT_MESSAGE_PAGE_SIZE = 50
MAX_MESSAGE_PAGE_SIZE = 100
MAX_SEARCH_RESULTS = 20

# Limites de upload por categoria de mídia.
_MIB = 1024 * 1024
MAX_IMAGE_BYTES = 2 * _MIB
MAX_DOCUMENT_BYTES = 2 * _MIB
MAX_VIDEO_BYTES = 50 * _MIB
MAX_AUDIO_BYTES = 16 * _MIB
# Teto absoluto de upload (maior categoria) — usado como limite de borda.
MAX_MEDIA_BYTES = MAX_VIDEO_BYTES
PRESIGNED_URL_EXPIRES_SECONDS = 7 * 86_400
APPLICATION_OCTET_STREAM = "application/octet-stream"

# ----- Chat: mensagens de erro (pt-br) -----
ERR_CONVERSATION_NOT_FOUND = "Conversa não encontrada."
ERR_NOT_A_PARTICIPANT = "Você não participa desta conversa."
ERR_RECIPIENT_NOT_FOUND = "Destinatário não encontrado."
ERR_EMPTY_MESSAGE = "A mensagem não pode estar vazia."
ERR_MEDIA_TOO_LARGE = "Arquivo excede o tamanho máximo permitido para o seu tipo."
ERR_UNSUPPORTED_MEDIA = "Tipo de mídia não suportado."
ERR_GROUP_NEEDS_MEMBERS = "Um grupo precisa de pelo menos um participante."
ERR_CANNOT_LEAVE_DIRECT = "Conversas diretas não podem ser deixadas; exclua-as."
ERR_MESSAGE_NOT_FOUND = "Mensagem não encontrada."
ERR_NOT_MESSAGE_SENDER = "Só é possível apagar para todos as mensagens que você enviou."

# Texto exibido no lugar de uma mensagem apagada para todos (tombstone).
MSG_MESSAGE_DELETED = "🚫 Esta mensagem foi apagada"


class ConversationType(StrEnum):
    """Tipos de conversa suportados."""

    DIRECT = "direct"
    GROUP = "group"


class MessageType(StrEnum):
    """Tipos de conteúdo de uma mensagem."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"


class DeleteScope(StrEnum):
    """Escopo da exclusão de conversa."""

    ME = "me"
    EVERYONE = "everyone"


class MessageStatus(StrEnum):
    """Estado de entrega de uma mensagem, na ótica de quem enviou."""

    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class SocketEvent(StrEnum):
    """Nomes dos eventos Socket.IO (cliente <-> servidor)."""

    # cliente -> servidor
    CONVERSATION_OPEN = "conversation:open"
    MESSAGE_SEND = "message:send"
    MESSAGE_READ = "message:read"
    MESSAGE_DELETE = "message:delete"
    TYPING = "typing"
    # servidor -> cliente
    MESSAGE_NEW = "message:new"
    MESSAGE_STATUS = "message:status"
    MESSAGE_DELETED = "message:deleted"
    CONVERSATION_UPDATED = "conversation:updated"
    PRESENCE = "presence"


# Prefixos das salas (rooms) do Socket.IO.
ROOM_USER_PREFIX = "user:"
ROOM_CONVERSATION_PREFIX = "conv:"

# ----- Presença (Redis) -----
PRESENCE_ONLINE_SET = "presence:online"
PRESENCE_LAST_SEEN_HASH = "presence:last_seen"

# ----- Retenção de histórico (purge diário) -----
# Mantém globalmente apenas os últimos 7 dias de conversas/mensagens/mídias.
RETENTION_DAYS = 7
# Horário do job diário de expurgo (00:01).
RETENTION_CRON_HOUR = 0
RETENTION_CRON_MINUTE = 1
