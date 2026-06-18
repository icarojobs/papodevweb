import { describe, expect, it, vi } from 'vitest'

import { api } from '@/lib/api'
import { chatService } from './chat.service'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

describe('chatService', () => {
  it('searchUsers chama GET /users/search com a query', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [] })
    await chatService.searchUsers('ana')
    expect(api.get).toHaveBeenCalledWith('/users/search', { params: { q: 'ana' } })
  })

  it('listConversations chama GET /conversations', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [{ id: '1' }] })
    const result = await chatService.listConversations()
    expect(api.get).toHaveBeenCalledWith('/conversations')
    expect(result).toEqual([{ id: '1' }])
  })

  it('createConversation chama POST /conversations', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { id: '1' } })
    await chatService.createConversation({ recipient_id: '2' })
    expect(api.post).toHaveBeenCalledWith('/conversations', { recipient_id: '2' })
  })

  it('getMessages chama GET com paginação', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [] })
    await chatService.getMessages('c1', { limit: 10 })
    expect(api.get).toHaveBeenCalledWith('/conversations/c1/messages', { params: { limit: 10 } })
  })

  it('getMessages usa query vazia por padrão', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [] })
    await chatService.getMessages('c1')
    expect(api.get).toHaveBeenCalledWith('/conversations/c1/messages', { params: {} })
  })

  it('toggleFavourite chama PATCH', async () => {
    vi.mocked(api.patch).mockResolvedValue({ data: { favourite: true } })
    const result = await chatService.toggleFavourite('c1')
    expect(api.patch).toHaveBeenCalledWith('/conversations/c1/favourite')
    expect(result).toEqual({ favourite: true })
  })

  it('leaveGroup chama POST /leave', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: undefined })
    await chatService.leaveGroup('c1')
    expect(api.post).toHaveBeenCalledWith('/conversations/c1/leave')
  })

  it('deleteConversation chama DELETE com escopo e mídia', async () => {
    vi.mocked(api.delete).mockResolvedValue({ data: undefined })
    await chatService.deleteConversation('c1', { scope: 'everyone', deleteMedia: true })
    expect(api.delete).toHaveBeenCalledWith('/conversations/c1', {
      params: { scope: 'everyone', delete_media: true },
    })
  })
})
