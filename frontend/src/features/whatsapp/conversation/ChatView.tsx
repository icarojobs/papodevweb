import {
  Avatar,
  Box,
  Flex,
  Icon,
  IconButton,
  Input,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Portal,
  Text,
  useDisclosure,
  useToast,
} from '@chakra-ui/react'
import { useEffect, useRef, useState } from 'react'
import { BsEmojiSmile, BsThreeDotsVertical } from 'react-icons/bs'
import { FiLogOut, FiMic, FiPaperclip, FiSearch, FiSend, FiSquare, FiTrash2, FiVideo } from 'react-icons/fi'
import { HiOutlinePhotograph } from 'react-icons/hi'
import { TbStar, TbStarFilled } from 'react-icons/tb'

import { AUDIO_MAX_SECONDS, TYPING_DEBOUNCE_MS } from '@/lib/constants'
import { validateMediaFile } from '@/lib/media'
import { mediaService } from '@/services/media.service'
import { useAuthStore } from '@/store/auth.store'
import { useChatStore } from '@/store/chat.store'
import type { Conversation } from '@/types/chat'
import { formatLastSeen } from '../format'
import { WA } from '../ui'
import { DeleteConversationDialog } from './DeleteConversationDialog'
import { MediaModal } from './MediaModal'
import { MessageBubble } from './MessageBubble'

function formatCountdown(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  return `${minutes}:${String(seconds % 60).padStart(2, '0')}`
}

function useAudioRecorder(onReady: (file: File) => void) {
  const [recording, setRecording] = useState(false)
  const [remaining, setRemaining] = useState(AUDIO_MAX_SECONDS)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval>>()
  const remainingRef = useRef(AUDIO_MAX_SECONDS)

  const stop = () => {
    if (timerRef.current) clearInterval(timerRef.current)
    recorderRef.current?.stop()
    setRecording(false)
  }

  const start = async () => {
    if (!navigator.mediaDevices?.getUserMedia) return
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream)
    chunksRef.current = []
    recorder.ondataavailable = (event) => chunksRef.current.push(event.data)
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
      onReady(new File([blob], 'audio.webm', { type: blob.type }))
      stream.getTracks().forEach((track) => track.stop())
    }
    recorder.start()
    recorderRef.current = recorder
    remainingRef.current = AUDIO_MAX_SECONDS
    setRemaining(AUDIO_MAX_SECONDS)
    setRecording(true)
    // Contagem regressiva; encerra automaticamente ao chegar a zero (2 min).
    timerRef.current = setInterval(() => {
      remainingRef.current -= 1
      setRemaining(remainingRef.current)
      if (remainingRef.current <= 0) stop()
    }, 1000)
  }

  useEffect(() => () => clearInterval(timerRef.current), [])

  return { recording, remaining, start, stop }
}

function presenceLabel(conversation: Conversation, currentUserId: string, typingNames: string[]) {
  if (typingNames.length > 0) {
    return conversation.type === 'group' ? `${typingNames[0]} está digitando…` : 'digitando…'
  }
  if (conversation.type === 'group') {
    return conversation.participants.map((participant) => participant.full_name).join(', ')
  }
  const other = conversation.participants.find((participant) => participant.id !== currentUserId)
  if (!other) return ''
  return other.online ? 'online' : formatLastSeen(other.last_seen)
}

interface ChatViewProps {
  conversation: Conversation
}

export function ChatView({ conversation }: ChatViewProps) {
  const media = useDisclosure()
  const deleteDialog = useDisclosure()
  const currentUserId = useAuthStore((s) => s.user?.id ?? '')
  const messages = useChatStore((s) => s.messagesByConversation[conversation.id])
  const typingIds = useChatStore((s) => s.typingByConversation[conversation.id])
  const sendMessage = useChatStore((s) => s.sendMessage)
  const sendTyping = useChatStore((s) => s.sendTyping)
  const toggleFavourite = useChatStore((s) => s.toggleFavourite)
  const leaveGroup = useChatStore((s) => s.leaveGroup)
  const toast = useToast()
  const isGroup = conversation.type === 'group'
  const [draft, setDraft] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const typingTimeout = useRef<ReturnType<typeof setTimeout>>()
  const scrollRef = useRef<HTMLDivElement>(null)

  const recorder = useAudioRecorder(async (file) => {
    const uploaded = await mediaService.upload(file)
    await sendMessage('', { ...uploaded, duration: uploaded.duration ?? null })
  })

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
  }, [messages])

  const typingNames = (typingIds ?? [])
    .map((id) => conversation.participants.find((p) => p.id === id)?.full_name)
    .filter((name): name is string => Boolean(name))

  const handleDraftChange = (value: string) => {
    setDraft(value)
    sendTyping(true)
    clearTimeout(typingTimeout.current)
    typingTimeout.current = setTimeout(() => sendTyping(false), TYPING_DEBOUNCE_MS)
  }

  const submit = async () => {
    if (!draft.trim()) return
    const text = draft
    setDraft('')
    sendTyping(false)
    await sendMessage(text)
  }

  const handleFile = async (file: File | undefined) => {
    if (!file) return
    const error = validateMediaFile(file)
    if (error) {
      toast({ status: 'error', title: error, duration: 4000, isClosable: true })
      return
    }
    const uploaded = await mediaService.upload(file)
    await sendMessage('', uploaded)
  }

  return (
    <Flex direction="column" h="100%" bg={WA.chatWallpaper} position="relative">
      <Box
        position="absolute"
        inset={0}
        opacity={0.4}
        bgImage="radial-gradient(#d6cfc4 0.5px, transparent 0.5px)"
        bgSize="18px 18px"
        pointerEvents="none"
      />

      <Flex
        align="center"
        justify="space-between"
        px={4}
        py={2}
        bg={WA.header}
        borderBottom={`1px solid ${WA.border}`}
        zIndex={1}
      >
        <Flex align="center" gap={3} minW={0}>
          <Avatar size="sm" name={conversation.name} />
          <Box minW={0}>
            <Text fontSize="md" color={WA.textPrimary} noOfLines={1}>
              {conversation.name}
            </Text>
            <Text fontSize="xs" color={WA.textSecondary} noOfLines={1}>
              {presenceLabel(conversation, currentUserId, typingNames)}
            </Text>
          </Box>
        </Flex>
        <Flex align="center" gap={1} color={WA.textSecondary}>
          <IconButton
            aria-label={conversation.favourite ? 'Desfavoritar' : 'Favoritar'}
            icon={<Icon as={conversation.favourite ? TbStarFilled : TbStar} boxSize={5} />}
            variant="ghost"
            rounded="full"
            onClick={() => toggleFavourite(conversation.id)}
          />
          <IconButton aria-label="Chamada de vídeo" icon={<Icon as={FiVideo} boxSize={5} />} variant="ghost" rounded="full" />
          <IconButton aria-label="Mídia" icon={<Icon as={HiOutlinePhotograph} boxSize={5} />} variant="ghost" rounded="full" onClick={media.onOpen} />
          <IconButton aria-label="Pesquisar" icon={<Icon as={FiSearch} boxSize={5} />} variant="ghost" rounded="full" />
          <Menu placement="bottom-end">
            <MenuButton
              as={IconButton}
              aria-label="Menu"
              icon={<Icon as={BsThreeDotsVertical} boxSize={5} />}
              variant="ghost"
              rounded="full"
            />
            <Portal>
              <MenuList zIndex="dropdown">
                {isGroup && (
                  <MenuItem
                    icon={<Icon as={FiLogOut} />}
                    onClick={() => leaveGroup(conversation.id)}
                  >
                    Sair do grupo
                  </MenuItem>
                )}
                <MenuItem
                  icon={<Icon as={FiTrash2} />}
                  color={WA.danger}
                  onClick={deleteDialog.onOpen}
                >
                  Excluir conversa
                </MenuItem>
              </MenuList>
            </Portal>
          </Menu>
        </Flex>
      </Flex>

      <Box ref={scrollRef} flex="1" overflowY="auto" py={4} zIndex={1}>
        {(messages ?? []).map((message) => (
          <MessageBubble
            key={message.id}
            conversationId={conversation.id}
            message={message}
            mine={message.sender_id === currentUserId}
            senderName={
              conversation.type === 'group'
                ? conversation.participants.find((p) => p.id === message.sender_id)?.full_name
                : undefined
            }
          />
        ))}
      </Box>

      <Flex align="center" gap={2} px={4} py={2} bg={WA.header} zIndex={1}>
        <IconButton aria-label="Emoji" icon={<Icon as={BsEmojiSmile} boxSize={5} />} variant="ghost" rounded="full" color={WA.textSecondary} />
        <IconButton
          aria-label="Anexar"
          icon={<Icon as={FiPaperclip} boxSize={5} />}
          variant="ghost"
          rounded="full"
          color={WA.textSecondary}
          onClick={() => fileInputRef.current?.click()}
        />
        <input
          ref={fileInputRef}
          type="file"
          hidden
          aria-label="Selecionar arquivo"
          onChange={(event) => {
            handleFile(event.target.files?.[0])
            event.target.value = ''
          }}
        />
        {recorder.recording ? (
          <Flex
            flex="1"
            align="center"
            gap={2}
            bg="#fff"
            rounded="lg"
            px={3}
            h="40px"
            aria-label="Gravando áudio"
          >
            <Box w="10px" h="10px" rounded="full" bg={WA.danger} />
            <Text fontSize="sm" color={WA.textPrimary} sx={{ fontVariantNumeric: 'tabular-nums' }}>
              {formatCountdown(recorder.remaining)}
            </Text>
            <Text fontSize="xs" color={WA.textSecondary}>
              gravando… (máx. 2 min)
            </Text>
          </Flex>
        ) : (
          <Input
            placeholder="Digite uma mensagem"
            value={draft}
            onChange={(event) => handleDraftChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                submit()
              }
            }}
            bg="#fff"
            border="none"
            rounded="lg"
            _focus={{ boxShadow: 'none' }}
          />
        )}
        {draft.trim() ? (
          <IconButton aria-label="Enviar" icon={<Icon as={FiSend} boxSize={5} />} variant="ghost" rounded="full" color={WA.greenDark} onClick={submit} />
        ) : (
          <IconButton
            aria-label={recorder.recording ? 'Parar gravação' : 'Gravar áudio'}
            icon={<Icon as={recorder.recording ? FiSquare : FiMic} boxSize={5} />}
            variant="ghost"
            rounded="full"
            color={recorder.recording ? WA.danger : WA.textSecondary}
            onClick={() => (recorder.recording ? recorder.stop() : recorder.start())}
          />
        )}
      </Flex>

      <MediaModal isOpen={media.isOpen} onClose={media.onClose} />
      <DeleteConversationDialog
        conversationId={conversation.id}
        conversationName={conversation.name}
        isOpen={deleteDialog.isOpen}
        onClose={deleteDialog.onClose}
      />
    </Flex>
  )
}
