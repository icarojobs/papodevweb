import { Avatar, Box, Flex, Icon, IconButton, Text } from '@chakra-ui/react'
import { BsThreeDotsVertical } from 'react-icons/bs'
import { FiPlus } from 'react-icons/fi'

import { ListRow } from '../components/ListRow'
import { STATUSES } from '../data/mock'
import { WA } from '../ui'

interface StatusPanelProps {
  userName: string
}

export function StatusPanel({ userName }: StatusPanelProps) {
  return (
    <Flex direction="column" h="100%" bg={WA.panelBg}>
      <Flex align="center" justify="space-between" px={5} py={4}>
        <Text fontSize="2xl" fontWeight="semibold" color={WA.textPrimary}>
          Status
        </Text>
        <Flex align="center" gap={1}>
          <IconButton aria-label="Menu" icon={<Icon as={BsThreeDotsVertical} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
          <IconButton aria-label="Adicionar status" icon={<Icon as={FiPlus} boxSize={5} />} variant="ghost" rounded="full" border={`1px solid ${WA.border}`} color={WA.textSecondary} />
        </Flex>
      </Flex>

      <Box overflowY="auto" flex="1">
        <Flex align="center" gap={3} px={5} py={2} cursor="pointer" _hover={{ bg: WA.hover }}>
          <Avatar size="md" name={userName} />
          <Box>
            <Text fontSize="md" color={WA.textPrimary}>
              My status
            </Text>
            <Text fontSize="sm" color={WA.textSecondary}>
              Yesterday at 8:31 pm
            </Text>
          </Box>
        </Flex>

        <Text px={5} py={2} fontSize="sm" color={WA.textSecondary}>
          Recent
        </Text>

        {STATUSES.map((s) => (
          <ListRow
            key={s.id}
            name={s.name}
            avatarRing={s.viewed ? 'viewed' : 'unviewed'}
            preview={s.time}
          />
        ))}
      </Box>
    </Flex>
  )
}
