import { Navigate, Outlet } from 'react-router-dom'

import { ROUTES } from '@/lib/constants'
import { useAuthStore } from '@/store/auth.store'

// Protege rotas administrativas: exige autenticação E perfil admin.
export function AdminRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const user = useAuthStore((state) => state.user)

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }
  if (!user?.is_admin) {
    return <Navigate to={ROUTES.CHAT} replace />
  }
  return <Outlet />
}
