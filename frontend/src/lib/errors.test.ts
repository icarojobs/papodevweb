import { AxiosError } from 'axios'
import { describe, expect, it } from 'vitest'

import { getErrorMessage } from './errors'

describe('getErrorMessage', () => {
  it('extrai o detail de um AxiosError', () => {
    const error = new AxiosError('falha')
    error.response = { data: { detail: 'E-mail já cadastrado.' } } as never
    expect(getErrorMessage(error)).toBe('E-mail já cadastrado.')
  })

  it('retorna mensagem padrão para erro desconhecido', () => {
    expect(getErrorMessage(new Error('x'))).toBe('Algo deu errado. Tente novamente.')
  })

  it('retorna mensagem padrão quando o detail não é string', () => {
    const error = new AxiosError('falha')
    error.response = { data: { detail: { campo: 'erro' } } } as never
    expect(getErrorMessage(error)).toBe('Algo deu errado. Tente novamente.')
  })
})
