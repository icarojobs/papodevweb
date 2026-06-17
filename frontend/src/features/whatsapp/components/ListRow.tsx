import { Avatar, Box, Flex, Text } from '@chakra-ui/react'
import type { ReactNode } from 'react'

import { WA } from '../ui'

interface ListRowProps {
  name: string
  avatarName?: string
  avatarRing?: 'unviewed' | 'viewed' | 'none'
  title?: ReactNode
  preview?: ReactNode
  time?: string
  timeColor?: string
  trailing?: ReactNode
  active?: boolean
  onClick?: () => void
}

// Linha genérica de lista (conversa, status, canal): avatar + título + prévia + meta.
export function ListRow({
  name,
  avatarName,
  avatarRing = 'none',
  preview,
  time,
  timeColor,
  trailing,
  active,
  onClick,
}: ListRowProps) {
  const ringProps =
    avatarRing === 'none'
      ? {}
      : {
          p: '2px',
          border: '2px solid',
          borderColor: avatarRing === 'unviewed' ? WA.green : '#c4cdd3',
          rounded: 'full',
        }

  return (
    <Flex
      align="center"
      gap={3}
      px={3}
      py="10px"
      cursor="pointer"
      bg={active ? WA.active : 'transparent'}
      _hover={{ bg: active ? WA.active : WA.hover }}
      onClick={onClick}
    >
      <Box {...ringProps} flexShrink={0}>
        <Avatar size="md" name={avatarName ?? name} />
      </Box>
      <Box flex="1" minW={0} borderBottom={`1px solid ${WA.divider}`} pb="10px" mt="10px" mb="-10px">
        <Flex justify="space-between" align="baseline" gap={2}>
          <Text fontSize="md" color={WA.textPrimary} noOfLines={1} fontWeight="normal">
            {name}
          </Text>
          {time && (
            <Text fontSize="xs" color={timeColor ?? WA.textSecondary} flexShrink={0}>
              {time}
            </Text>
          )}
        </Flex>
        <Flex justify="space-between" align="center" gap={2} mt="2px">
          <Box fontSize="sm" color={WA.textSecondary} noOfLines={1} flex="1" minW={0}>
            {preview}
          </Box>
          {trailing}
        </Flex>
      </Box>
    </Flex>
  )
}
