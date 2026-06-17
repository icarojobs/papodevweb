import { create } from 'zustand'

import { authService } from '@/services/auth.service'
import { STORAGE_KEYS } from '@/lib/constants'
import type { LoginPayload, TokenResponse, UserPublic } from '@/types/auth'

interface AuthState {
  user: UserPublic | null
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<void>
  logout: () => Promise<void>
}

function persistSession(response: TokenResponse): UserPublic {
  localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token)
  return response.user
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  login: async (payload) => {
    const response = await authService.login(payload)
    set({ user: persistSession(response), isAuthenticated: true })
  },

  logout: async () => {
    await authService.logout()
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    set({ user: null, isAuthenticated: false })
  },
}))
