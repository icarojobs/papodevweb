import axios from 'axios'

import { API_URL, STORAGE_KEYS } from './constants'

// Instância única do axios. `withCredentials` permite o envio do cookie
// httpOnly de refresh token usado pelas rotas /auth.
export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
