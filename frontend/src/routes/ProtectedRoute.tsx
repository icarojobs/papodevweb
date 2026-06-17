import { Navigate, Outlet } from 'react-router-dom'

import { ROUTES } from '@/lib/constants'
import { useAuthStore } from '@/store/auth.store'

// Protege rotas autenticadas; redireciona ao login quando não autenticado.
export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <Outlet /> : <Navigate to={ROUTES.LOGIN} replace />
}
