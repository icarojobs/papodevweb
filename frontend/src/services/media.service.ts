import { api } from '@/lib/api'
import type { MediaPublic } from '@/types/chat'

// Camada de upload de mídia (imagens, arquivos e áudio) para o backend/MinIO.
export const mediaService = {
  async upload(file: File): Promise<MediaPublic> {
    const form = new FormData()
    form.append('file', file)
    const { data } = await api.post<MediaPublic>('/media', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}
