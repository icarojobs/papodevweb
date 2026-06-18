import {
  Box,
  Flex,
  Icon,
  IconButton,
  Image,
  Link,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Portal,
  Text,
  useDisclosure,
} from '@chakra-ui/react'
import { BsCheck, BsCheckAll, BsChevronDown } from 'react-icons/bs'
import { FiFileText, FiTrash2 } from 'react-icons/fi'

import { MESSAGE_DELETED_TEXT } from '@/lib/constants'
import { useChatStore } from '@/store/chat.store'
import type { Message } from '@/types/chat'
import { formatFileSize, formatMessageTime } from '../format'
import { WA } from '../ui'
import { ImageViewerModal } from './ImageViewerModal'

const READ_TICK_COLOR = '#53bdeb'

function StatusTicks({ message }: { message: Message }) {
  if (message.status === 'sent') {
    return <Icon as={BsCheck} boxSize={4} color={WA.textMuted} aria-label="Enviada" />
  }
  const isRead = message.status === 'read'
  return (
    <Icon
      as={BsCheckAll}
      boxSize={4}
      color={isRead ? READ_TICK_COLOR : WA.textMuted}
      aria-label={isRead ? 'Lida' : 'Entregue'}
    />
  )
}

function MediaContent({ message }: { message: Message }) {
  const viewer = useDisclosure()
  const media = message.media
  if (!media) return null
  if (message.type === 'image') {
    return (
      <>
        <Image
          src={media.url}
          alt={media.name}
          maxW="280px"
          rounded="md"
          mb={1}
          cursor="pointer"
          onClick={viewer.onOpen}
        />
        <ImageViewerModal
          src={media.url}
          alt={media.name}
          isOpen={viewer.isOpen}
          onClose={viewer.onClose}
        />
      </>
    )
  }
  if (message.type === 'video') {
    return (
      <Box as="video" controls src={media.url} maxW="280px" rounded="md" mb={1} aria-label="Vídeo">
        <track kind="captions" />
      </Box>
    )
  }
  if (message.type === 'audio') {
    return (
      <Box as="audio" controls src={media.url} maxW="280px" mb={1} aria-label="Áudio">
        <track kind="captions" />
      </Box>
    )
  }
  return (
    <Link href={media.url} isExternal _hover={{ textDecoration: 'none' }}>
      <Flex align="center" gap={2} bg={WA.searchBg} rounded="md" px={3} py={2} mb={1} minW="200px">
        <Icon as={FiFileText} boxSize={6} color={WA.greenDark} />
        <Box minW={0}>
          <Text fontSize="sm" color={WA.textPrimary} noOfLines={1}>
            {media.name}
          </Text>
          <Text fontSize="xs" color={WA.textSecondary}>
            {formatFileSize(media.size)}
          </Text>
        </Box>
      </Flex>
    </Link>
  )
}

interface MessageBubbleProps {
  conversationId: string
  message: Message
  mine: boolean
  senderName?: string
}

export function MessageBubble({ conversationId, message, mine, senderName }: MessageBubbleProps) {
  const deleteMessage = useChatStore((s) => s.deleteMessage)
  const canDeleteForEveryone = mine && !message.deleted

  return (
    <Flex justify={mine ? 'flex-end' : 'flex-start'} px={{ base: 4, md: 12 }} mb={1}>
      <Box
        role="group"
        position="relative"
        bg={mine ? WA.bubbleOut : WA.bubbleIn}
        rounded="lg"
        borderTopRightRadius={mine ? 'sm' : 'lg'}
        borderTopLeftRadius={mine ? 'lg' : 'sm'}
        px={3}
        py={2}
        maxW="65%"
        boxShadow="0 1px 0.5px rgba(0,0,0,0.13)"
      >
        {!message.deleted && (
          <Menu placement="bottom-end" isLazy>
            <MenuButton
              as={IconButton}
              aria-label="Opções da mensagem"
              icon={<Icon as={BsChevronDown} boxSize={4} />}
              size="xs"
              variant="ghost"
              position="absolute"
              top={1}
              right={1}
              minW="auto"
              h="auto"
              opacity={0}
              _groupHover={{ opacity: 1 }}
              color={WA.textSecondary}
            />
            <Portal>
              <MenuList zIndex="dropdown" minW="180px">
                <MenuItem
                  icon={<Icon as={FiTrash2} />}
                  onClick={() => deleteMessage(conversationId, message.id, 'me')}
                >
                  Apagar para mim
                </MenuItem>
                {canDeleteForEveryone && (
                  <MenuItem
                    icon={<Icon as={FiTrash2} />}
                    color={WA.danger}
                    onClick={() => deleteMessage(conversationId, message.id, 'everyone')}
                  >
                    Apagar para todos
                  </MenuItem>
                )}
              </MenuList>
            </Portal>
          </Menu>
        )}

        {!mine && senderName && !message.deleted && (
          <Text fontSize="xs" fontWeight="bold" color={WA.greenDark} mb={0.5}>
            {senderName}
          </Text>
        )}

        {message.deleted ? (
          <Flex align="center" gap={1}>
            <Text fontSize="sm" fontStyle="italic" color={WA.textMuted}>
              {MESSAGE_DELETED_TEXT}
            </Text>
          </Flex>
        ) : (
          <>
            <MediaContent message={message} />
            {message.text && (
              <Text fontSize="sm" color={WA.textPrimary} whiteSpace="pre-wrap">
                {message.text}
              </Text>
            )}
          </>
        )}

        <Flex align="center" justify="flex-end" gap={1} mt={1}>
          <Text fontSize="10px" color={WA.textMuted}>
            {formatMessageTime(message.created_at)}
          </Text>
          {mine && !message.deleted && <StatusTicks message={message} />}
        </Flex>
      </Box>
    </Flex>
  )
}
