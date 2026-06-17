import { describe, expect, it } from 'vitest'
import { Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from './ProtectedRoute'
import { useAuthStore } from '@/store/auth.store'
import { renderWithProviders, screen } from '@/test/utils'

function Tree() {
  return (
    <Routes>
      <Route path="/login" element={<div>Tela de login</div>} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<div>Conteúdo protegido</div>} />
      </Route>
    </Routes>
  )
}

describe('ProtectedRoute', () => {
  it('redireciona para login quando não autenticado', () => {
    useAuthStore.setState({ isAuthenticated: false })
    renderWithProviders(<Tree />)
    expect(screen.getByText('Tela de login')).toBeInTheDocument()
  })

  it('renderiza o conteúdo quando autenticado', () => {
    useAuthStore.setState({ isAuthenticated: true })
    renderWithProviders(<Tree />)
    expect(screen.getByText('Conteúdo protegido')).toBeInTheDocument()
  })
})
