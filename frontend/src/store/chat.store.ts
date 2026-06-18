import { create } from 'zustand'

import {
  bindChatHandlers,
  connectChatSocket,
  emitDeleteMessage,
  emitOpen,
  emitRead,
  emitSend,
  emitTyping,
} from '@/lib/chatSocket'
import { disconnectSocket } from '@/lib/socket'
import { chatService } from '@/services/chat.service'
import type {
  ChatFilter,
  ChatUser,
  Conversation,
  DeleteScope,
  ConversationUpdatedEvent,
  MediaPublic,
  Message,
  MessageDeletedEvent,
  MessageStatusEvent,
  MessageType,
  NewMessageEvent,
  PresenceEvent,
  TypingEvent,
} from '@/types/chat'

// Ordena conversas da mais recente para a mais antiga (igual ao backend).
function sortByRecent(conversations: Conversation[]): Conversation[] {
  return [...conversations].sort((a, b) => b.updated_at.localeCompare(a.updated_at))
}

// Filtro puro da lista (busca + abas All/Unread/Favourites/Groups).
export function filterConversations(
  conversations: Conversation[],
  filter: ChatFilter,
  search: string,
): Conversation[] {
  const term = search.trim().toLowerCase()
  return conversations.filter((conversation) => {
    if (filter === 'unread' && conversation.unread <= 0) return false
    if (filter === 'favourites' && !conversation.favourite) return false
    if (filter === 'groups' && conversation.type !== 'group') return false
    if (term && !conversation.name.toLowerCase().includes(term)) return false
    return true
  })
}

// Deriva o tipo da mensagem a partir do MIME da mídia.
export function messageTypeFromMime(mime: string): MessageType {
  if (mime.startsWith('image/')) return 'image'
  if (mime.startsWith('video/')) return 'video'
  if (mime.startsWith('audio/')) return 'audio'
  return 'document'
}

function upsertConversation(list: Conversation[], incoming: Conversation): Conversation[] {
  const without = list.filter((conversation) => conversation.id !== incoming.id)
  return sortByRecent([incoming, ...without])
}

// Aplica a exclusão de uma mensagem na lista local: "para mim" remove;
// "para todos" transforma em tombstone (sem texto/mídia).
export function applyDeletion(
  messages: Message[],
  messageId: string,
  scope: DeleteScope,
): Message[] {
  if (scope === 'me') return messages.filter((message) => message.id !== messageId)
  return messages.map((message) =>
    message.id === messageId ? { ...message, deleted: true, text: '', media: null } : message,
  )
}

// Remove uma conversa do estado local (lista, mensagens, digitação e seleção).
export function stripConversation(state: ChatState, conversationId: string) {
  const messagesByConversation = { ...state.messagesByConversation }
  delete messagesByConversation[conversationId]
  const typingByConversation = { ...state.typingByConversation }
  delete typingByConversation[conversationId]
  return {
    conversations: state.conversations.filter((c) => c.id !== conversationId),
    messagesByConversation,
    typingByConversation,
    activeConversationId:
      state.activeConversationId === conversationId ? null : state.activeConversationId,
  }
}

interface ChatState {
  conversations: Conversation[]
  messagesByConversation: Record<string, Message[]>
  activeConversationId: string | null
  filter: ChatFilter
  search: string
  userResults: ChatUser[]
  typingByConversation: Record<string, string[]>
  loadingConversations: boolean
  loadingMessages: boolean
  unbind: (() => void) | null

  initialize: () => Promise<void>
  teardown: () => void
  loadConversations: () => Promise<void>
  selectConversation: (conversationId: string) => Promise<void>
  sendMessage: (text: string, media?: MediaPublic | null) => Promise<void>
  deleteMessage: (conversationId: string, messageId: string, scope: DeleteScope) => void
  sendTyping: (typing: boolean) => void
  toggleFavourite: (conversationId: string) => Promise<void>
  leaveGroup: (conversationId: string) => Promise<void>
  deleteConversation: (
    conversationId: string,
    scope: DeleteScope,
    deleteMedia: boolean,
  ) => Promise<void>
  startConversation: (recipientId: string) => Promise<Conversation>
  startGroup: (name: string, memberIds: string[]) => Promise<Conversation>
  setFilter: (filter: ChatFilter) => void
  setSearch: (search: string) => void
  searchUsers: (term: string) => Promise<void>

  receiveMessage: (event: NewMessageEvent) => void
  applyStatus: (event: MessageStatusEvent) => void
  applyPresence: (event: PresenceEvent) => void
  applyTyping: (event: TypingEvent) => void
  applyConversationUpdated: (event: ConversationUpdatedEvent) => void
  applyMessageDeleted: (event: MessageDeletedEvent) => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  messagesByConversation: {},
  activeConversationId: null,
  filter: 'all',
  search: '',
  userResults: [],
  typingByConversation: {},
  loadingConversations: false,
  loadingMessages: false,
  unbind: null,

  initialize: async () => {
    connectChatSocket()
    const unbind = bindChatHandlers({
      onNewMessage: get().receiveMessage,
      onMessageStatus: get().applyStatus,
      onPresence: get().applyPresence,
      onTyping: get().applyTyping,
      onConversationUpdated: get().applyConversationUpdated,
      onMessageDeleted: get().applyMessageDeleted,
    })
    set({ unbind })
    await get().loadConversations()
  },

  teardown: () => {
    get().unbind?.()
    disconnectSocket()
    set({
      conversations: [],
      messagesByConversation: {},
      activeConversationId: null,
      typingByConversation: {},
      userResults: [],
      unbind: null,
    })
  },

  loadConversations: async () => {
    set({ loadingConversations: true })
    const conversations = await chatService.listConversations()
    set({ conversations: sortByRecent(conversations), loadingConversations: false })
  },

  selectConversation: async (conversationId) => {
    set((state) => ({
      activeConversationId: conversationId,
      conversations: state.conversations.map((conversation) =>
        conversation.id === conversationId ? { ...conversation, unread: 0 } : conversation,
      ),
    }))
    emitOpen(conversationId)
    if (!get().messagesByConversation[conversationId]) {
      set({ loadingMessages: true })
      const messages = await chatService.getMessages(conversationId)
      set((state) => ({
        messagesByConversation: { ...state.messagesByConversation, [conversationId]: messages },
        loadingMessages: false,
      }))
    }
  },

  sendMessage: async (text, media) => {
    const conversationId = get().activeConversationId
    if (!conversationId) return
    const trimmed = text.trim()
    if (!trimmed && !media) return
    const type: MessageType = media ? messageTypeFromMime(media.mime) : 'text'
    await emitSend({ conversation_id: conversationId, type, text: trimmed, media })
  },

  deleteMessage: (conversationId, messageId, scope) => {
    emitDeleteMessage(conversationId, messageId, scope)
    set((state) => {
      const messages = state.messagesByConversation[conversationId]
      if (!messages) return state
      return {
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversationId]: applyDeletion(messages, messageId, scope),
        },
      }
    })
  },

  sendTyping: (typing) => {
    const conversationId = get().activeConversationId
    if (conversationId) emitTyping(conversationId, typing)
  },

  toggleFavourite: async (conversationId) => {
    const { favourite } = await chatService.toggleFavourite(conversationId)
    set((state) => ({
      conversations: state.conversations.map((conversation) =>
        conversation.id === conversationId ? { ...conversation, favourite } : conversation,
      ),
    }))
  },

  // Sair/excluir sempre remove a conversa da visão local — mesmo se a chamada
  // falhar (ex.: conversa já removida no servidor) — para nunca ficar "presa".
  leaveGroup: async (conversationId) => {
    try {
      await chatService.leaveGroup(conversationId)
    } finally {
      set((state) => stripConversation(state, conversationId))
    }
  },

  deleteConversation: async (conversationId, scope, deleteMedia) => {
    try {
      await chatService.deleteConversation(conversationId, { scope, deleteMedia })
    } finally {
      set((state) => stripConversation(state, conversationId))
    }
  },

  startConversation: async (recipientId) => {
    const conversation = await chatService.createConversation({ recipient_id: recipientId })
    set((state) => ({
      conversations: upsertConversation(state.conversations, conversation),
      search: '',
      userResults: [],
    }))
    await get().selectConversation(conversation.id)
    return conversation
  },

  startGroup: async (name, memberIds) => {
    const conversation = await chatService.createConversation({
      type: 'group',
      name,
      member_ids: memberIds,
    })
    set((state) => ({ conversations: upsertConversation(state.conversations, conversation) }))
    await get().selectConversation(conversation.id)
    return conversation
  },

  setFilter: (filter) => set({ filter }),
  setSearch: (search) => set(search.trim() ? { search } : { search, userResults: [] }),

  searchUsers: async (term) => {
    const trimmed = term.trim()
    if (!trimmed) {
      set({ userResults: [] })
      return
    }
    set({ userResults: await chatService.searchUsers(trimmed) })
  },

  receiveMessage: ({ conversation_id, message }) => {
    set((state) => {
      const existing = state.messagesByConversation[conversation_id] ?? []
      if (existing.some((item) => item.id === message.id)) return state
      return {
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversation_id]: [...existing, message],
        },
      }
    })
    // Se a conversa está aberta, marca como lida imediatamente.
    if (get().activeConversationId === conversation_id) {
      emitRead(conversation_id)
    }
  },

  applyStatus: ({ conversation_id, message_ids, status, user_id }) => {
    set((state) => {
      const messages = state.messagesByConversation[conversation_id]
      if (!messages) return state
      const ids = new Set(message_ids)
      const updated = messages.map((message) => {
        if (!ids.has(message.id)) return message
        const readBy =
          status === 'read' && !message.read_by.includes(user_id)
            ? [...message.read_by, user_id]
            : message.read_by
        const deliveredTo = message.delivered_to.includes(user_id)
          ? message.delivered_to
          : [...message.delivered_to, user_id]
        return { ...message, status, read_by: readBy, delivered_to: deliveredTo }
      })
      return {
        messagesByConversation: { ...state.messagesByConversation, [conversation_id]: updated },
      }
    })
  },

  applyPresence: ({ user_id, online, last_seen }) => {
    set((state) => ({
      conversations: state.conversations.map((conversation) => ({
        ...conversation,
        participants: conversation.participants.map((participant) =>
          participant.id === user_id ? { ...participant, online, last_seen } : participant,
        ),
      })),
    }))
  },

  applyTyping: ({ conversation_id, user_id, typing }) => {
    set((state) => {
      const current = state.typingByConversation[conversation_id] ?? []
      const next = typing
        ? Array.from(new Set([...current, user_id]))
        : current.filter((id) => id !== user_id)
      return {
        typingByConversation: { ...state.typingByConversation, [conversation_id]: next },
      }
    })
  },

  applyConversationUpdated: ({ conversation }) => {
    set((state) => {
      const isActive = state.activeConversationId === conversation.id
      // Conversa aberta permanece sem badge de não-lidas.
      const merged = isActive ? { ...conversation, unread: 0 } : conversation
      return { conversations: upsertConversation(state.conversations, merged) }
    })
  },

  applyMessageDeleted: ({ conversation_id, message_id, scope }) => {
    set((state) => {
      const messages = state.messagesByConversation[conversation_id]
      if (!messages) return state
      return {
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversation_id]: applyDeletion(messages, message_id, scope),
        },
      }
    })
  },
}))
