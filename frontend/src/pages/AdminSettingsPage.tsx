import {
  Badge,
  Box,
  Button,
  Center,
  Container,
  Divider,
  FormControl,
  FormErrorMessage,
  FormHelperText,
  FormLabel,
  Heading,
  HStack,
  Input,
  Spinner,
  Switch,
  Text,
  useToast,
  VStack,
} from '@chakra-ui/react'
import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'

import { getErrorMessage } from '@/lib/errors'
import { emailSettingsSchema, type EmailSettingsFormData } from '@/lib/validation'
import { adminService } from '@/services/admin.service'
import type { EmailSettingsPayload } from '@/types/admin'

const DEFAULT_VALUES: EmailSettingsFormData = {
  host: '',
  port: 587,
  username: '',
  password: '',
  from_email: '',
  from_name: '',
  use_tls: true,
}

export function AdminSettingsPage() {
  const toast = useToast()
  const [loading, setLoading] = useState(true)
  const [passwordSet, setPasswordSet] = useState(false)
  const [testEmail, setTestEmail] = useState('')
  const [sendingTest, setSendingTest] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EmailSettingsFormData>({
    resolver: zodResolver(emailSettingsSchema),
    defaultValues: DEFAULT_VALUES,
  })

  useEffect(() => {
    let active = true
    adminService
      .getEmailSettings()
      .then((settings) => {
        if (!active) return
        setPasswordSet(settings.password_set)
        reset({
          host: settings.host,
          port: settings.port,
          username: settings.username,
          password: '',
          from_email: settings.from_email,
          from_name: settings.from_name,
          use_tls: settings.use_tls,
        })
      })
      .catch((error) => {
        if (active) toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [reset, toast])

  const onSubmit = async (data: EmailSettingsFormData) => {
    const payload: EmailSettingsPayload = {
      host: data.host,
      port: data.port,
      username: data.username,
      from_email: data.from_email,
      from_name: data.from_name,
      use_tls: data.use_tls,
    }
    // Só envia a senha quando preenchida (mantém a atual caso vazia).
    if (data.password) payload.password = data.password

    try {
      const saved = await adminService.updateEmailSettings(payload)
      setPasswordSet(saved.password_set)
      reset({ ...data, password: '' })
      toast({ title: 'Configurações de e-mail salvas.', status: 'success', isClosable: true })
    } catch (error) {
      toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
    }
  }

  const onSendTest = async () => {
    if (!testEmail) {
      toast({ title: 'Informe um e-mail para o teste.', status: 'warning', isClosable: true })
      return
    }
    setSendingTest(true)
    try {
      const response = await adminService.sendTestEmail(testEmail)
      toast({ title: response.message, status: 'success', isClosable: true })
    } catch (error) {
      toast({ title: getErrorMessage(error), status: 'error', isClosable: true })
    } finally {
      setSendingTest(false)
    }
  }

  if (loading) {
    return (
      <Center minH="100vh" bg="#0b141a">
        <Spinner color="green.400" size="xl" thickness="3px" />
      </Center>
    )
  }

  return (
    <Box minH="100vh" bg="#0b141a" py={10} color="whiteAlpha.900">
      <Container maxW="container.md">
        <Heading size="lg" mb={1}>
          Administração — Configurações
        </Heading>
        <Text color="whiteAlpha.700" mb={8}>
          Configure o e-mail de disparo (servidor SMTP) usado para confirmação de conta,
          redefinição de senha e demais notificações.
        </Text>

        <Box as="form" onSubmit={handleSubmit(onSubmit)} noValidate bg="#111b21" p={6} borderRadius="lg">
          <Heading size="md" mb={4}>
            E-mail de disparo (SMTP)
          </Heading>
          <VStack spacing={4} align="stretch">
            <FormControl isInvalid={!!errors.host}>
              <FormLabel>Servidor SMTP</FormLabel>
              <Input placeholder="smtp.seuprovedor.com" {...register('host')} />
              <FormErrorMessage>{errors.host?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.port}>
              <FormLabel>Porta</FormLabel>
              <Input type="number" {...register('port', { valueAsNumber: true })} />
              <FormErrorMessage>{errors.port?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.username}>
              <FormLabel>Usuário</FormLabel>
              <Input placeholder="usuário/login do SMTP" {...register('username')} />
              <FormErrorMessage>{errors.username?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.password}>
              <FormLabel>
                Senha{' '}
                {passwordSet && (
                  <Badge colorScheme="green" ml={2}>
                    configurada
                  </Badge>
                )}
              </FormLabel>
              <Input
                type="password"
                placeholder={passwordSet ? 'Deixe em branco para manter a atual' : 'senha do SMTP'}
                {...register('password')}
              />
              <FormHelperText color="whiteAlpha.600">
                A senha é guardada criptografada e nunca é exibida.
              </FormHelperText>
              <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.from_email}>
              <FormLabel>E-mail do remetente</FormLabel>
              <Input type="email" placeholder="no-reply@seudominio.com" {...register('from_email')} />
              <FormErrorMessage>{errors.from_email?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.from_name}>
              <FormLabel>Nome do remetente</FormLabel>
              <Input placeholder="Papo Dev Web" {...register('from_name')} />
              <FormErrorMessage>{errors.from_name?.message}</FormErrorMessage>
            </FormControl>

            <FormControl display="flex" alignItems="center">
              <FormLabel htmlFor="use_tls" mb={0}>
                Usar STARTTLS
              </FormLabel>
              <Switch id="use_tls" {...register('use_tls')} />
            </FormControl>

            <Button type="submit" variant="whatsapp" isLoading={isSubmitting} alignSelf="flex-start">
              Salvar configurações
            </Button>
          </VStack>
        </Box>

        <Divider my={8} borderColor="whiteAlpha.300" />

        <Box bg="#111b21" p={6} borderRadius="lg">
          <Heading size="md" mb={2}>
            Enviar e-mail de teste
          </Heading>
          <Text color="whiteAlpha.700" mb={4} fontSize="sm">
            Envia uma mensagem de teste com a configuração atual para validar o SMTP.
          </Text>
          <HStack align="flex-end" spacing={3}>
            <FormControl>
              <FormLabel>Enviar para</FormLabel>
              <Input
                type="email"
                placeholder="voce@exemplo.com"
                value={testEmail}
                onChange={(event) => setTestEmail(event.target.value)}
              />
            </FormControl>
            <Button onClick={onSendTest} isLoading={sendingTest} flexShrink={0}>
              Enviar teste
            </Button>
          </HStack>
        </Box>
      </Container>
    </Box>
  )
}
