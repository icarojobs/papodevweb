// Tipos da área administrativa (/admin) — configuração do e-mail de disparo.

export interface EmailSettings {
  host: string
  port: number
  username: string
  from_email: string
  from_name: string
  use_tls: boolean
  // Indica se já existe uma senha salva (a senha em si nunca é exposta).
  password_set: boolean
}

export interface EmailSettingsPayload {
  host: string
  port: number
  username: string
  // Omitida/vazia => mantém a senha atual no servidor (write-only).
  password?: string
  from_email: string
  from_name: string
  use_tls: boolean
}
