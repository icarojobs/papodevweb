import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { HomePage } from './HomePage'
import { useAuthStore } from '@/store/auth.store'
import { renderWithProviders, screen } from '@/test/utils'

vi.mock('@/services/auth.service', () => ({
  authService: { logout: vi.fn().mockResolvedValue(undefined) },
}))

describe('HomePage (WhatsApp shell)', () => {
  beforeEach(() => {
    useAuthStore.setState({
      isAuthenticated: true,
      user: {
        id: '1',
        full_name: 'Maria da Silva',
        email: 'maria@example.com',
        created_at: '2026-01-01T00:00:00Z',
      },
    })
  })

  it('renderiza o painel de conversas por padrão', () => {
    renderWithProviders(<HomePage />)
    expect(screen.getByText('WhatsApp')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Search or start a new chat')).toBeInTheDocument()
  })

  it('navega para Configurações e faz logout', async () => {
    const logoutSpy = vi.spyOn(useAuthStore.getState(), 'logout')
    renderWithProviders(<HomePage />)

    await userEvent.click(screen.getByLabelText('Configurações'))
    expect(screen.getByText('Profile')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Log out'))
    expect(logoutSpy).toHaveBeenCalled()
  })
})
