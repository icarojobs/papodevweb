// Constantes centrais do frontend (evita magic strings/numbers — DRY).

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL ?? 'http://localhost:8000'

export const ROUTES = {
  HOME: '/',
  CHAT: '/chat',
  LOGIN: '/login',
  REGISTER: '/cadastro',
  FORGOT_PASSWORD: '/esqueci-senha',
  RESET_PASSWORD: '/redefinir-senha',
  VERIFY_EMAIL: '/confirmar-email',
  TERMS: '/termos',
} as const

// Dias de retenção do histórico (deve refletir RETENTION_DAYS do backend).
export const RETENTION_DAYS = 7

export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MIN_FULL_NAME_LENGTH: 2,
} as const

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'papodevweb.accessToken',
} as const

// Eventos Socket.IO (devem corresponder a app/core/constants.py::SocketEvent).
export const SOCKET_EVENTS = {
  CONVERSATION_OPEN: 'conversation:open',
  MESSAGE_SEND: 'message:send',
  MESSAGE_READ: 'message:read',
  MESSAGE_DELETE: 'message:delete',
  TYPING: 'typing',
  MESSAGE_NEW: 'message:new',
  MESSAGE_STATUS: 'message:status',
  MESSAGE_DELETED: 'message:deleted',
  CONVERSATION_UPDATED: 'conversation:updated',
  PRESENCE: 'presence',
} as const

export const MESSAGE_DELETED_TEXT = '🚫 Esta mensagem foi apagada'

// Limites de upload por categoria de mídia (devem refletir o backend).
export const MEDIA_LIMITS = {
  image: { bytes: 2 * 1024 * 1024, human: '2 MB', label: 'A imagem' },
  video: { bytes: 50 * 1024 * 1024, human: '50 MB', label: 'O vídeo' },
  document: { bytes: 2 * 1024 * 1024, human: '2 MB', label: 'O documento' },
  audio: { bytes: 16 * 1024 * 1024, human: '16 MB', label: 'O áudio' },
} as const

// Duração máxima de uma gravação de áudio (2 minutos).
export const AUDIO_MAX_SECONDS = 120

// Filtros da lista de conversas (rótulo em pt-br exibido na UI).
export const CHAT_FILTERS = [
  { key: 'all', label: 'Tudo' },
  { key: 'unread', label: 'Não lidas' },
  { key: 'favourites', label: 'Favoritas' },
  { key: 'groups', label: 'Grupos' },
] as const

export const TYPING_DEBOUNCE_MS = 1500
