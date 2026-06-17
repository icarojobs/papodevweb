import { Box, Flex, Heading, Image, Text, VStack } from '@chakra-ui/react'
import type { ReactNode } from 'react'

interface AuthLayoutProps {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}

// Layout compartilhado das telas de login/cadastro, no visual do WhatsApp Web.
export function AuthLayout({ title, subtitle, children, footer }: AuthLayoutProps) {
  return (
    <Flex minH="100vh" align="center" justify="center" bg="#0b141a" px={4}>
      <Box w="100%" maxW="420px">
        <Flex justify="center" mb={5}>
          <Image src="/logo.svg" alt="Papo Dev Web" h="56px" />
        </Flex>
        <Box h="6px" bg="whatsapp.600" borderTopRadius="md" />
        <Box bg="#111b21" p={8} borderBottomRadius="md" boxShadow="lg">
          <VStack spacing={2} align="stretch" mb={6}>
            <Heading size="lg" color="white">
              {title}
            </Heading>
            <Text color="whiteAlpha.700" fontSize="sm">
              {subtitle}
            </Text>
          </VStack>
          {children}
          <Box mt={6} textAlign="center">
            {footer}
          </Box>
        </Box>
      </Box>
    </Flex>
  )
}
