import { Avatar, Box, Flex, Icon, IconButton, Input, Text, useDisclosure } from '@chakra-ui/react'
import { BsEmojiSmile, BsThreeDotsVertical } from 'react-icons/bs'
import { FiMic, FiPaperclip, FiSearch, FiVideo } from 'react-icons/fi'
import { HiOutlinePhotograph } from 'react-icons/hi'

import type { Conversation } from '../data/mock'
import { SAMPLE_MESSAGES } from '../data/mock'
import { WA } from '../ui'
import { MediaModal } from './MediaModal'

function DatePill({ label }: { label: string }) {
  return (
    <Flex justify="center" my={3}>
      <Box bg="#ffffff" color={WA.textSecondary} fontSize="xs" px={3} py={1} rounded="md" boxShadow="sm">
        {label}
      </Box>
    </Flex>
  )
}

function IncomingBubble({ text, time }: { text: string; time: string }) {
  return (
    <Flex justify="flex-start" px={{ base: 4, md: 12 }} mb={1}>
      <Box bg={WA.bubbleIn} rounded="lg" borderTopLeftRadius="sm" px={3} py={2} maxW="65%" boxShadow="0 1px 0.5px rgba(0,0,0,0.13)">
        <Text fontSize="sm" color={WA.textPrimary}>
          {text}
        </Text>
        <Text fontSize="10px" color={WA.textMuted} textAlign="right" mt={1}>
          {time}
        </Text>
      </Box>
    </Flex>
  )
}

interface ChatViewProps {
  conversation: Conversation
}

export function ChatView({ conversation }: ChatViewProps) {
  const media = useDisclosure()

  return (
    <Flex direction="column" h="100%" bg={WA.chatWallpaper} position="relative">
      {/* Wallpaper sutil */}
      <Box
        position="absolute"
        inset={0}
        opacity={0.4}
        bgImage="radial-gradient(#d6cfc4 0.5px, transparent 0.5px)"
        bgSize="18px 18px"
        pointerEvents="none"
      />

      {/* Header */}
      <Flex align="center" justify="space-between" px={4} py={2} bg={WA.header} borderBottom={`1px solid ${WA.border}`} zIndex={1}>
        <Flex align="center" gap={3} minW={0}>
          <Avatar size="sm" name={conversation.name} />
          <Box minW={0}>
            <Text fontSize="md" color={WA.textPrimary} noOfLines={1}>
              {conversation.name}
            </Text>
            <Text fontSize="xs" color={WA.textSecondary}>
              online
            </Text>
          </Box>
        </Flex>
        <Flex align="center" gap={1} color={WA.textSecondary}>
          <IconButton aria-label="Chamada de vídeo" icon={<Icon as={FiVideo} boxSize={5} />} variant="ghost" rounded="full" />
          <IconButton aria-label="Mídia" icon={<Icon as={HiOutlinePhotograph} boxSize={5} />} variant="ghost" rounded="full" onClick={media.onOpen} />
          <IconButton aria-label="Pesquisar" icon={<Icon as={FiSearch} boxSize={5} />} variant="ghost" rounded="full" />
          <IconButton aria-label="Menu" icon={<Icon as={BsThreeDotsVertical} boxSize={5} />} variant="ghost" rounded="full" />
        </Flex>
      </Flex>

      {/* Mensagens */}
      <Box flex="1" overflowY="auto" py={4} zIndex={1}>
        <DatePill label="Today" />
        {SAMPLE_MESSAGES.map((text, i) => (
          <IncomingBubble key={i} text={text} time={`10:0${i}`} />
        ))}
      </Box>

      {/* Barra de digitação */}
      <Flex align="center" gap={2} px={4} py={2} bg={WA.header} zIndex={1}>
        <IconButton aria-label="Emoji" icon={<Icon as={BsEmojiSmile} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
        <IconButton aria-label="Anexar" icon={<Icon as={FiPaperclip} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
        <Input placeholder="Type a message" bg="#fff" border="none" rounded="lg" _focus={{ boxShadow: 'none' }} />
        <IconButton aria-label="Gravar áudio" icon={<Icon as={FiMic} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
      </Flex>

      <MediaModal isOpen={media.isOpen} onClose={media.onClose} />
    </Flex>
  )
}
