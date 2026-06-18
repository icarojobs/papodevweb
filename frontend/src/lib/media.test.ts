import { describe, expect, it } from 'vitest'

import { MEDIA_LIMITS } from './constants'
import { mediaCategory, validateMediaFile } from './media'

function fakeFile(type: string, size: number): File {
  const file = new File(['x'], 'arquivo', { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

describe('mediaCategory', () => {
  it('classifica os MIME types', () => {
    expect(mediaCategory('image/png')).toBe('image')
    expect(mediaCategory('video/mp4')).toBe('video')
    expect(mediaCategory('audio/webm')).toBe('audio')
    expect(mediaCategory('application/pdf')).toBe('document')
    expect(mediaCategory('text/plain')).toBe('document')
    expect(mediaCategory('font/woff2')).toBeNull()
  })
})

describe('validateMediaFile', () => {
  it('aceita arquivos dentro do limite', () => {
    expect(validateMediaFile(fakeFile('image/png', 1024))).toBeNull()
    expect(validateMediaFile(fakeFile('video/mp4', MEDIA_LIMITS.video.bytes))).toBeNull()
  })

  it('rejeita tipo não suportado', () => {
    expect(validateMediaFile(fakeFile('font/woff2', 10))).toBe('Tipo de arquivo não suportado.')
  })

  it('rejeita imagem acima de 2MB', () => {
    const error = validateMediaFile(fakeFile('image/png', MEDIA_LIMITS.image.bytes + 1))
    expect(error).toBe('A imagem excede o tamanho máximo de 2 MB.')
  })

  it('rejeita vídeo acima de 50MB', () => {
    const error = validateMediaFile(fakeFile('video/mp4', MEDIA_LIMITS.video.bytes + 1))
    expect(error).toBe('O vídeo excede o tamanho máximo de 50 MB.')
  })

  it('rejeita documento acima de 2MB', () => {
    const error = validateMediaFile(fakeFile('application/pdf', MEDIA_LIMITS.document.bytes + 1))
    expect(error).toBe('O documento excede o tamanho máximo de 2 MB.')
  })
})
