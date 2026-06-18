import { beforeEach, describe, expect, it, vi } from 'vitest'

import { emitDeleteMessage, emitOpen, emitRead, emitSend, emitTyping } from '@/lib/chatSocket'
import { chatService } from '@/services/chat.service'
import type { Conversation, Message } from '@/types/chat'
import {
  applyDeletion,
  filterConversations,
  messageTypeFromMime,
  stripConversation,
  useChatStore,
} from './chat.store'

vi.mock('@/lib/chatSocket', () => ({
  connectChatSocket: vi.fn(),
  bindChatHandlers: vi.fn(() => vi.fn()),
  emitOpen: vi.fn(),
  emitRead: vi.fn(),
  emitSend: vi.fn(() => Promise.resolve({ ok: true })),
  emitTyping: vi.fn(),
  emitDeleteMessage: vi.fn(),
}))
vi.mock('@/lib/socket', () => ({ disconnectSocket: vi.fn() }))
vi.mock('@/services/chat.service', () => ({
  chatService: {
    listConversations: vi.fn(),
    getMessages: vi.fn(),
    createConversation: vi.fn(),
    toggleFavourite: vi.fn(),
    searchUsers: vi.fn(),
    leaveGroup: vi.fn().mockResolvedValue(undefined),
    deleteConversation: vi.fn().mockResolvedValue(undefined),
  },
}))

function conv(over: Partial<Conversation> = {}): Conversation {
  return {
    id: 'c1',
    type: 'direct',
    name: 'Bob',
    participants: [
      { id: 'u1', full_name: 'Eu', email: 'eu@x', online: false, last_seen: null },
      { id: 'u2', full_name: 'Bob', email: 'bob@x', online: false, last_seen: null },
    ],
    last_message: null,
    unread: 0,
    favourite: false,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...over,
  }
}

function msg(over: Partial<Message> = {}): Message {
  return {
    id: 'm1',
    conversation_id: 'c1',
    sender_id: 'u2',
    type: 'text',
    text: 'oi',
    media: null,
    created_at: '2026-01-01T00:00:01Z',
    status: 'sent',
    read_by: ['u2'],
    delivered_to: ['u2'],
    ...over,
  }
}

const store = () => useChatStore.getState()

beforeEach(() => {
  vi.clearAllMocks()
  useChatStore.setState({
    conversations: [],
    messagesByConversation: {},
    activeConversationId: null,
    filter: 'all',
    search: '',
    userResults: [],
    typingByConversation: {},
    unbind: null,
  })
})

describe('helpers puros', () => {
  it('filterConversations aplica abas e busca', () => {
    const list = [
      conv({ id: 'a', name: 'Ana', unread: 0, favourite: false, type: 'direct' }),
      conv({ id: 'b', name: 'Bruno', unread: 3, favourite: true, type: 'group' }),
    ]
    expect(filterConversations(list, 'all', '').length).toBe(2)
    expect(filterConversations(list, 'unread', '').map((c) => c.id)).toEqual(['b'])
    expect(filterConversations(list, 'favourites', '').map((c) => c.id)).toEqual(['b'])
    expect(filterConversations(list, 'groups', '').map((c) => c.id)).toEqual(['b'])
    expect(filterConversations(list, 'all', 'ana').map((c) => c.id)).toEqual(['a'])
  })

  it('messageTypeFromMime deriva o tipo', () => {
    expect(messageTypeFromMime('image/png')).toBe('image')
    expect(messageTypeFromMime('video/mp4')).toBe('video')
    expect(messageTypeFromMime('audio/webm')).toBe('audio')
    expect(messageTypeFromMime('application/pdf')).toBe('document')
  })

  it('applyDeletion remove (me) ou vira tombstone (everyone)', () => {
    const list = [msg({ id: 'm1', text: 'oi', media: { key: 'k' } as never })]
    expect(applyDeletion(list, 'm1', 'me')).toEqual([])
    const tomb = applyDeletion(list, 'm1', 'everyone')
    expect(tomb[0]).toMatchObject({ id: 'm1', deleted: true, text: '', media: null })
  })
})

describe('ações do store', () => {
  it('loadConversations ordena por mais recente', async () => {
    vi.mocked(chatService.listConversations).mockResolvedValue([
      conv({ id: 'a', updated_at: '2026-01-01T00:00:00Z' }),
      conv({ id: 'b', updated_at: '2026-02-01T00:00:00Z' }),
    ])
    await store().loadConversations()
    expect(store().conversations.map((c) => c.id)).toEqual(['b', 'a'])
  })

  it('selectConversation marca ativa, zera não-lidas, abre e carrega', async () => {
    useChatStore.setState({ conversations: [conv({ unread: 5 })] })
    vi.mocked(chatService.getMessages).mockResolvedValue([msg()])
    await store().selectConversation('c1')
    expect(store().activeConversationId).toBe('c1')
    expect(store().conversations[0].unread).toBe(0)
    expect(emitOpen).toHaveBeenCalledWith('c1')
    expect(store().messagesByConversation.c1).toHaveLength(1)
  })

  it('selectConversation não recarrega mensagens já em cache', async () => {
    useChatStore.setState({ messagesByConversation: { c1: [msg()] } })
    await store().selectConversation('c1')
    expect(chatService.getMessages).not.toHaveBeenCalled()
  })

  it('sendMessage emite com o tipo derivado da mídia', async () => {
    useChatStore.setState({ activeConversationId: 'c1' })
    await store().sendMessage('', { key: 'k', url: 'u', mime: 'image/png', size: 1, name: 'a.png' })
    expect(emitSend).toHaveBeenCalledWith(
      expect.objectContaining({ conversation_id: 'c1', type: 'image' }),
    )
  })

  it('sendMessage ignora vazio sem mídia e sem conversa ativa', async () => {
    await store().sendMessage('oi')
    useChatStore.setState({ activeConversationId: 'c1' })
    await store().sendMessage('   ')
    expect(emitSend).not.toHaveBeenCalled()
  })

  it('deleteMessage emite e atualiza o estado local (me/everyone)', () => {
    useChatStore.setState({ messagesByConversation: { c1: [msg({ id: 'm1' })] } })
    store().deleteMessage('c1', 'm1', 'me')
    expect(emitDeleteMessage).toHaveBeenCalledWith('c1', 'm1', 'me')
    expect(store().messagesByConversation.c1).toEqual([])

    useChatStore.setState({ messagesByConversation: { c1: [msg({ id: 'm2', text: 'oi' })] } })
    store().deleteMessage('c1', 'm2', 'everyone')
    expect(store().messagesByConversation.c1[0]).toMatchObject({ deleted: true, text: '' })
  })

  it('deleteMessage ignora conversa sem mensagens carregadas', () => {
    store().deleteMessage('desconhecida', 'm1', 'me')
    expect(emitDeleteMessage).toHaveBeenCalled()
    expect(store().messagesByConversation.desconhecida).toBeUndefined()
  })

  it('sendTyping emite para a conversa ativa', () => {
    useChatStore.setState({ activeConversationId: 'c1' })
    store().sendTyping(true)
    expect(emitTyping).toHaveBeenCalledWith('c1', true)
  })

  it('toggleFavourite atualiza o estado local', async () => {
    useChatStore.setState({ conversations: [conv({ favourite: false })] })
    vi.mocked(chatService.toggleFavourite).mockResolvedValue({ favourite: true })
    await store().toggleFavourite('c1')
    expect(store().conversations[0].favourite).toBe(true)
  })

  it('startConversation cria, insere e seleciona', async () => {
    vi.mocked(chatService.createConversation).mockResolvedValue(conv({ id: 'c1' }))
    vi.mocked(chatService.getMessages).mockResolvedValue([])
    const created = await store().startConversation('u2')
    expect(created.id).toBe('c1')
    expect(store().conversations.map((c) => c.id)).toContain('c1')
    expect(store().activeConversationId).toBe('c1')
  })

  it('leaveGroup remove a conversa do estado', async () => {
    useChatStore.setState({
      conversations: [conv()],
      messagesByConversation: { c1: [msg()] },
      activeConversationId: 'c1',
    })
    await store().leaveGroup('c1')
    expect(chatService.leaveGroup).toHaveBeenCalledWith('c1')
    expect(store().conversations).toEqual([])
    expect(store().messagesByConversation.c1).toBeUndefined()
    expect(store().activeConversationId).toBeNull()
  })

  it('deleteConversation chama o serviço e remove do estado', async () => {
    useChatStore.setState({ conversations: [conv()], activeConversationId: 'c1' })
    await store().deleteConversation('c1', 'everyone', true)
    expect(chatService.deleteConversation).toHaveBeenCalledWith('c1', {
      scope: 'everyone',
      deleteMedia: true,
    })
    expect(store().conversations).toEqual([])
  })

  it('deleteConversation remove localmente mesmo se a API falhar', async () => {
    useChatStore.setState({ conversations: [conv()], activeConversationId: 'c1' })
    vi.mocked(chatService.deleteConversation).mockRejectedValueOnce(new Error('404'))
    await expect(store().deleteConversation('c1', 'me', false)).rejects.toThrow()
    expect(store().conversations).toEqual([])
    expect(store().activeConversationId).toBeNull()
  })

  it('leaveGroup remove localmente mesmo se a API falhar', async () => {
    useChatStore.setState({ conversations: [conv()], activeConversationId: 'c1' })
    vi.mocked(chatService.leaveGroup).mockRejectedValueOnce(new Error('boom'))
    await expect(store().leaveGroup('c1')).rejects.toThrow()
    expect(store().conversations).toEqual([])
  })

  it('stripConversation preserva outras conversas e seleção', () => {
    const state = {
      conversations: [conv({ id: 'c1' }), conv({ id: 'c2' })],
      messagesByConversation: { c1: [msg()], c2: [msg()] },
      typingByConversation: { c1: ['u2'] },
      activeConversationId: 'c2',
    } as never
    const next = stripConversation(state, 'c1')
    expect(next.conversations.map((c) => c.id)).toEqual(['c2'])
    expect(next.messagesByConversation.c1).toBeUndefined()
    expect(next.activeConversationId).toBe('c2')
  })

  it('startGroup cria um grupo', async () => {
    vi.mocked(chatService.createConversation).mockResolvedValue(conv({ id: 'g1', type: 'group' }))
    vi.mocked(chatService.getMessages).mockResolvedValue([])
    await store().startGroup('Equipe', ['u2', 'u3'])
    expect(chatService.createConversation).toHaveBeenCalledWith({
      type: 'group',
      name: 'Equipe',
      member_ids: ['u2', 'u3'],
    })
  })

  it('setFilter e setSearch atualizam o estado', () => {
    store().setFilter('groups')
    store().setSearch('ana')
    expect(store().filter).toBe('groups')
    expect(store().search).toBe('ana')
  })

  it('setSearch vazio limpa os resultados de usuários', () => {
    useChatStore.setState({ userResults: [{ id: 'u9' } as never] })
    store().setSearch('   ')
    expect(store().userResults).toEqual([])
  })

  it('searchUsers busca usuários e limpa quando vazio', async () => {
    vi.mocked(chatService.searchUsers).mockResolvedValue([
      { id: 'u2', full_name: 'Fulano', email: 'fulano@x', online: false, last_seen: null },
    ])
    await store().searchUsers('fulano')
    expect(store().userResults).toHaveLength(1)
    await store().searchUsers('   ')
    expect(store().userResults).toEqual([])
  })

  it('initialize conecta, vincula e carrega; teardown limpa', async () => {
    vi.mocked(chatService.listConversations).mockResolvedValue([])
    await store().initialize()
    expect(store().unbind).toBeTypeOf('function')
    store().teardown()
    expect(store().conversations).toEqual([])
    expect(store().unbind).toBeNull()
  })
})

describe('appliers de eventos', () => {
  it('receiveMessage adiciona, deduplica e marca lida quando ativa', () => {
    useChatStore.setState({ activeConversationId: 'c1' })
    store().receiveMessage({ conversation_id: 'c1', message: msg() })
    store().receiveMessage({ conversation_id: 'c1', message: msg() })
    expect(store().messagesByConversation.c1).toHaveLength(1)
    expect(emitRead).toHaveBeenCalledWith('c1')
  })

  it('receiveMessage não marca lida se a conversa não está ativa', () => {
    store().receiveMessage({ conversation_id: 'c1', message: msg() })
    expect(emitRead).not.toHaveBeenCalled()
  })

  it('applyStatus atualiza status e read_by', () => {
    useChatStore.setState({
      messagesByConversation: { c1: [msg({ id: 'm1', status: 'sent', read_by: ['u1'] })] },
    })
    store().applyStatus({
      conversation_id: 'c1',
      message_ids: ['m1'],
      status: 'read',
      user_id: 'u2',
    })
    const updated = store().messagesByConversation.c1[0]
    expect(updated.status).toBe('read')
    expect(updated.read_by).toContain('u2')
    expect(updated.delivered_to).toContain('u2')
  })

  it('applyStatus ignora conversa desconhecida', () => {
    store().applyStatus({ conversation_id: 'x', message_ids: ['m1'], status: 'read', user_id: 'u2' })
    expect(store().messagesByConversation.x).toBeUndefined()
  })

  it('applyPresence atualiza o participante', () => {
    useChatStore.setState({ conversations: [conv()] })
    store().applyPresence({ user_id: 'u2', online: true, last_seen: null })
    const bob = store().conversations[0].participants.find((p) => p.id === 'u2')
    expect(bob?.online).toBe(true)
  })

  it('applyTyping adiciona e remove o usuário', () => {
    store().applyTyping({ conversation_id: 'c1', user_id: 'u2', typing: true })
    expect(store().typingByConversation.c1).toEqual(['u2'])
    store().applyTyping({ conversation_id: 'c1', user_id: 'u2', typing: false })
    expect(store().typingByConversation.c1).toEqual([])
  })

  it('applyConversationUpdated faz upsert e zera não-lidas da ativa', () => {
    useChatStore.setState({ activeConversationId: 'c1', conversations: [conv()] })
    store().applyConversationUpdated({ conversation: conv({ unread: 9 }) })
    expect(store().conversations).toHaveLength(1)
    expect(store().conversations[0].unread).toBe(0)
  })

  it('applyMessageDeleted aplica o tombstone recebido por evento', () => {
    useChatStore.setState({ messagesByConversation: { c1: [msg({ id: 'm1', text: 'oi' })] } })
    store().applyMessageDeleted({ conversation_id: 'c1', message_id: 'm1', scope: 'everyone' })
    expect(store().messagesByConversation.c1[0]).toMatchObject({ deleted: true })
  })

  it('applyMessageDeleted ignora conversa desconhecida', () => {
    store().applyMessageDeleted({ conversation_id: 'x', message_id: 'm1', scope: 'me' })
    expect(store().messagesByConversation.x).toBeUndefined()
  })
})
