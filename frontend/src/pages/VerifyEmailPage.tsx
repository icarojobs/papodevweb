import {
  Alert,
  AlertIcon,
  Button,
  Link as ChakraLink,
  Spinner,
  Text,
  VStack,
} from '@chakra-ui/react'
import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { AuthLayout } from '@/components/auth/AuthLayout'
import { ROUTES } from '@/lib/constants'
import { getErrorMessage } from '@/lib/errors'
import { authService } from '@/services/auth.service'

type Status = 'loading' | 'success' | 'error'

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [status, setStatus] = useState<Status>('loading')
  const [message, setMessage] = useState('')
  // Evita dupla chamada no StrictMode (efeito roda duas vezes em dev).
  const startedRef = useRef(false)

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true

    if (!token) {
      setStatus('error')
      setMessage('Link de confirmação inválido ou incompleto.')
      return
    }

    authService
      .verifyEmail(token)
      .then(() => {
        setStatus('success')
        setMessage('E-mail confirmado com sucesso. Você já pode entrar.')
      })
      .catch((error) => {
        setStatus('error')
        setMessage(getErrorMessage(error))
      })
  }, [token])

  return (
    <AuthLayout
      title="Confirmação de e-mail"
      subtitle="Estamos ativando a sua conta."
      footer={
        <ChakraLink as={Link} to={ROUTES.LOGIN} color="whatsapp.500" fontWeight="bold" fontSize="sm">
          Ir para o login
        </ChakraLink>
      }
    >
      {status === 'loading' ? (
        <VStack spacing={3} py={4}>
          <Spinner color="whatsapp.500" />
          <Text color="whiteAlpha.700" fontSize="sm">
            Confirmando o seu e-mail...
          </Text>
        </VStack>
      ) : (
        <VStack spacing={4} align="stretch">
          <Alert status={status} borderRadius="md">
            <AlertIcon />
            <Text fontSize="sm">{message}</Text>
          </Alert>
          {status === 'success' && (
            <Button as={Link} to={ROUTES.LOGIN} variant="whatsapp">
              Entrar
            </Button>
          )}
        </VStack>
      )}
    </AuthLayout>
  )
}
