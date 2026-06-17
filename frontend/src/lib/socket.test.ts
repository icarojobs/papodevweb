import { afterEach, describe, expect, it, vi } from 'vitest'

import { disconnectSocket, getSocket } from './socket'

vi.mock('socket.io-client', () => ({
  io: vi.fn(() => ({ disconnect: vi.fn() })),
}))

describe('socket', () => {
  afterEach(() => {
    disconnectSocket()
  })

  it('reutiliza a mesma instância de socket', () => {
    const first = getSocket()
    const second = getSocket()
    expect(first).toBe(second)
  })

  it('recria o socket após desconectar', () => {
    const first = getSocket()
    disconnectSocket()
    const second = getSocket()
    expect(first).not.toBe(second)
  })
})
