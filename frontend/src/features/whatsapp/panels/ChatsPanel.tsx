import {
  Box,
  Flex,
  Icon,
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  Text,
  useDisclosure,
} from '@chakra-ui/react'
import { useEffect } from 'react'
import { BsThreeDotsVertical } from 'react-icons/bs'
import { FiSearch } from 'react-icons/fi'
import { LuMessageSquarePlus } from 'react-icons/lu'
import { TbStarFilled } from 'react-icons/tb'

import { CHAT_FILTERS } from '@/lib/constants'
import { filterConversations, useChatStore } from '@/store/chat.store'
import type { ChatFilter, Conversation } from '@/types/chat'
import { ListRow } from '../components/ListRow'
import { NewChatModal } from '../conversation/NewChatModal'
import { formatListTime } from '../format'
import { WA } from '../ui'

function UnreadBadge({ count }: { count: number }) {
  return (
    <Flex
      minW="20px"
      h="20px"
      px="6px"
      rounded="full"
      bg={WA.unread}
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

function filterCount(conversations: Conversation[], key: ChatFilter): number {
  if (key === 'unread') return conversations.filter((c) => c.unread > 0).length
  if (key === 'favourites') return conversations.filter((c) => c.favourite).length
  if (key === 'groups') return conversations.filter((c) => c.type === 'group').length
  return 0
}

export function ChatsPanel() {
  const conversations = useChatStore((s) => s.conversations)
  const filter = useChatStore((s) => s.filter)
  const search = useChatStore((s) => s.search)
  const activeId = useChatStore((s) => s.activeConversationId)
  const userResults = useChatStore((s) => s.userResults)
  const setFilter = useChatStore((s) => s.setFilter)
  const setSearch = useChatStore((s) => s.setSearch)
  const searchUsers = useChatStore((s) => s.searchUsers)
  const selectConversation = useChatStore((s) => s.selectConversation)
  const startConversation = useChatStore((s) => s.startConversation)
  const newChat = useDisclosure()

  const visible = filterConversations(conversations, filter, search)
  const term = search.trim()

  // Busca usuários cadastrados (debounce) para iniciar novas conversas.
  useEffect(() => {
    const handle = setTimeout(() => searchUsers(search), 250)
    return () => clearTimeout(handle)
  }, [search, searchUsers])

  return (
    <Flex direction="column" h="100%" bg={WA.panelBg}>
      <Flex align="center" justify="space-between" px={5} py={3}>
        <Text fontSize="2xl" fontWeight="bold" color={WA.greenTitle}>
          Papo Dev Web
        </Text>
        <Flex align="center" gap={1}>
          <IconButton
            aria-label="Nova conversa"
            icon={<Icon as={LuMessageSquarePlus} boxSize={5} />}
            variant="ghost"
            rounded="full"
            color={WA.textSecondary}
            onClick={newChat.onOpen}
          />
          <IconButton
            aria-label="Menu"
            icon={<Icon as={BsThreeDotsVertical} boxSize={5} />}
            variant="ghost"
            rounded="full"
            color={WA.textSecondary}
          />
        </Flex>
      </Flex>

      <Box px={3} pb={2}>
        <InputGroup size="sm">
          <InputLeftElement pointerEvents="none" h="35px">
            <Icon as={FiSearch} color={WA.textSecondary} />
          </InputLeftElement>
          <Input
            aria-label="Buscar conversas"
            placeholder="Pesquisar ou começar uma nova conversa"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            bg={WA.searchBg}
            border="none"
            rounded="lg"
            h="35px"
            pl="40px"
            _focus={{ bg: WA.searchBg, boxShadow: 'none' }}
          />
        </InputGroup>
      </Box>

      <Flex px={3} pb={2} gap={2} wrap="nowrap" overflowX="auto">
        {CHAT_FILTERS.map(({ key, label }) => {
          const isActive = key === filter
          const count = filterCount(conversations, key)
          return (
            <Box
              as="button"
              key={key}
              aria-pressed={isActive}
              flexShrink={0}
              rounded="full"
              px={3}
              h="30px"
              fontSize="sm"
              bg={isActive ? '#d9fdd3' : WA.searchBg}
              color={isActive ? WA.greenDark : WA.textSecondary}
              _hover={{ bg: isActive ? '#cdf5c5' : '#e6e9eb' }}
              onClick={() => setFilter(key)}
            >
              {label}
              {count > 0 ? ` ${count}` : ''}
            </Box>
          )
        })}
      </Flex>

      <Box overflowY="auto" flex="1">
        {visible.length === 0 && userResults.length === 0 && (
          <Text fontSize="sm" color={WA.textSecondary} textAlign="center" py={6}>
            {term ? 'Nada encontrado.' : 'Nenhuma conversa por aqui ainda.'}
          </Text>
        )}
        {term && (
          <Text px={5} pt={3} pb={1} fontSize="sm" color={WA.green} fontWeight="medium">
            Conversas
          </Text>
        )}
        {visible.map((conversation) => (
          <ListRow
            key={conversation.id}
            name={conversation.name}
            preview={conversation.last_message?.text ?? 'Toque para conversar'}
            time={formatListTime(conversation.last_message?.created_at ?? conversation.updated_at)}
            timeColor={conversation.unread > 0 ? WA.green : undefined}
            active={conversation.id === activeId}
            onClick={() => selectConversation(conversation.id)}
            trailing={
              <Flex align="center" gap={1} flexShrink={0}>
                {conversation.favourite && (
                  <Icon as={TbStarFilled} boxSize={4} color={WA.textMuted} aria-label="Favorita" />
                )}
                {conversation.unread > 0 ? <UnreadBadge count={conversation.unread} /> : null}
              </Flex>
            }
          />
        ))}

        {term && userResults.length > 0 && (
          <>
            <Text px={5} pt={3} pb={1} fontSize="sm" color={WA.green} fontWeight="medium">
              Contatos
            </Text>
            {userResults.map((user) => (
              <ListRow
                key={user.id}
                name={user.full_name}
                preview={user.email}
                onClick={() => startConversation(user.id)}
              />
            ))}
          </>
        )}
      </Box>

      <NewChatModal isOpen={newChat.isOpen} onClose={newChat.onClose} />
    </Flex>
  )
}
