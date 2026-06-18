import { beforeEach, describe, expect, it, vi } from 'vitest'

import { SOCKET_EVENTS, STORAGE_KEYS } from './constants'
import {
  bindChatHandlers,
  connectChatSocket,
  emitDeleteMessage,
  emitOpen,
  emitRead,
  emitSend,
  emitTyping,
} from './chatSocket'

const fakeSocket = vi.hoisted(() => ({
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn(),
  connect: vi.fn(),
  connected: false,
  auth: {} as Record<string, unknown>,
}))

vi.mock('./socket', () => ({ getSocket: () => fakeSocket }))

const handlers = {
  onNewMessage: vi.fn(),
  onMessageStatus: vi.fn(),
  onPresence: vi.fn(),
  onTyping: vi.fn(),
  onConversationUpdated: vi.fn(),
  onMessageDeleted: vi.fn(),
}

describe('chatSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fakeSocket.connected = false
  })

  it('connectChatSocket autentica com o token e conecta', () => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'abc')
    connectChatSocket()
    expect(fakeSocket.auth).toEqual({ token: 'abc' })
    expect(fakeSocket.connect).toHaveBeenCalled()
  })

  it('connectChatSocket não reconecta se já conectado', () => {
    fakeSocket.connected = true
    connectChatSocket()
    expect(fakeSocket.connect).not.toHaveBeenCalled()
  })

  it('bindChatHandlers registra e remove os ouvintes', () => {
    const unbind = bindChatHandlers(handlers)
    expect(fakeSocket.on).toHaveBeenCalledTimes(6)
    unbind()
    expect(fakeSocket.off).toHaveBeenCalledTimes(6)
  })

  it('emitSend resolve com o ack do servidor', async () => {
    fakeSocket.emit.mockImplementationOnce((_event, _payload, cb) => cb({ ok: true }))
    const ack = await emitSend({ conversation_id: 'c1', type: 'text', text: 'oi' })
    expect(ack).toEqual({ ok: true })
    expect(fakeSocket.emit).toHaveBeenCalledWith(
      SOCKET_EVENTS.MESSAGE_SEND,
      expect.objectContaining({ conversation_id: 'c1' }),
      expect.any(Function),
    )
  })

  it('emitDeleteMessage emite o evento de exclusão', () => {
    emitDeleteMessage('c1', 'm1', 'everyone')
    expect(fakeSocket.emit).toHaveBeenCalledWith(SOCKET_EVENTS.MESSAGE_DELETE, {
      conversation_id: 'c1',
      message_id: 'm1',
      scope: 'everyone',
    })
  })

  it('emitOpen, emitRead e emitTyping emitem os eventos corretos', () => {
    emitOpen('c1')
    emitRead('c1')
    emitTyping('c1', true)
    expect(fakeSocket.emit).toHaveBeenCalledWith(SOCKET_EVENTS.CONVERSATION_OPEN, {
      conversation_id: 'c1',
    })
    expect(fakeSocket.emit).toHaveBeenCalledWith(SOCKET_EVENTS.MESSAGE_READ, {
      conversation_id: 'c1',
    })
    expect(fakeSocket.emit).toHaveBeenCalledWith(SOCKET_EVENTS.TYPING, {
      conversation_id: 'c1',
      typing: true,
    })
  })
})
