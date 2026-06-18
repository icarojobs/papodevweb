import { describe, expect, it, vi } from 'vitest'

import { api } from '@/lib/api'
import { authService } from './auth.service'

vi.mock('@/lib/api', () => ({
  api: { post: vi.fn(), get: vi.fn() },
}))

const messageResponse = { message: 'ok' }

const tokenResponse = {
  access_token: 't',
  token_type: 'bearer',
  user: {
    id: '1',
    full_name: 'Maria',
    email: 'maria@example.com',
    created_at: '2026-01-01T00:00:00Z',
  },
}

describe('authService', () => {
  it('register chama POST /auth/register', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: messageResponse })
    const result = await authService.register({
      full_name: 'Maria',
      email: 'maria@example.com',
      password: 'senhaSegura123',
      confirm_password: 'senhaSegura123',
    })
    expect(api.post).toHaveBeenCalledWith('/auth/register', expect.any(Object))
    expect(result).toEqual(messageResponse)
  })

  it('verifyEmail chama POST /auth/verify-email', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: messageResponse })
    const result = await authService.verifyEmail('tok-123')
    expect(api.post).toHaveBeenCalledWith('/auth/verify-email', { token: 'tok-123' })
    expect(result).toEqual(messageResponse)
  })

  it('login chama POST /auth/login', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: tokenResponse })
    const result = await authService.login({ email: 'maria@example.com', password: 'x' })
    expect(api.post).toHaveBeenCalledWith('/auth/login', expect.any(Object))
    expect(result).toEqual(tokenResponse)
  })

  it('refresh chama POST /auth/refresh', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: tokenResponse })
    const result = await authService.refresh()
    expect(api.post).toHaveBeenCalledWith('/auth/refresh')
    expect(result).toEqual(tokenResponse)
  })

  it('me chama GET /auth/me', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: tokenResponse.user })
    const result = await authService.me()
    expect(api.get).toHaveBeenCalledWith('/auth/me')
    expect(result).toEqual(tokenResponse.user)
  })

  it('logout chama POST /auth/logout', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: null })
    await authService.logout()
    expect(api.post).toHaveBeenCalledWith('/auth/logout')
  })

  it('forgotPassword chama POST /auth/forgot-password', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: messageResponse })
    const result = await authService.forgotPassword('maria@example.com')
    expect(api.post).toHaveBeenCalledWith('/auth/forgot-password', {
      email: 'maria@example.com',
    })
    expect(result).toEqual(messageResponse)
  })

  it('resetPassword chama POST /auth/reset-password', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: messageResponse })
    const payload = {
      token: 'abc',
      password: 'novaSenha123',
      confirm_password: 'novaSenha123',
    }
    const result = await authService.resetPassword(payload)
    expect(api.post).toHaveBeenCalledWith('/auth/reset-password', payload)
    expect(result).toEqual(messageResponse)
  })
})
