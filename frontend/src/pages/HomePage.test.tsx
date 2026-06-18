import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { HomePage } from './HomePage'
import { useAuthStore } from '@/store/auth.store'
import { useChatStore } from '@/store/chat.store'
import { renderWithProviders, screen } from '@/test/utils'

vi.mock('@/services/auth.service', () => ({
  authService: { logout: vi.fn().mockResolvedValue(undefined) },
}))

// Evita conexão real de socket e chamadas HTTP ao inicializar o chat.
vi.mock('@/lib/chatSocket', () => ({
  connectChatSocket: vi.fn(),
  bindChatHandlers: vi.fn(() => vi.fn()),
  emitOpen: vi.fn(),
  emitRead: vi.fn(),
  emitSend: vi.fn(),
  emitTyping: vi.fn(),
}))

vi.mock('@/services/chat.service', () => ({
  chatService: {
    listConversations: vi.fn().mockResolvedValue([]),
    getMessages: vi.fn().mockResolvedValue([]),
    searchUsers: vi.fn().mockResolvedValue([]),
    createConversation: vi.fn(),
    toggleFavourite: vi.fn(),
  },
}))

describe('HomePage (shell do WhatsApp)', () => {
  beforeEach(() => {
    useChatStore.setState({
      conversations: [],
      messagesByConversation: {},
      activeConversationId: null,
      typingByConversation: {},
    })
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
    expect(screen.getByText('Papo Dev Web')).toBeInTheDocument()
    expect(screen.getByLabelText('Buscar conversas')).toBeInTheDocument()
  })

  it('navega para Configurações e faz logout', async () => {
    const logoutSpy = vi.spyOn(useAuthStore.getState(), 'logout')
    renderWithProviders(<HomePage />)

    await userEvent.click(screen.getByLabelText('Configurações'))
    expect(screen.getByText('Profile')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Sair'))
    expect(logoutSpy).toHaveBeenCalled()
  })
})
