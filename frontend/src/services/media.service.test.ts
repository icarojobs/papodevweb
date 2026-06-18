import { describe, expect, it, vi } from 'vitest'

import { api } from '@/lib/api'
import { mediaService } from './media.service'

vi.mock('@/lib/api', () => ({
  api: { post: vi.fn() },
}))

describe('mediaService', () => {
  it('upload envia FormData multipart para /media', async () => {
    const media = { key: 'k', url: 'u', mime: 'image/png', size: 3, name: 'a.png' }
    vi.mocked(api.post).mockResolvedValue({ data: media })

    const file = new File([new Uint8Array([1, 2, 3])], 'a.png', { type: 'image/png' })
    const result = await mediaService.upload(file)

    expect(result).toEqual(media)
    const [url, body, config] = vi.mocked(api.post).mock.calls[0]
    expect(url).toBe('/media')
    expect(body).toBeInstanceOf(FormData)
    expect((body as FormData).get('file')).toBe(file)
    expect(config).toMatchObject({ headers: { 'Content-Type': 'multipart/form-data' } })
  })
})
