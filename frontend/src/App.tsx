import { useEffect } from 'react'
import { Center, Spinner } from '@chakra-ui/react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { ROUTES } from '@/lib/constants'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { HomePage } from '@/pages/HomePage'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { TermsPage } from '@/pages/TermsPage'
import { VerifyEmailPage } from '@/pages/VerifyEmailPage'
import { ProtectedRoute } from '@/routes/ProtectedRoute'
import { useAuthStore } from '@/store/auth.store'

export function App() {
  const initializing = useAuthStore((state) => state.initializing)
  const bootstrap = useAuthStore((state) => state.bootstrap)

  // Restaura a sessão (cookie de refresh) antes de decidir as rotas protegidas.
  useEffect(() => {
    bootstrap()
  }, [bootstrap])

  if (initializing) {
    return (
      <Center minH="100vh" bg="#0b141a">
        <Spinner color="green.400" size="xl" thickness="3px" />
      </Center>
    )
  }

  return (
    <Routes>
      <Route path={ROUTES.HOME} element={<LandingPage />} />
      <Route path={ROUTES.LOGIN} element={<LoginPage />} />
      <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
      <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />
      <Route path={ROUTES.RESET_PASSWORD} element={<ResetPasswordPage />} />
      <Route path={ROUTES.VERIFY_EMAIL} element={<VerifyEmailPage />} />
      <Route path={ROUTES.TERMS} element={<TermsPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path={ROUTES.CHAT} element={<HomePage />} />
      </Route>
      <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
    </Routes>
  )
}
