import {
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
import { Link, useNavigate } from 'react-router-dom'

import { AuthLayout } from '@/components/auth/AuthLayout'
import { ROUTES } from '@/lib/constants'
import { loginSchema, type LoginFormData } from '@/lib/validation'
import { useAuthStore } from '@/store/auth.store'
import { getErrorMessage } from '@/lib/errors'

export function LoginPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const login = useAuthStore((state) => state.login)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) })

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data)
      navigate(ROUTES.HOME)
    } catch (error) {
      toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
    }
  }

  return (
    <AuthLayout
      title="Entrar"
      subtitle="Acesse sua conta para continuar no Papo Dev Web."
      footer={
        <Text color="whiteAlpha.700" fontSize="sm">
          Ainda não tem conta?{' '}
          <ChakraLink as={Link} to={ROUTES.REGISTER} color="whatsapp.500" fontWeight="bold">
            Cadastre-se
          </ChakraLink>
        </Text>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <VStack spacing={4} align="stretch">
          <FormControl isInvalid={!!errors.email}>
            <FormLabel color="whiteAlpha.800">E-mail</FormLabel>
            <Input type="email" placeholder="voce@exemplo.com" {...register('email')} />
            <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isInvalid={!!errors.password}>
            <FormLabel color="whiteAlpha.800">Senha</FormLabel>
            <Input type="password" placeholder="••••••••" {...register('password')} />
            <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
          </FormControl>

          <ChakraLink
            as={Link}
            to={ROUTES.FORGOT_PASSWORD}
            color="whatsapp.500"
            fontSize="sm"
            alignSelf="flex-end"
          >
            Esqueceu a senha?
          </ChakraLink>

          <Button type="submit" variant="whatsapp" isLoading={isSubmitting}>
            Entrar
          </Button>
        </VStack>
      </form>
    </AuthLayout>
  )
}
