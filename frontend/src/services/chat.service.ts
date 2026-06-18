import { api } from '@/lib/api'
import type {
  ChatUser,
  Conversation,
  CreateConversationPayload,
  DeleteScope,
  Message,
} from '@/types/chat'

interface MessagesQuery {
  before?: string
  limit?: number
}

interface DeleteOptions {
  scope: DeleteScope
  deleteMedia: boolean
}

// Camada de acesso à API de chat (isola os endpoints HTTP).
export const chatService = {
  async searchUsers(query: string): Promise<ChatUser[]> {
    const { data } = await api.get<ChatUser[]>('/users/search', { params: { q: query } })
    return data
  },

  async listConversations(): Promise<Conversation[]> {
    const { data } = await api.get<Conversation[]>('/conversations')
    return data
  },

  async createConversation(payload: CreateConversationPayload): Promise<Conversation> {
    const { data } = await api.post<Conversation>('/conversations', payload)
    return data
  },

  async getMessages(conversationId: string, query: MessagesQuery = {}): Promise<Message[]> {
    const { data } = await api.get<Message[]>(`/conversations/${conversationId}/messages`, {
      params: query,
    })
    return data
  },

  async toggleFavourite(conversationId: string): Promise<{ favourite: boolean }> {
    const { data } = await api.patch<{ favourite: boolean }>(
      `/conversations/${conversationId}/favourite`,
    )
    return data
  },

  async leaveGroup(conversationId: string): Promise<void> {
    await api.post(`/conversations/${conversationId}/leave`)
  },

  async deleteConversation(
    conversationId: string,
    { scope, deleteMedia }: DeleteOptions,
  ): Promise<void> {
    await api.delete(`/conversations/${conversationId}`, {
      params: { scope, delete_media: deleteMedia },
    })
  },
}
