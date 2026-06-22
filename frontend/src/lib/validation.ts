import { z } from 'zod'

import { VALIDATION } from './constants'

// Schemas de validação dos formulários de autenticação (mensagens em pt-br).
export const loginSchema = z.object({
  email: z.string().email('Informe um e-mail válido.'),
  password: z.string().min(1, 'Informe a senha.'),
})

export const registerSchema = z
  .object({
    full_name: z
      .string()
      .min(VALIDATION.MIN_FULL_NAME_LENGTH, 'Informe seu nome completo.'),
    email: z.string().email('Informe um e-mail válido.'),
    password: z
      .string()
      .min(VALIDATION.MIN_PASSWORD_LENGTH, 'A senha deve ter no mínimo 8 caracteres.'),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'As senhas não conferem.',
    path: ['confirm_password'],
  })

export const forgotPasswordSchema = z.object({
  email: z.string().email('Informe um e-mail válido.'),
})

export const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(VALIDATION.MIN_PASSWORD_LENGTH, 'A senha deve ter no mínimo 8 caracteres.'),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'As senhas não conferem.',
    path: ['confirm_password'],
  })

export type LoginFormData = z.infer<typeof loginSchema>
// Configuração do e-mail de disparo (SMTP) no painel /admin.
export const emailSettingsSchema = z.object({
  host: z.string().min(1, 'Informe o servidor SMTP.'),
  port: z
    .number({ invalid_type_error: 'Informe uma porta válida.' })
    .int('Informe uma porta válida.')
    .min(1, 'Informe uma porta válida.')
    .max(65535, 'Informe uma porta válida.'),
  username: z.string(),
  // Vazia => mantém a senha atual no servidor (write-only).
  password: z.string(),
  from_email: z.string().email('Informe um e-mail de remetente válido.'),
  from_name: z.string(),
  use_tls: z.boolean(),
})

export type RegisterFormData = z.infer<typeof registerSchema>
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>
export type EmailSettingsFormData = z.infer<typeof emailSettingsSchema>
