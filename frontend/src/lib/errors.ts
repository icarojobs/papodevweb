import { AxiosError } from 'axios'

const DEFAULT_ERROR_MESSAGE = 'Algo deu errado. Tente novamente.'

// Extrai uma mensagem amigável (pt-br) de erros vindos da API.
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
  }
  return DEFAULT_ERROR_MESSAGE
}
