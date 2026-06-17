import { ChakraProvider } from '@chakra-ui/react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { ResetPasswordPage } from './ResetPasswordPage'
import { authService } from '@/services/auth.service'
import { theme } from '@/theme'

const navigateMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => navigateMock }
})

vi.mock('@/services/auth.service', () => ({
  authService: { resetPassword: vi.fn() },
}))

function renderAt(path: string, ui: ReactElement) {
  return render(
    <ChakraProvider theme={theme}>
      <MemoryRouter initialEntries={[path]}>{ui}</MemoryRouter>
    </ChakraProvider>,
  )
}

describe('ResetPasswordPage', () => {
  it('mostra erro quando não há token na URL', () => {
    renderAt('/redefinir-senha', <ResetPasswordPage />)
    expect(screen.getByText(/link de redefinição inválido/i)).toBeInTheDocument()
  })

  it('redefine a senha e navega para o login', async () => {
    vi.mocked(authService.resetPassword).mockResolvedValue({ message: 'ok' })

    renderAt('/redefinir-senha?token=abc123', <ResetPasswordPage />)
    await userEvent.type(screen.getByLabelText('Nova senha'), 'novaSenha123')
    await userEvent.type(screen.getByLabelText('Repetir nova senha'), 'novaSenha123')
    await userEvent.click(screen.getByRole('button', { name: 'Redefinir senha' }))

    await waitFor(() =>
      expect(authService.resetPassword).toHaveBeenCalledWith({
        token: 'abc123',
        password: 'novaSenha123',
        confirm_password: 'novaSenha123',
      }),
    )
    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith('/login'))
  })

  it('mostra erro quando a redefinição falha', async () => {
    vi.mocked(authService.resetPassword).mockRejectedValue(new Error('falhou'))

    renderAt('/redefinir-senha?token=abc123', <ResetPasswordPage />)
    await userEvent.type(screen.getByLabelText('Nova senha'), 'novaSenha123')
    await userEvent.type(screen.getByLabelText('Repetir nova senha'), 'novaSenha123')
    await userEvent.click(screen.getByRole('button', { name: 'Redefinir senha' }))

    expect(
      await screen.findByText('Algo deu errado. Tente novamente.'),
    ).toBeInTheDocument()
    expect(navigateMock).not.toHaveBeenCalled()
  })
})
