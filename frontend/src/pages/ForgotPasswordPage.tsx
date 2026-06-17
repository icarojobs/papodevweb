import {
  Alert,
  AlertIcon,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Link as ChakraLink,
  Text,
  useToast,
  VStack,
} from '@chakra-ui/react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'

import { AuthLayout } from '@/components/auth/AuthLayout'
import { ROUTES } from '@/lib/constants'
import { getErrorMessage } from '@/lib/errors'
import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/lib/validation'
import { authService } from '@/services/auth.service'

export function ForgotPasswordPage() {
  const toast = useToast()
  const [sent, setSent] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormData>({ resolver: zodResolver(forgotPasswordSchema) })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      await authService.forgotPassword(data.email)
      setSent(true)
    } catch (error) {
      toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
    }
  }

  return (
    <AuthLayout
      title="Recuperar senha"
      subtitle="Informe seu e-mail e enviaremos um link para redefinir a senha."
      footer={
        <ChakraLink as={Link} to={ROUTES.LOGIN} color="whatsapp.500" fontWeight="bold" fontSize="sm">
          Voltar para o login
        </ChakraLink>
      }
    >
      {sent ? (
        <Alert status="success" borderRadius="md" bg="whatsapp.600" color="white">
          <AlertIcon color="white" />
          <Text fontSize="sm">
            Se o e-mail estiver cadastrado, enviamos um link de redefinição. Verifique sua
            caixa de entrada.
          </Text>
        </Alert>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <VStack spacing={4} align="stretch">
            <FormControl isInvalid={!!errors.email}>
              <FormLabel color="whiteAlpha.800">E-mail</FormLabel>
              <Input type="email" placeholder="voce@exemplo.com" {...register('email')} />
              <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
            </FormControl>

            <Button type="submit" variant="whatsapp" isLoading={isSubmitting}>
              Enviar link
            </Button>
          </VStack>
        </form>
      )}
    </AuthLayout>
  )
}
