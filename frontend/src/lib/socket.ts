import { io, type Socket } from 'socket.io-client'

import { SOCKET_URL, STORAGE_KEYS } from './constants'

let socket: Socket | null = null

// Cria (ou reutiliza) a conexão Socket.IO autenticada pelo access token.
export function getSocket(): Socket {
  if (!socket) {
    socket = io(SOCKET_URL, {
      autoConnect: false,
      auth: { token: localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) ?? '' },
    })
  }
  return socket
}

export function disconnectSocket(): void {
  socket?.disconnect()
  socket = null
}
