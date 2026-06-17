import { Box, Flex, Icon, IconButton, Input, InputGroup, InputLeftElement, Text } from '@chakra-ui/react'
import { FiPlusCircle, FiSearch } from 'react-icons/fi'

import { ListRow } from '../components/ListRow'
import { CHANNELS } from '../data/mock'
import { WA } from '../ui'

function UnreadBadge({ count }: { count: number }) {
  return (
    <Flex minW="20px" h="20px" px="6px" rounded="full" bg={WA.unread} color="white" fontSize="12px" fontWeight="medium" align="center" justify="center" flexShrink={0}>
      {count > 999 ? '999+' : count}
    </Flex>
  )
}

export function ChannelsPanel() {
  return (
    <Flex direction="column" h="100%" bg={WA.panelBg}>
      <Flex align="center" justify="space-between" px={5} py={4}>
        <Text fontSize="2xl" fontWeight="semibold" color={WA.textPrimary}>
          Channels
        </Text>
        <IconButton aria-label="Descobrir canais" icon={<Icon as={FiPlusCircle} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
      </Flex>

      <Box px={3} pb={2}>
        <InputGroup size="sm">
          <InputLeftElement pointerEvents="none" h="35px">
            <Icon as={FiSearch} color={WA.textSecondary} />
          </InputLeftElement>
          <Input placeholder="Search" bg={WA.searchBg} border="none" rounded="lg" h="35px" pl="40px" _focus={{ bg: WA.searchBg, boxShadow: 'none' }} />
        </InputGroup>
      </Box>

      <Box overflowY="auto" flex="1">
        {CHANNELS.map((c) => (
          <ListRow
            key={c.id}
            name={c.name}
            preview={c.preview}
            time={c.time}
            timeColor={c.unread ? WA.green : undefined}
            trailing={c.unread ? <UnreadBadge count={c.unread} /> : undefined}
          />
        ))}
        <Text px={5} py={4} fontSize="sm" color={WA.green} fontWeight="medium" cursor="pointer">
          Find channels to follow
        </Text>
      </Box>
    </Flex>
  )
}
