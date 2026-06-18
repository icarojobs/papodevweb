// Tipos do domínio de chat — espelham os schemas públicos do backend.

export type ConversationType = 'direct' | 'group'
export type MessageType = 'text' | 'image' | 'video' | 'document' | 'audio'
export type MessageStatus = 'sent' | 'delivered' | 'read'

export interface ChatUser {
  id: string
  full_name: string
  email: string
  online: boolean
  last_seen: string | null
}

export interface MediaPublic {
  key: string
  url: string
  mime: string
  size: number
  name: string
  duration?: number | null
}

export interface Message {
  id: string
  conversation_id: string
  sender_id: string
  type: MessageType
  text: string
  media?: MediaPublic | null
  created_at: string
  status: MessageStatus
  read_by: string[]
  delivered_to: string[]
  deleted?: boolean
}

export interface Conversation {
  id: string
  type: ConversationType
  name: string
  participants: ChatUser[]
  last_message: Message | null
  unread: number
  favourite: boolean
  created_at: string
  updated_at: string
}

export interface CreateConversationPayload {
  type?: ConversationType
  recipient_id?: string
  name?: string
  member_ids?: string[]
}

export interface SendMessagePayload {
  conversation_id: string
  type: MessageType
  text: string
  media?: MediaPublic | null
}

export interface SendAck {
  ok: boolean
  message?: Message
  error?: string
}

// Eventos servidor -> cliente.
export interface NewMessageEvent {
  conversation_id: string
  message: Message
}

export interface MessageStatusEvent {
  conversation_id: string
  message_ids: string[]
  status: MessageStatus
  user_id: string
}

export interface PresenceEvent {
  user_id: string
  online: boolean
  last_seen: string | null
}

export interface TypingEvent {
  conversation_id: string
  user_id: string
  typing: boolean
}

export interface ConversationUpdatedEvent {
  conversation: Conversation
}

export interface MessageDeletedEvent {
  conversation_id: string
  message_id: string
  scope: DeleteScope
}

// Filtros da lista de conversas.
export type ChatFilter = 'all' | 'unread' | 'favourites' | 'groups'

// Escopo da exclusão de conversa.
export type DeleteScope = 'me' | 'everyone'
