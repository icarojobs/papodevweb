import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { RegisterPage } from './RegisterPage'
import { authService } from '@/services/auth.service'
import { renderWithProviders, screen } from '@/test/utils'

vi.mock('@/services/auth.service', () => ({
  authService: { register: vi.fn() },
}))

async function fillForm() {
  await userEvent.type(screen.getByLabelText('Nome completo'), 'Maria da Silva')
  await userEvent.type(screen.getByLabelText('E-mail'), 'maria@example.com')
  await userEvent.type(screen.getByLabelText('Senha'), 'senhaSegura123')
  await userEvent.type(screen.getByLabelText('Repetir senha'), 'senhaSegura123')
}

describe('RegisterPage', () => {
  it('valida divergência entre as senhas', async () => {
    renderWithProviders(<RegisterPage />)
    await userEvent.type(screen.getByLabelText('Nome completo'), 'Maria da Silva')
    await userEvent.type(screen.getByLabelText('E-mail'), 'maria@example.com')
    await userEvent.type(screen.getByLabelText('Senha'), 'senhaSegura123')
    await userEvent.type(screen.getByLabelText('Repetir senha'), 'diferente123')
    await userEvent.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByText('As senhas não conferem.')).toBeInTheDocument()
    expect(authService.register).not.toHaveBeenCalled()
  })

  it('exibe confirmação de e-mail após cadastrar', async () => {
    vi.mocked(authService.register).mockResolvedValue({ message: 'ok' })

    renderWithProviders(<RegisterPage />)
    await fillForm()
    await userEvent.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByText(/link de confirmação/i)).toBeInTheDocument()
    expect(authService.register).toHaveBeenCalled()
  })

  it('mostra toast de erro quando o cadastro falha', async () => {
    vi.mocked(authService.register).mockRejectedValue(new Error('falhou'))

    renderWithProviders(<RegisterPage />)
    await fillForm()
    await userEvent.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(
      await screen.findByText('Algo deu errado. Tente novamente.'),
    ).toBeInTheDocument()
  })
})
