import { api } from '@/lib/api'
import type {
  LoginPayload,
  MessageResponse,
  RegisterPayload,
  ResetPasswordPayload,
  TokenResponse,
  UserPublic,
} from '@/types/auth'

// Camada de acesso à API de autenticação (isola os endpoints HTTP).
export const authService = {
  async register(payload: RegisterPayload): Promise<MessageResponse> {
    const { data } = await api.post<MessageResponse>('/auth/register', payload)
    return data
  },

  async verifyEmail(token: string): Promise<MessageResponse> {
    const { data } = await api.post<MessageResponse>('/auth/verify-email', { token })
    return data
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/login', payload)
    return data
  },

  async me(): Promise<UserPublic> {
    const { data } = await api.get<UserPublic>('/auth/me')
    return data
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  async forgotPassword(email: string): Promise<MessageResponse> {
    const { data } = await api.post<MessageResponse>('/auth/forgot-password', { email })
    return data
  },

  async resetPassword(payload: ResetPasswordPayload): Promise<MessageResponse> {
    const { data } = await api.post<MessageResponse>('/auth/reset-password', payload)
    return data
  },
}
