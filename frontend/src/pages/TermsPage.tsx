import { Box, Container, Heading, Link, ListItem, Text, UnorderedList, VStack } from '@chakra-ui/react'
import { Link as RouterLink } from 'react-router-dom'

import { RETENTION_DAYS, ROUTES } from '@/lib/constants'

// Página pública de Termos de Uso. Documenta, entre outras regras, a política
// de retenção de histórico (expurgo automático após RETENTION_DAYS dias).
export function TermsPage() {
  return (
    <Box minH="100vh" bg="#0b141a" py={12} px={4}>
      <Container maxW="3xl" bg="#111b21" color="whiteAlpha.900" p={{ base: 6, md: 10 }} rounded="lg">
        <Heading size="lg" mb={2} color="white">
          Termos de Uso — Papo Dev Web
        </Heading>
        <Text color="whiteAlpha.600" fontSize="sm" mb={8}>
          Ao usar a plataforma, você concorda com os termos abaixo.
        </Text>

        <VStack spacing={6} align="stretch">
          <Box>
            <Heading size="md" mb={2} color="white">
              1. Uso da plataforma
            </Heading>
            <Text color="whiteAlpha.800">
              O Papo Dev Web é uma plataforma de mensagens para fins de estudo e demonstração.
              Você é responsável pelo conteúdo que envia e por manter suas credenciais seguras.
            </Text>
          </Box>

          <Box>
            <Heading size="md" mb={2} color="white">
              2. Retenção de histórico e mídias
            </Heading>
            <Text color="whiteAlpha.800" mb={2}>
              Para preservar privacidade e otimizar recursos, mantemos de forma global apenas os
              últimos <strong>{RETENTION_DAYS} dias</strong> de histórico. Após esse período, os
              dados são excluídos automaticamente:
            </Text>
            <UnorderedList color="whiteAlpha.800" spacing={1} pl={4}>
              <ListItem>
                Mensagens com mais de {RETENTION_DAYS} dias são apagadas permanentemente.
              </ListItem>
              <ListItem>
                Objetos/mídias (imagens, vídeos, áudios e documentos) dessas mensagens são
                removidos do armazenamento.
              </ListItem>
              <ListItem>
                Conversas sem atividade por mais de {RETENTION_DAYS} dias são excluídas por
                completo.
              </ListItem>
            </UnorderedList>
            <Text color="whiteAlpha.600" fontSize="sm" mt={2}>
              A limpeza é executada automaticamente todos os dias às 00:01. A exclusão é
              irreversível.
            </Text>
          </Box>

          <Box>
            <Heading size="md" mb={2} color="white">
              3. Privacidade
            </Heading>
            <Text color="whiteAlpha.800">
              Coletamos apenas os dados necessários para o funcionamento do serviço (cadastro e
              mensagens). Não compartilhamos seus dados com terceiros.
            </Text>
          </Box>
        </VStack>

        <Box mt={10}>
          <Link as={RouterLink} to={ROUTES.LOGIN} color="whatsapp.300">
            ← Voltar para o início
          </Link>
        </Box>
      </Container>
    </Box>
  )
}
