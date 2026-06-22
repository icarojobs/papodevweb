import { describe, expect, it } from 'vitest'
import { Route, Routes } from 'react-router-dom'

import { AdminRoute } from './AdminRoute'
import { useAuthStore } from '@/store/auth.store'
import { renderWithProviders, screen } from '@/test/utils'

const adminUser = {
  id: '1',
  full_name: 'Admin',
  email: 'admin@example.com',
  created_at: '2026-01-01T00:00:00Z',
  is_admin: true,
}

function Tree() {
  return (
    <Routes>
      <Route path="/login" element={<div>Tela de login</div>} />
      <Route path="/chat" element={<div>Tela de chat</div>} />
      <Route element={<AdminRoute />}>
        <Route path="/" element={<div>Conteúdo admin</div>} />
      </Route>
    </Routes>
  )
}

describe('AdminRoute', () => {
  it('redireciona para login quando não autenticado', () => {
    useAuthStore.setState({ isAuthenticated: false, user: null })
    renderWithProviders(<Tree />)
    expect(screen.getByText('Tela de login')).toBeInTheDocument()
  })

  it('redireciona para o chat quando autenticado sem ser admin', () => {
    useAuthStore.setState({ isAuthenticated: true, user: { ...adminUser, is_admin: false } })
    renderWithProviders(<Tree />)
    expect(screen.getByText('Tela de chat')).toBeInTheDocument()
  })

  it('renderiza o conteúdo quando admin', () => {
    useAuthStore.setState({ isAuthenticated: true, user: adminUser })
    renderWithProviders(<Tree />)
    expect(screen.getByText('Conteúdo admin')).toBeInTheDocument()
  })
})
