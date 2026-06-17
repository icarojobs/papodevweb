import { Flex, Text, VStack } from '@chakra-ui/react'
import type { ReactNode } from 'react'

import { WA } from '../ui'

interface EmptyStateProps {
  icon: ReactNode
  title: string
  subtitle: string
  footer?: ReactNode
}

// Estado vazio do painel direito (ícone grande, título e descrição centralizados).
export function EmptyState({ icon, title, subtitle, footer }: EmptyStateProps) {
  return (
    <Flex direction="column" h="100%" align="center" justify="center" bg={WA.rightBg} px={8} position="relative">
      <VStack spacing={5} maxW="480px" textAlign="center">
        {icon}
        <Text fontSize="3xl" fontWeight="light" color={WA.textPrimary}>
          {title}
        </Text>
        <Text fontSize="sm" color={WA.textSecondary}>
          {subtitle}
        </Text>
      </VStack>
      {footer && (
        <Flex position="absolute" bottom={8} align="center" gap={2}>
          {footer}
        </Flex>
      )}
    </Flex>
  )
}
