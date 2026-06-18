import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  Heading,
  HStack,
  Icon,
  Image,
  Link,
  SimpleGrid,
  Stack,
  Text,
} from '@chakra-ui/react'
import type { IconType } from 'react-icons'
import { BsDiscord, BsSlack, BsTelegram, BsWhatsapp } from 'react-icons/bs'
import { FiGithub, FiLock, FiSearch, FiTrash2, FiUsers, FiZap } from 'react-icons/fi'
import { Link as RouterLink } from 'react-router-dom'

import { ROUTES } from '@/lib/constants'
import { useAuthStore } from '@/store/auth.store'

const BG = '#0b141a'
const PANEL = '#111b21'
const ACCENT = '#25d366'

interface Pillar {
  icon: IconType
  name: string
  best: string
  color: string
}

const PILLARS: Pillar[] = [
  { icon: BsWhatsapp, name: 'WhatsApp', best: 'simplicidade e mensagens em tempo real', color: '#25d366' },
  { icon: BsSlack, name: 'Slack', best: 'organização por times e produtividade', color: '#e01e5a' },
  { icon: BsTelegram, name: 'Telegram', best: 'velocidade, canais e mídia leve', color: '#29a9eb' },
  { icon: BsDiscord, name: 'Discord', best: 'comunidades e presença em tempo real', color: '#5865f2' },
]

interface Feature {
  icon: IconType
  title: string
  description: string
}

const FEATURES: Feature[] = [
  { icon: FiZap, title: 'Tempo real', description: 'Mensagens, recibos de entrega/leitura, presença e digitação instantâneos via WebSocket.' },
  { icon: FiUsers, title: 'Diretas e grupos', description: 'Converse 1-a-1 ou crie grupos. Encontre pessoas por nome ou e-mail.' },
  { icon: FiSearch, title: 'Busca e filtros', description: 'Filtre por não lidas, favoritas e grupos. Encontre conversas e contatos num só campo.' },
  { icon: FiLock, title: 'Privacidade', description: 'Apague mensagens para você ou para todos. Controle total sobre o seu histórico.' },
  { icon: FiTrash2, title: 'Retenção inteligente', description: 'Histórico e mídias mantidos por 7 dias e expurgados automaticamente.' },
  { icon: FiGithub, title: '100% open source', description: 'Gratuito e de código aberto. Construído para a comunidade de tecnologia.' },
]

function Brand() {
  return (
    <HStack spacing={3}>
      <Image src="/logo.svg" alt="Papo Dev Web" h="32px" />
    </HStack>
  )
}

export function LandingPage() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  const primaryCta = isAuthenticated ? (
    <Button as={RouterLink} to={ROUTES.CHAT} size="lg" bg={ACCENT} color="#0b141a" _hover={{ bg: '#1fbf59' }}>
      Abrir o chat
    </Button>
  ) : (
    <Button as={RouterLink} to={ROUTES.REGISTER} size="lg" bg={ACCENT} color="#0b141a" _hover={{ bg: '#1fbf59' }}>
      Criar conta grátis
    </Button>
  )

  return (
    <Box bg={BG} color="whiteAlpha.900" minH="100vh">
      {/* Cabeçalho */}
      <Box as="header" borderBottom="1px solid" borderColor="whiteAlpha.200">
        <Container maxW="6xl">
          <Flex as="nav" py={4} align="center" justify="space-between">
            <Brand />
            <HStack spacing={3}>
              {isAuthenticated ? (
                <Button as={RouterLink} to={ROUTES.CHAT} variant="outline" colorScheme="whiteAlpha">
                  Abrir o chat
                </Button>
              ) : (
                <>
                  <Button as={RouterLink} to={ROUTES.LOGIN} variant="ghost" color="whiteAlpha.900">
                    Entrar
                  </Button>
                  <Button as={RouterLink} to={ROUTES.REGISTER} bg={ACCENT} color="#0b141a" _hover={{ bg: '#1fbf59' }}>
                    Começar
                  </Button>
                </>
              )}
            </HStack>
          </Flex>
        </Container>
      </Box>

      <Box as="main">
        {/* Hero */}
        <Container as="section" maxW="5xl" py={{ base: 16, md: 24 }} textAlign="center">
          <Badge colorScheme="green" variant="subtle" rounded="full" px={3} py={1} mb={6} fontSize="xs">
            🚀 Grátis e open source
          </Badge>
          <Heading
            as="h1"
            fontSize={{ base: '3xl', md: '6xl' }}
            lineHeight="1.05"
            letterSpacing="-0.02em"
            bgGradient="linear(to-r, #25d366, #29a9eb)"
            bgClip="text"
          >
            Toda a sua comunicação. Um só lugar.
          </Heading>
          <Text fontSize={{ base: 'lg', md: '2xl' }} color="whiteAlpha.700" mt={6} maxW="3xl" mx="auto">
            O melhor do WhatsApp, Slack, Telegram e Discord reunido em uma única plataforma —
            pensada para profissionais de tecnologia. 100% gratuita e de código aberto.
          </Text>
          <Stack direction={{ base: 'column', sm: 'row' }} spacing={4} justify="center" mt={10}>
            {primaryCta}
            <Button
              as={RouterLink}
              to={isAuthenticated ? ROUTES.CHAT : ROUTES.LOGIN}
              size="lg"
              variant="outline"
              colorScheme="whiteAlpha"
            >
              {isAuthenticated ? 'Ir para conversas' : 'Já tenho conta'}
            </Button>
          </Stack>
        </Container>

        {/* Pilares: o melhor de cada um */}
        <Box as="section" bg={PANEL} py={{ base: 16, md: 20 }}>
          <Container maxW="6xl">
            <Heading as="h2" size="xl" textAlign="center" mb={3}>
              O melhor de cada mundo
            </Heading>
            <Text textAlign="center" color="whiteAlpha.700" maxW="2xl" mx="auto" mb={12}>
              Reunimos as melhores ideias dos apps que você já conhece — sem precisar de quatro
              ferramentas diferentes.
            </Text>
            <SimpleGrid columns={{ base: 1, sm: 2, lg: 4 }} spacing={6}>
              {PILLARS.map((pillar) => (
                <Box
                  key={pillar.name}
                  bg={BG}
                  border="1px solid"
                  borderColor="whiteAlpha.200"
                  rounded="xl"
                  p={6}
                >
                  <Icon as={pillar.icon} boxSize={9} color={pillar.color} mb={4} />
                  <Heading as="h3" size="md" mb={2}>
                    {pillar.name}
                  </Heading>
                  <Text color="whiteAlpha.700" fontSize="sm">
                    {pillar.best}
                  </Text>
                </Box>
              ))}
            </SimpleGrid>
          </Container>
        </Box>

        {/* Recursos */}
        <Container as="section" maxW="6xl" py={{ base: 16, md: 20 }}>
          <Heading as="h2" size="xl" textAlign="center" mb={12}>
            Recursos que você espera — e mais
          </Heading>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={6}>
            {FEATURES.map((feature) => (
              <Box
                key={feature.title}
                border="1px solid"
                borderColor="whiteAlpha.200"
                rounded="xl"
                p={6}
                _hover={{ borderColor: ACCENT, transform: 'translateY(-2px)' }}
                transition="all 0.2s"
              >
                <Icon as={feature.icon} boxSize={7} color={ACCENT} mb={4} />
                <Heading as="h3" size="md" mb={2}>
                  {feature.title}
                </Heading>
                <Text color="whiteAlpha.700" fontSize="sm">
                  {feature.description}
                </Text>
              </Box>
            ))}
          </Grid>
        </Container>

        {/* Chamada final */}
        <Box as="section" bg={PANEL} py={{ base: 16, md: 20 }}>
          <Container maxW="3xl" textAlign="center">
            <Heading as="h2" size="xl" mb={4}>
              Pronto para conversar?
            </Heading>
            <Text color="whiteAlpha.700" mb={8}>
              Crie sua conta gratuita em segundos e comece a usar agora mesmo.
            </Text>
            {primaryCta}
          </Container>
        </Box>
      </Box>

      {/* Rodapé */}
      <Box as="footer" borderTop="1px solid" borderColor="whiteAlpha.200" py={8}>
        <Container maxW="6xl">
          <Flex direction={{ base: 'column', md: 'row' }} align="center" justify="space-between" gap={4}>
            <Text color="whiteAlpha.600" fontSize="sm">
              © Papo Dev Web — gratuito e open source.
            </Text>
            <HStack spacing={6} fontSize="sm">
              <Link as={RouterLink} to={ROUTES.TERMS} color="whiteAlpha.700">
                Termos de Uso
              </Link>
              <Link as={RouterLink} to={ROUTES.LOGIN} color="whiteAlpha.700">
                Entrar
              </Link>
            </HStack>
          </Flex>
        </Container>
      </Box>
    </Box>
  )
}
