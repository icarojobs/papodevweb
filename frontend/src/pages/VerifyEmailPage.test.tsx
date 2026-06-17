import { ChakraProvider } from '@chakra-ui/react'
import { render, screen } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { VerifyEmailPage } from './VerifyEmailPage'
import { authService } from '@/services/auth.service'
import { theme } from '@/theme'

vi.mock('@/services/auth.service', () => ({
  authService: { verifyEmail: vi.fn() },
}))

function renderAt(path: string, ui: ReactElement) {
  return render(
    <ChakraProvider theme={theme}>
      <MemoryRouter initialEntries={[path]}>{ui}</MemoryRouter>
    </ChakraProvider>,
  )
}

describe('VerifyEmailPage', () => {
  it('mostra erro quando não há token na URL', async () => {
    renderAt('/confirmar-email', <VerifyEmailPage />)
    expect(
      await screen.findByText(/link de confirmação inválido/i),
    ).toBeInTheDocument()
    expect(authService.verifyEmail).not.toHaveBeenCalled()
  })

  it('confirma o e-mail com sucesso', async () => {
    vi.mocked(authService.verifyEmail).mockResolvedValue({ message: 'ok' })

    renderAt('/confirmar-email?token=abc123', <VerifyEmailPage />)

    expect(await screen.findByText(/confirmado com sucesso/i)).toBeInTheDocument()
    expect(authService.verifyEmail).toHaveBeenCalledWith('abc123')
    expect(screen.getByRole('link', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('mostra erro quando o token é inválido', async () => {
    vi.mocked(authService.verifyEmail).mockRejectedValue(new Error('falhou'))

    renderAt('/confirmar-email?token=invalido', <VerifyEmailPage />)

    expect(
      await screen.findByText('Algo deu errado. Tente novamente.'),
    ).toBeInTheDocument()
  })
})
