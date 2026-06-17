import { Avatar, Box, Flex, Icon, IconButton, Square, Text } from '@chakra-ui/react'
import { FiPlusCircle } from 'react-icons/fi'
import { HiMiniMegaphone, HiOutlineUserGroup } from 'react-icons/hi2'

import { COMMUNITIES, type CommunityGroup } from '../data/mock'
import { WA } from '../ui'

function GroupRow({ group }: { group: CommunityGroup }) {
  return (
    <Flex align="center" gap={3} pl={5} pr={3} py={2} cursor="pointer" _hover={{ bg: WA.hover }}>
      <Square size="40px" rounded="lg" bg={group.announcement ? '#dcf8c6' : '#e9edef'} color={WA.textSecondary}>
        <Icon as={group.announcement ? HiMiniMegaphone : HiOutlineUserGroup} boxSize={5} color={group.announcement ? WA.greenDark : WA.textSecondary} />
      </Square>
      <Box flex="1" minW={0}>
        <Flex justify="space-between" align="baseline" gap={2}>
          <Text fontSize="md" color={WA.textPrimary} noOfLines={1}>
            {group.label}
          </Text>
          <Text fontSize="xs" color={group.unread ? WA.green : WA.textSecondary} flexShrink={0}>
            {group.time}
          </Text>
        </Flex>
        <Flex justify="space-between" align="center" gap={2}>
          <Text fontSize="sm" color={WA.textSecondary} noOfLines={1} flex="1">
            {group.preview}
          </Text>
          {group.unread ? (
            <Flex minW="20px" h="20px" px="6px" rounded="full" bg={WA.unread} color="white" fontSize="12px" align="center" justify="center" flexShrink={0}>
              {group.unread}
            </Flex>
          ) : null}
        </Flex>
      </Box>
    </Flex>
  )
}

export function CommunitiesPanel() {
  return (
    <Flex direction="column" h="100%" bg={WA.panelBg}>
      <Flex align="center" justify="space-between" px={5} py={4}>
        <Text fontSize="2xl" fontWeight="semibold" color={WA.textPrimary}>
          Communities
        </Text>
        <IconButton aria-label="Nova comunidade" icon={<Icon as={FiPlusCircle} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
      </Flex>

      <Box overflowY="auto" flex="1">
        <Flex align="center" gap={3} px={5} py={3} cursor="pointer" _hover={{ bg: WA.hover }}>
          <Square size="48px" rounded="2xl" bg={WA.green}>
            <Icon as={HiOutlineUserGroup} boxSize={6} color="white" />
          </Square>
          <Text fontSize="md" color={WA.textPrimary}>
            New community
          </Text>
        </Flex>

        {COMMUNITIES.map((community) => (
          <Box key={community.id} mt={2}>
            <Flex align="center" gap={3} px={5} py={2}>
              <Avatar size="md" rounded="2xl" borderRadius="16px" name={community.name} />
              <Text fontSize="md" fontWeight="semibold" color={WA.textPrimary} noOfLines={1}>
                {community.name}
              </Text>
            </Flex>
            {community.groups.map((g) => (
              <GroupRow key={g.label} group={g} />
            ))}
            <Text pl="72px" py={2} fontSize="sm" color={WA.green} fontWeight="medium" cursor="pointer" borderBottom={`1px solid ${WA.divider}`}>
              View all
            </Text>
          </Box>
        ))}

        <Flex align="center" justify="center" gap={2} py={4} fontSize="xs" color={WA.textMuted}>
          🔒 Your personal messages in communities are end-to-end encrypted
        </Flex>
      </Box>
    </Flex>
  )
}
