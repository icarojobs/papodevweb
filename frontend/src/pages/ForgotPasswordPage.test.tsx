import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ForgotPasswordPage } from './ForgotPasswordPage'
import { authService } from '@/services/auth.service'
import { renderWithProviders, screen } from '@/test/utils'

vi.mock('@/services/auth.service', () => ({
  authService: { forgotPassword: vi.fn() },
}))

describe('ForgotPasswordPage', () => {
  it('valida e-mail inválido', async () => {
    renderWithProviders(<ForgotPasswordPage />)
    await userEvent.type(screen.getByLabelText('E-mail'), 'invalido')
    await userEvent.click(screen.getByRole('button', { name: 'Enviar link' }))

    expect(await screen.findByText('Informe um e-mail válido.')).toBeInTheDocument()
    expect(authService.forgotPassword).not.toHaveBeenCalled()
  })

  it('exibe confirmação após enviar', async () => {
    vi.mocked(authService.forgotPassword).mockResolvedValue({ message: 'ok' })

    renderWithProviders(<ForgotPasswordPage />)
    await userEvent.type(screen.getByLabelText('E-mail'), 'maria@example.com')
    await userEvent.click(screen.getByRole('button', { name: 'Enviar link' }))

    expect(
      await screen.findByText(/enviamos um link de redefinição/i),
    ).toBeInTheDocument()
    expect(authService.forgotPassword).toHaveBeenCalledWith('maria@example.com')
  })

  it('mostra erro quando a requisição falha', async () => {
    vi.mocked(authService.forgotPassword).mockRejectedValue(new Error('falhou'))

    renderWithProviders(<ForgotPasswordPage />)
    await userEvent.type(screen.getByLabelText('E-mail'), 'maria@example.com')
    await userEvent.click(screen.getByRole('button', { name: 'Enviar link' }))

    expect(
      await screen.findByText('Algo deu errado. Tente novamente.'),
    ).toBeInTheDocument()
  })
})
