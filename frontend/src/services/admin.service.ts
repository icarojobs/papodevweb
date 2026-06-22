import { api } from '@/lib/api'
import type { EmailSettings, EmailSettingsPayload } from '@/types/admin'
import type { MessageResponse } from '@/types/auth'

// Camada de acesso à API administrativa (/admin) — e-mail de disparo.
export const adminService = {
  async getEmailSettings(): Promise<EmailSettings> {
    const { data } = await api.get<EmailSettings>('/admin/settings/email')
    return data
  },

  async updateEmailSettings(payload: EmailSettingsPayload): Promise<EmailSettings> {
    const { data } = await api.put<EmailSettings>('/admin/settings/email', payload)
    return data
  },

  async sendTestEmail(to: string): Promise<MessageResponse> {
    const { data } = await api.post<MessageResponse>('/admin/settings/email/test', { to })
    return data
  },
}
