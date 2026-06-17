import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { LoginPage } from './LoginPage'
import { authService } from '@/services/auth.service'
import { useAuthStore } from '@/store/auth.store'
import { renderWithProviders, screen, waitFor } from '@/test/utils'

const navigateMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => navigateMock }
})

vi.mock('@/services/auth.service', () => ({
  authService: { login: vi.fn() },
}))

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false })
  })

  it('exibe erro de validação para e-mail inválido', async () => {
    renderWithProviders(<LoginPage />)
    await userEvent.type(screen.getByLabelText('E-mail'), 'invalido')
    await userEvent.type(screen.getByLabelText('Senha'), '123')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Informe um e-mail válido.')).toBeInTheDocument()
    expect(authService.login).not.toHaveBeenCalled()
  })

  it('faz login e navega para a home', async () => {
    vi.mocked(authService.login).mockResolvedValue({
      access_token: 't',
      token_type: 'bearer',
      user: {
        id: '1',
        full_name: 'Maria',
        email: 'maria@example.com',
        created_at: '2026-01-01T00:00:00Z',
      },
    })

    renderWithProviders(<LoginPage />)
    await userEvent.type(screen.getByLabelText('E-mail'), 'maria@example.com')
    await userEvent.type(screen.getByLabelText('Senha'), 'senhaSegura123')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith('/'))
  })

  it('mostra toast de erro quando o login falha', async () => {
    vi.mocked(authService.login).mockRejectedValue(new Error('falhou'))

    renderWithProviders(<LoginPage />)
    await userEvent.type(screen.getByLabelText('E-mail'), 'maria@example.com')
    await userEvent.type(screen.getByLabelText('Senha'), 'senhaSegura123')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(
      await screen.findByText('Algo deu errado. Tente novamente.'),
    ).toBeInTheDocument()
    expect(navigateMock).not.toHaveBeenCalled()
  })
})
