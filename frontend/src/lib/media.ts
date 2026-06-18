import { MEDIA_LIMITS } from './constants'

export type MediaCategory = keyof typeof MEDIA_LIMITS

// Classifica um MIME type em uma categoria de mídia (ou null se não suportado).
export function mediaCategory(mime: string): MediaCategory | null {
  if (mime.startsWith('image/')) return 'image'
  if (mime.startsWith('video/')) return 'video'
  if (mime.startsWith('audio/')) return 'audio'
  if (mime.startsWith('application/') || mime.startsWith('text/')) return 'document'
  return null
}

// Valida um arquivo antes do upload. Retorna a mensagem de erro (pt-br) ou null.
export function validateMediaFile(file: File): string | null {
  const category = mediaCategory(file.type || '')
  if (category === null) {
    return 'Tipo de arquivo não suportado.'
  }
  const limit = MEDIA_LIMITS[category]
  if (file.size > limit.bytes) {
    return `${limit.label} excede o tamanho máximo de ${limit.human}.`
  }
  return null
}
