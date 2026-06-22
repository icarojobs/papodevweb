export interface UserPublic {
  id: string
  full_name: string
  email: string
  created_at: string
  // Acesso ao painel administrativo (/admin). Opcional por compatibilidade.
  is_admin?: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserPublic
}

export interface RegisterPayload {
  full_name: string
  email: string
  password: string
  confirm_password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface ResetPasswordPayload {
  token: string
  password: string
  confirm_password: string
}

export interface MessageResponse {
  message: string
}
