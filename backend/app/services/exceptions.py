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


class ConversationNotFoundError(DomainError):
    """Conversa inexistente."""


class NotAParticipantError(DomainError):
    """Usuário não participa da conversa."""


class RecipientNotFoundError(DomainError):
    """Destinatário (usuário) inexistente."""


class EmptyMessageError(DomainError):
    """Mensagem sem conteúdo (texto vazio e sem mídia)."""


class GroupNeedsMembersError(DomainError):
    """Tentativa de criar grupo sem participantes válidos."""


class MediaTooLargeError(DomainError):
    """Arquivo de mídia excede o tamanho máximo permitido."""


class UnsupportedMediaError(DomainError):
    """Tipo de mídia não suportado."""


class CannotLeaveDirectError(DomainError):
    """Conversas diretas não podem ser 'deixadas' (apenas excluídas)."""


class MessageNotFoundError(DomainError):
    """Mensagem inexistente (ou de outra conversa)."""


class CannotDeleteForEveryoneError(DomainError):
    """Apenas o autor pode apagar a mensagem para todos."""
