import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { AdminSettingsPage } from './AdminSettingsPage'
import { adminService } from '@/services/admin.service'
import { renderWithProviders, screen, waitFor } from '@/test/utils'

vi.mock('@/services/admin.service', () => ({
  adminService: {
    getEmailSettings: vi.fn(),
    updateEmailSettings: vi.fn(),
    sendTestEmail: vi.fn(),
  },
}))

const SETTINGS = {
  host: 'smtp.atual',
  port: 587,
  username: 'apikey',
  from_email: 'no-reply@papodevweb.com.br',
  from_name: 'Papo Dev Web',
  use_tls: true,
  password_set: false,
}

function mockLoad(overrides = {}) {
  vi.mocked(adminService.getEmailSettings).mockResolvedValue({ ...SETTINGS, ...overrides })
}

async function renderLoaded() {
  renderWithProviders(<AdminSettingsPage />)
  // Espera o carregamento concluir (spinner -> formulário).
  return (await screen.findByLabelText('Servidor SMTP')) as HTMLInputElement
}

describe('AdminSettingsPage', () => {
  it('carrega e preenche a configuração atual', async () => {
    mockLoad()
    const host = await renderLoaded()
    expect(host.value).toBe('smtp.atual')
    expect((screen.getByLabelText('E-mail do remetente') as HTMLInputElement).value).toBe(
      'no-reply@papodevweb.com.br',
    )
  })

  it('exibe a badge "configurada" quando já há senha salva', async () => {
    mockLoad({ password_set: true })
    renderWithProviders(<AdminSettingsPage />)
    await screen.findByLabelText('Servidor SMTP')
    expect(screen.getByText('configurada')).toBeInTheDocument()
  })

  it('mostra erro de validação quando o servidor SMTP fica vazio', async () => {
    mockLoad()
    const host = await renderLoaded()
    await userEvent.clear(host)
    await userEvent.click(screen.getByRole('button', { name: 'Salvar configurações' }))

    expect(await screen.findByText('Informe o servidor SMTP.')).toBeInTheDocument()
    expect(adminService.updateEmailSettings).not.toHaveBeenCalled()
  })

  it('salva omitindo a senha quando o campo está vazio', async () => {
    mockLoad()
    vi.mocked(adminService.updateEmailSettings).mockResolvedValue({ ...SETTINGS })
    await renderLoaded()

    await userEvent.click(screen.getByRole('button', { name: 'Salvar configurações' }))

    await waitFor(() => expect(adminService.updateEmailSettings).toHaveBeenCalled())
    const payload = vi.mocked(adminService.updateEmailSettings).mock.calls[0][0]
    expect(payload.host).toBe('smtp.atual')
    expect(payload.password).toBeUndefined()
    expect(await screen.findByText('Configurações de e-mail salvas.')).toBeInTheDocument()
  })

  it('inclui a senha no payload quando preenchida', async () => {
    mockLoad()
    vi.mocked(adminService.updateEmailSettings).mockResolvedValue({ ...SETTINGS, password_set: true })
    await renderLoaded()

    await userEvent.type(screen.getByLabelText('Senha'), 'novaSenha123')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar configurações' }))

    await waitFor(() => expect(adminService.updateEmailSettings).toHaveBeenCalled())
    const payload = vi.mocked(adminService.updateEmailSettings).mock.calls[0][0]
    expect(payload.password).toBe('novaSenha123')
  })

  it('mostra erro quando salvar falha', async () => {
    mockLoad()
    vi.mocked(adminService.updateEmailSettings).mockRejectedValue(new Error('falhou'))
    await renderLoaded()

    await userEvent.click(screen.getByRole('button', { name: 'Salvar configurações' }))

    expect(await screen.findByText('Algo deu errado. Tente novamente.')).toBeInTheDocument()
  })

  it('avisa ao enviar e-mail de teste sem destinatário', async () => {
    mockLoad()
    await renderLoaded()

    await userEvent.click(screen.getByRole('button', { name: 'Enviar teste' }))

    expect(await screen.findByText('Informe um e-mail para o teste.')).toBeInTheDocument()
    expect(adminService.sendTestEmail).not.toHaveBeenCalled()
  })

  it('envia e-mail de teste para o destinatário informado', async () => {
    mockLoad()
    vi.mocked(adminService.sendTestEmail).mockResolvedValue({ message: 'E-mail de teste enviado.' })
    await renderLoaded()

    await userEvent.type(screen.getByLabelText('Enviar para'), 'qa@example.com')
    await userEvent.click(screen.getByRole('button', { name: 'Enviar teste' }))

    await waitFor(() => expect(adminService.sendTestEmail).toHaveBeenCalledWith('qa@example.com'))
    expect(await screen.findByText('E-mail de teste enviado.')).toBeInTheDocument()
  })

  it('mostra erro quando o carregamento inicial falha', async () => {
    vi.mocked(adminService.getEmailSettings).mockRejectedValue(new Error('falhou'))
    renderWithProviders(<AdminSettingsPage />)
    // Mesmo com erro no load, o formulário aparece (com valores padrão).
    expect(await screen.findByLabelText('Servidor SMTP')).toBeInTheDocument()
  })
})
