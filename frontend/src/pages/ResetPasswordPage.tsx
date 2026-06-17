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
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { AuthLayout } from '@/components/auth/AuthLayout'
import { ROUTES } from '@/lib/constants'
import { getErrorMessage } from '@/lib/errors'
import { resetPasswordSchema, type ResetPasswordFormData } from '@/lib/validation'
import { authService } from '@/services/auth.service'

export function ResetPasswordPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({ resolver: zodResolver(resetPasswordSchema) })

  const onSubmit = async (data: ResetPasswordFormData) => {
    try {
      await authService.resetPassword({ token, ...data })
      toast({ title: 'Senha redefinida com sucesso.', status: 'success', isClosable: true })
      navigate(ROUTES.LOGIN)
    } catch (error) {
      toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
    }
  }

  const backToLogin = (
    <ChakraLink as={Link} to={ROUTES.LOGIN} color="whatsapp.500" fontWeight="bold" fontSize="sm">
      Voltar para o login
    </ChakraLink>
  )

  if (!token) {
    return (
      <AuthLayout
        title="Redefinir senha"
        subtitle="Link inválido."
        footer={backToLogin}
      >
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          <Text fontSize="sm">
            Link de redefinição inválido ou incompleto. Solicite um novo link.
          </Text>
        </Alert>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Redefinir senha"
      subtitle="Crie uma nova senha para a sua conta."
      footer={backToLogin}
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <VStack spacing={4} align="stretch">
          <FormControl isInvalid={!!errors.password}>
            <FormLabel color="whiteAlpha.800">Nova senha</FormLabel>
            <Input type="password" placeholder="••••••••" {...register('password')} />
            <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isInvalid={!!errors.confirm_password}>
            <FormLabel color="whiteAlpha.800">Repetir nova senha</FormLabel>
            <Input type="password" placeholder="••••••••" {...register('confirm_password')} />
            <FormErrorMessage>{errors.confirm_password?.message}</FormErrorMessage>
          </FormControl>

          <Button type="submit" variant="whatsapp" isLoading={isSubmitting}>
            Redefinir senha
          </Button>
        </VStack>
      </form>
    </AuthLayout>
  )
}
