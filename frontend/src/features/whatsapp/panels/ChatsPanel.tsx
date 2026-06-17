import {
  Box,
  Button,
  CloseButton,
  Flex,
  Icon,
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  Text,
} from '@chakra-ui/react'
import { useState } from 'react'
import { BsThreeDotsVertical } from 'react-icons/bs'
import { FiSearch } from 'react-icons/fi'
import { HiOutlineBellSlash } from 'react-icons/hi2'
import { MdOutlineArchive } from 'react-icons/md'
import { TbPinnedFilled } from 'react-icons/tb'
import { LuMessageSquarePlus } from 'react-icons/lu'

import { ListRow } from '../components/ListRow'
import { CONVERSATIONS, type Conversation } from '../data/mock'
import { WA } from '../ui'

const FILTERS = ['All', 'Unread 32', 'Favourites 1', 'Groups 13'] as const

function UnreadBadge({ count, muted }: { count: number; muted?: boolean }) {
  return (
    <Flex
      minW="20px"
      h="20px"
      px="6px"
      rounded="full"
      bg={muted ? WA.textMuted : WA.unread}
      color="white"
      fontSize="12px"
      fontWeight="medium"
      align="center"
      justify="center"
    >
      {count > 999 ? '999+' : count}
    </Flex>
  )
}

interface ChatsPanelProps {
  selectedId?: string
  onSelectChat: (conversation: Conversation) => void
}

export function ChatsPanel({ selectedId, onSelectChat }: ChatsPanelProps) {
  const [activeFilter, setActiveFilter] = useState('All')
  const [bannerVisible, setBannerVisible] = useState(true)

  return (
    <Flex direction="column" h="100%" bg={WA.panelBg}>
      {/* Header */}
      <Flex align="center" justify="space-between" px={5} py={3}>
        <Text fontSize="2xl" fontWeight="bold" color={WA.greenTitle}>
          WhatsApp
        </Text>
        <Flex align="center" gap={1}>
          <IconButton aria-label="Nova conversa" icon={<Icon as={LuMessageSquarePlus} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
          <IconButton aria-label="Menu" icon={<Icon as={BsThreeDotsVertical} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
        </Flex>
      </Flex>

      {/* Search */}
      <Box px={3} pb={2}>
        <InputGroup size="sm">
          <InputLeftElement pointerEvents="none" h="35px">
            <Icon as={FiSearch} color={WA.textSecondary} />
          </InputLeftElement>
          <Input placeholder="Search or start a new chat" bg={WA.searchBg} border="none" rounded="lg" h="35px" pl="40px" _focus={{ bg: WA.searchBg, boxShadow: 'none' }} />
        </InputGroup>
      </Box>

      {/* Filtros */}
      <Flex px={3} pb={2} gap={2} wrap="nowrap" overflowX="auto">
        {FILTERS.map((f) => {
          const isActive = f === activeFilter
          return (
            <Button
              key={f}
              size="xs"
              rounded="full"
              px={3}
              h="30px"
              flexShrink={0}
              fontWeight="normal"
              bg={isActive ? '#d9fdd3' : WA.searchBg}
              color={isActive ? WA.greenDark : WA.textSecondary}
              _hover={{ bg: isActive ? '#cdf5c5' : '#e6e9eb' }}
              onClick={() => setActiveFilter(f)}
            >
              {f}
            </Button>
          )
        })}
      </Flex>

      <Box overflowY="auto" flex="1">
        {/* Banner de notificações */}
        {bannerVisible && (
          <Flex align="center" gap={3} mx={3} my={2} px={3} py={2} bg="#e7f8ec" rounded="lg">
            <Icon as={HiOutlineBellSlash} boxSize={5} color={WA.greenDark} />
            <Text fontSize="sm" color={WA.textPrimary} flex="1">
              Message notifications are off.{' '}
              <Text as="span" color={WA.greenDark} fontWeight="medium" cursor="pointer">
                Turn on
              </Text>
            </Text>
            <CloseButton size="sm" onClick={() => setBannerVisible(false)} />
          </Flex>
        )}

        {/* Arquivadas */}
        <Flex align="center" gap={4} px={5} py={3} cursor="pointer" _hover={{ bg: WA.hover }}>
          <Icon as={MdOutlineArchive} boxSize={5} color={WA.green} />
          <Text fontSize="sm" color={WA.textPrimary} flex="1">
            Archived
          </Text>
          <Text fontSize="xs" color={WA.textSecondary}>
            19
          </Text>
        </Flex>

        {/* Lista de conversas */}
        {CONVERSATIONS.map((c) => (
          <ListRow
            key={c.id}
            name={c.name}
            preview={c.preview}
            time={c.time}
            timeColor={c.unread ? WA.green : undefined}
            active={c.id === selectedId}
            onClick={() => onSelectChat(c)}
            trailing={
              <Flex align="center" gap={1} flexShrink={0}>
                {c.muted && <Icon as={HiOutlineBellSlash} boxSize={4} color={WA.textMuted} />}
                {c.pinned && <Icon as={TbPinnedFilled} boxSize={4} color={WA.textMuted} />}
                {c.unread ? <UnreadBadge count={c.unread} muted={c.muted} /> : null}
              </Flex>
            }
          />
        ))}
      </Box>
    </Flex>
  )
}
