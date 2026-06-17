import { describe, expect, it } from 'vitest'

import { forgotPasswordSchema, loginSchema, registerSchema, resetPasswordSchema } from './validation'

describe('loginSchema', () => {
  it('aceita credenciais válidas', () => {
    const result = loginSchema.safeParse({ email: 'a@b.com', password: '123' })
    expect(result.success).toBe(true)
  })

  it('rejeita e-mail inválido', () => {
    const result = loginSchema.safeParse({ email: 'invalido', password: '123' })
    expect(result.success).toBe(false)
  })
})

describe('registerSchema', () => {
  const base = {
    full_name: 'Maria da Silva',
    email: 'maria@example.com',
    password: 'senhaSegura123',
    confirm_password: 'senhaSegura123',
  }

  it('aceita cadastro válido', () => {
    expect(registerSchema.safeParse(base).success).toBe(true)
  })

  it('rejeita quando as senhas não conferem', () => {
    const result = registerSchema.safeParse({ ...base, confirm_password: 'outra123' })
    expect(result.success).toBe(false)
  })

  it('rejeita senha curta', () => {
    const result = registerSchema.safeParse({ ...base, password: '123', confirm_password: '123' })
    expect(result.success).toBe(false)
  })
})

describe('forgotPasswordSchema', () => {
  it('aceita e-mail válido', () => {
    expect(forgotPasswordSchema.safeParse({ email: 'a@b.com' }).success).toBe(true)
  })

  it('rejeita e-mail inválido', () => {
    expect(forgotPasswordSchema.safeParse({ email: 'invalido' }).success).toBe(false)
  })
})

describe('resetPasswordSchema', () => {
  it('aceita senhas iguais e válidas', () => {
    const result = resetPasswordSchema.safeParse({
      password: 'novaSenha123',
      confirm_password: 'novaSenha123',
    })
    expect(result.success).toBe(true)
  })

  it('rejeita senhas divergentes', () => {
    const result = resetPasswordSchema.safeParse({
      password: 'novaSenha123',
      confirm_password: 'outra123',
    })
    expect(result.success).toBe(false)
  })
})
