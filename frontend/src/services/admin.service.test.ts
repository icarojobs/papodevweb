import { describe, expect, it, vi } from 'vitest'

import { api } from '@/lib/api'
import { adminService } from './admin.service'

vi.mock('@/lib/api', () => ({
  api: { get: vi.fn(), put: vi.fn(), post: vi.fn() },
}))

const emailSettings = {
  host: 'smtp.x',
  port: 587,
  username: 'apikey',
  from_email: 'no-reply@x.com',
  from_name: 'Papo Dev Web',
  use_tls: true,
  password_set: true,
}

describe('adminService', () => {
  it('getEmailSettings chama GET /admin/settings/email', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: emailSettings })
    const result = await adminService.getEmailSettings()
    expect(api.get).toHaveBeenCalledWith('/admin/settings/email')
    expect(result).toEqual(emailSettings)
  })

  it('updateEmailSettings chama PUT /admin/settings/email', async () => {
    vi.mocked(api.put).mockResolvedValue({ data: emailSettings })
    const payload = {
      host: 'smtp.x',
      port: 587,
      username: 'apikey',
      password: 'segredo',
      from_email: 'no-reply@x.com',
      from_name: 'Papo Dev Web',
      use_tls: true,
    }
    const result = await adminService.updateEmailSettings(payload)
    expect(api.put).toHaveBeenCalledWith('/admin/settings/email', payload)
    expect(result).toEqual(emailSettings)
  })

  it('sendTestEmail chama POST /admin/settings/email/test', async () => {
    vi.mocked(api.post).mockResolvedValue({ data: { message: 'ok' } })
    const result = await adminService.sendTestEmail('qa@example.com')
    expect(api.post).toHaveBeenCalledWith('/admin/settings/email/test', { to: 'qa@example.com' })
    expect(result).toEqual({ message: 'ok' })
  })
})
