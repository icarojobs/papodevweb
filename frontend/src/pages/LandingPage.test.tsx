import { beforeEach, describe, expect, it } from 'vitest'

import { LandingPage } from './LandingPage'
import { useAuthStore } from '@/store/auth.store'
import { renderWithProviders, screen } from '@/test/utils'

describe('LandingPage', () => {
  beforeEach(() => {
    useAuthStore.setState({ isAuthenticated: false, user: null })
  })

  it('exibe o pitch e CTAs para visitante não autenticado', () => {
    renderWithProviders(<LandingPage />)
    expect(screen.getByText('Toda a sua comunicação. Um só lugar.')).toBeInTheDocument()
    expect(screen.getByText(/WhatsApp, Slack, Telegram e Discord/)).toBeInTheDocument()
    expect(screen.getAllByText('Criar conta grátis').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Entrar').length).toBeGreaterThan(0)
  })

  it('mostra atalho para o chat quando autenticado', () => {
    useAuthStore.setState({ isAuthenticated: true })
    renderWithProviders(<LandingPage />)
    expect(screen.getAllByText('Abrir o chat').length).toBeGreaterThan(0)
  })
})
