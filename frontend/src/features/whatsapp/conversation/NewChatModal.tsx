import {
  Avatar,
  Box,
  Button,
  Flex,
  Icon,
  Input,
  LightMode,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Tag,
  TagCloseButton,
  TagLabel,
  Text,
} from '@chakra-ui/react'
import { useState } from 'react'
import { HiOutlineUserGroup } from 'react-icons/hi2'

import { chatService } from '@/services/chat.service'
import { useChatStore } from '@/store/chat.store'
import type { ChatUser } from '@/types/chat'
import { WA } from '../ui'

interface NewChatModalProps {
  isOpen: boolean
  onClose: () => void
}

export function NewChatModal({ isOpen, onClose }: NewChatModalProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<ChatUser[]>([])
  const [groupMode, setGroupMode] = useState(false)
  const [selected, setSelected] = useState<ChatUser[]>([])
  const [groupName, setGroupName] = useState('')
  const startConversation = useChatStore((s) => s.startConversation)
  const startGroup = useChatStore((s) => s.startGroup)

  const reset = () => {
    setQuery('')
    setResults([])
    setGroupMode(false)
    setSelected([])
    setGroupName('')
  }

  const close = () => {
    reset()
    onClose()
  }

  const search = async (value: string) => {
    setQuery(value)
    if (!value.trim()) {
      setResults([])
      return
    }
    setResults(await chatService.searchUsers(value.trim()))
  }

  const pickUser = async (user: ChatUser) => {
    if (groupMode) {
      setSelected((current) =>
        current.some((item) => item.id === user.id) ? current : [...current, user],
      )
      return
    }
    await startConversation(user.id)
    close()
  }

  const createGroup = async () => {
    if (!groupName.trim() || selected.length === 0) return
    await startGroup(groupName.trim(), selected.map((user) => user.id))
    close()
  }

  return (
    <Modal isOpen={isOpen} onClose={close} isCentered>
      <LightMode>
        <ModalOverlay />
        <ModalContent bg={WA.panelBg} color={WA.textPrimary}>
        <ModalHeader color={WA.textPrimary}>
          {groupMode ? 'Novo grupo' : 'Nova conversa'}
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          {!groupMode && (
            <Flex
              align="center"
              gap={3}
              mb={3}
              cursor="pointer"
              color={WA.greenDark}
              onClick={() => setGroupMode(true)}
            >
              <Icon as={HiOutlineUserGroup} boxSize={5} />
              <Text fontWeight="medium">Novo grupo</Text>
            </Flex>
          )}

          {groupMode && (
            <Input
              placeholder="Nome do grupo"
              value={groupName}
              onChange={(event) => setGroupName(event.target.value)}
              mb={3}
            />
          )}

          {selected.length > 0 && (
            <Flex wrap="wrap" gap={2} mb={3}>
              {selected.map((user) => (
                <Tag key={user.id} colorScheme="green" rounded="full">
                  <TagLabel>{user.full_name}</TagLabel>
                  <TagCloseButton
                    onClick={() =>
                      setSelected((current) => current.filter((item) => item.id !== user.id))
                    }
                  />
                </Tag>
              ))}
            </Flex>
          )}

          <Input
            placeholder="Buscar por nome ou e-mail"
            value={query}
            onChange={(event) => search(event.target.value)}
            autoFocus
          />

          <Box mt={2} maxH="280px" overflowY="auto">
            {results.length === 0 && query.trim() && (
              <Text fontSize="sm" color={WA.textSecondary} py={3}>
                Nenhum usuário encontrado.
              </Text>
            )}
            {results.map((user) => (
              <Flex
                key={user.id}
                align="center"
                gap={3}
                px={2}
                py={2}
                rounded="md"
                cursor="pointer"
                _hover={{ bg: WA.hover }}
                onClick={() => pickUser(user)}
              >
                <Avatar size="sm" name={user.full_name} />
                <Box minW={0}>
                  <Text color={WA.textPrimary} noOfLines={1}>
                    {user.full_name}
                  </Text>
                  <Text fontSize="xs" color={WA.textSecondary} noOfLines={1}>
                    {user.email}
                  </Text>
                </Box>
              </Flex>
            ))}
          </Box>

          {groupMode && (
            <Button
              mt={4}
              w="100%"
              colorScheme="green"
              bg={WA.green}
              isDisabled={!groupName.trim() || selected.length === 0}
              onClick={createGroup}
            >
              Criar grupo
            </Button>
          )}
        </ModalBody>
        </ModalContent>
      </LightMode>
    </Modal>
  )
}
