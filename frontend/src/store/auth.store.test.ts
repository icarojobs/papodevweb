import { beforeEach, describe, expect, it, vi } from 'vitest'

import { authService } from '@/services/auth.service'
import { STORAGE_KEYS } from '@/lib/constants'
import { useAuthStore } from './auth.store'
import type { TokenResponse } from '@/types/auth'

vi.mock('@/services/auth.service', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
  },
}))

const tokenResponse: TokenResponse = {
  access_token: 'token-123',
  token_type: 'bearer',
  user: {
    id: '1',
    full_name: 'Maria da Silva',
    email: 'maria@example.com',
    created_at: '2026-01-01T00:00:00Z',
  },
}

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false })
  })

  it('faz login e persiste o token', async () => {
    vi.mocked(authService.login).mockResolvedValue(tokenResponse)

    await useAuthStore.getState().login({ email: 'maria@example.com', password: 'x' })

    expect(useAuthStore.getState().isAuthenticated).toBe(true)
    expect(useAuthStore.getState().user?.email).toBe('maria@example.com')
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBe('token-123')
  })

  it('faz logout e limpa o token', async () => {
    vi.mocked(authService.logout).mockResolvedValue()
    useAuthStore.setState({ user: tokenResponse.user, isAuthenticated: true })
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'token-123')

    await useAuthStore.getState().logout()

    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBeNull()
  })

  it('bootstrap restaura a sessão via refresh', async () => {
    vi.mocked(authService.refresh).mockResolvedValue(tokenResponse)
    useAuthStore.setState({ initializing: true })

    await useAuthStore.getState().bootstrap()

    expect(useAuthStore.getState().isAuthenticated).toBe(true)
    expect(useAuthStore.getState().user?.email).toBe('maria@example.com')
    expect(useAuthStore.getState().initializing).toBe(false)
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBe('token-123')
  })

  it('bootstrap sem sessão válida deixa deslogado', async () => {
    vi.mocked(authService.refresh).mockRejectedValue(new Error('401'))
    useAuthStore.setState({ initializing: true, isAuthenticated: true })
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'velho')

    await useAuthStore.getState().bootstrap()

    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().initializing).toBe(false)
    expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBeNull()
  })
})
