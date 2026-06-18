import type { Socket } from 'socket.io-client'

import type {
  ConversationUpdatedEvent,
  DeleteScope,
  MessageDeletedEvent,
  MessageStatusEvent,
  NewMessageEvent,
  PresenceEvent,
  SendAck,
  SendMessagePayload,
  TypingEvent,
} from '@/types/chat'
import { SOCKET_EVENTS, STORAGE_KEYS } from './constants'
import { getSocket } from './socket'

export interface ChatSocketHandlers {
  onNewMessage: (event: NewMessageEvent) => void
  onMessageStatus: (event: MessageStatusEvent) => void
  onPresence: (event: PresenceEvent) => void
  onTyping: (event: TypingEvent) => void
  onConversationUpdated: (event: ConversationUpdatedEvent) => void
  onMessageDeleted: (event: MessageDeletedEvent) => void
}

// Conecta o socket autenticado pelo access token atual.
export function connectChatSocket(): Socket {
  const socket = getSocket()
  socket.auth = { token: localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) ?? '' }
  if (!socket.connected) {
    socket.connect()
  }
  return socket
}

// Registra os ouvintes dos eventos do servidor; retorna função de limpeza.
export function bindChatHandlers(handlers: ChatSocketHandlers): () => void {
  const socket = getSocket()
  socket.on(SOCKET_EVENTS.MESSAGE_NEW, handlers.onNewMessage)
  socket.on(SOCKET_EVENTS.MESSAGE_STATUS, handlers.onMessageStatus)
  socket.on(SOCKET_EVENTS.PRESENCE, handlers.onPresence)
  socket.on(SOCKET_EVENTS.TYPING, handlers.onTyping)
  socket.on(SOCKET_EVENTS.CONVERSATION_UPDATED, handlers.onConversationUpdated)
  socket.on(SOCKET_EVENTS.MESSAGE_DELETED, handlers.onMessageDeleted)
  return () => {
    socket.off(SOCKET_EVENTS.MESSAGE_NEW, handlers.onNewMessage)
    socket.off(SOCKET_EVENTS.MESSAGE_STATUS, handlers.onMessageStatus)
    socket.off(SOCKET_EVENTS.PRESENCE, handlers.onPresence)
    socket.off(SOCKET_EVENTS.TYPING, handlers.onTyping)
    socket.off(SOCKET_EVENTS.CONVERSATION_UPDATED, handlers.onConversationUpdated)
    socket.off(SOCKET_EVENTS.MESSAGE_DELETED, handlers.onMessageDeleted)
  }
}

// Envia uma mensagem e resolve com o ack do servidor.
export function emitSend(payload: SendMessagePayload): Promise<SendAck> {
  return new Promise((resolve) => {
    getSocket().emit(SOCKET_EVENTS.MESSAGE_SEND, payload, (ack: SendAck) => resolve(ack))
  })
}

export function emitOpen(conversationId: string): void {
  getSocket().emit(SOCKET_EVENTS.CONVERSATION_OPEN, { conversation_id: conversationId })
}

export function emitRead(conversationId: string): void {
  getSocket().emit(SOCKET_EVENTS.MESSAGE_READ, { conversation_id: conversationId })
}

export function emitTyping(conversationId: string, typing: boolean): void {
  getSocket().emit(SOCKET_EVENTS.TYPING, { conversation_id: conversationId, typing })
}

export function emitDeleteMessage(
  conversationId: string,
  messageId: string,
  scope: DeleteScope,
): void {
  getSocket().emit(SOCKET_EVENTS.MESSAGE_DELETE, {
    conversation_id: conversationId,
    message_id: messageId,
    scope,
  })
}
