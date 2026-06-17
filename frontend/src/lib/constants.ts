// Constantes centrais do frontend (evita magic strings/numbers — DRY).

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
export const SOCKET_URL = import.meta.env.VITE_SOCKET_URL ?? 'http://localhost:8000'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/cadastro',
  FORGOT_PASSWORD: '/esqueci-senha',
  RESET_PASSWORD: '/redefinir-senha',
  VERIFY_EMAIL: '/confirmar-email',
} as const

export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MIN_FULL_NAME_LENGTH: 2,
} as const

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'papodevweb.accessToken',
} as const
