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
import { registerSchema, type RegisterFormData } from '@/lib/validation'
import { authService } from '@/services/auth.service'

export function RegisterPage() {
  const toast = useToast()
  const [sent, setSent] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({ resolver: zodResolver(registerSchema) })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await authService.register(data)
      setSent(true)
    } catch (error) {
      toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
    }
  }

  return (
    <AuthLayout
      title="Criar conta"
      subtitle="Preencha os dados para começar a usar o Papo Dev Web."
      footer={
        <Text color="whiteAlpha.700" fontSize="sm">
          Já tem conta?{' '}
          <ChakraLink as={Link} to={ROUTES.LOGIN} color="whatsapp.500" fontWeight="bold">
            Entrar
          </ChakraLink>
        </Text>
      }
    >
      {sent ? (
        <Alert status="success" borderRadius="md" bg="whatsapp.600" color="white">
          <AlertIcon color="white" />
          <Text fontSize="sm">
            Cadastro realizado! Enviamos um link de confirmação para o seu e-mail. Confirme
            em até 24 horas para ativar a sua conta.
          </Text>
        </Alert>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <VStack spacing={4} align="stretch">
            <FormControl isInvalid={!!errors.full_name}>
              <FormLabel color="whiteAlpha.800">Nome completo</FormLabel>
              <Input placeholder="Seu nome completo" {...register('full_name')} />
              <FormErrorMessage>{errors.full_name?.message}</FormErrorMessage>
            </FormControl>

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

            <FormControl isInvalid={!!errors.confirm_password}>
              <FormLabel color="whiteAlpha.800">Repetir senha</FormLabel>
              <Input type="password" placeholder="••••••••" {...register('confirm_password')} />
              <FormErrorMessage>{errors.confirm_password?.message}</FormErrorMessage>
            </FormControl>

            <Button type="submit" variant="whatsapp" isLoading={isSubmitting}>
              Cadastrar
            </Button>
          </VStack>
        </form>
      )}
    </AuthLayout>
  )
}
