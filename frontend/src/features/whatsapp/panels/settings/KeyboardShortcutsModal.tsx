import {
  Button,
  Flex,
  Grid,
  Kbd,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Text,
} from '@chakra-ui/react'

import { WA } from '../../ui'

type Shortcut = [label: string, keys: string[]]

const SHORTCUTS: Shortcut[] = [
  ['Mark as unread', ['Ctrl', 'Alt', 'Shift', 'U']],
  ['Mute', ['Ctrl', 'Alt', 'Shift', 'M']],
  ['Archive chat', ['Ctrl', 'Alt', 'Shift', 'E']],
  ['Pin chat', ['Ctrl', 'Alt', 'Shift', 'P']],
  ['Search', ['Ctrl', 'Alt', '/']],
  ['Search chat', ['Ctrl', 'Shift', 'F']],
  ['New chat', ['Ctrl', 'Alt', 'N']],
  ['Next chat', ['Ctrl', 'Alt', ']']],
  ['Previous chat', ['Ctrl', 'Alt', '[']],
  ['Label chat', ['Ctrl', 'Alt', 'Shift', 'L']],
  ['Close chat', ['Escape']],
  ['New group', ['Ctrl', 'Alt', 'Shift', 'N']],
  ['Profile and About', ['Ctrl', 'Alt', 'P']],
  ['Increase speed of selected voice message', ['Shift', '.']],
  ['Decrease speed of selected voice message', ['Shift', ',']],
  ['Settings', ['Ctrl', 'Alt', ',']],
  ['Emoji panel', ['Ctrl', 'Alt', 'E']],
  ['GIF panel', ['Ctrl', 'Alt', 'G']],
  ['Sticker panel', ['Ctrl', 'Alt', 'S']],
  ['Extended search', ['Alt', 'K']],
]

function ShortcutRow({ item }: { item: Shortcut }) {
  const [label, keys] = item
  return (
    <Flex align="center" justify="space-between" gap={4} py={2}>
      <Text fontSize="sm" color={WA.textPrimary} noOfLines={1}>
        {label}
      </Text>
      <Flex gap={1} flexShrink={0}>
        {keys.map((k) => (
          <Kbd key={k}>{k}</Kbd>
        ))}
      </Flex>
    </Flex>
  )
}

interface KeyboardShortcutsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function KeyboardShortcutsModal({ isOpen, onClose }: KeyboardShortcutsModalProps) {
  const left = SHORTCUTS.filter((_, i) => i % 2 === 0)
  const right = SHORTCUTS.filter((_, i) => i % 2 === 1)

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="2xl" isCentered scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent bg={WA.panelBg}>
        <ModalHeader color={WA.textPrimary}>Keyboard shortcuts</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Grid templateColumns="1fr 1fr" columnGap={10}>
            <Flex direction="column">{left.map((s) => <ShortcutRow key={s[0]} item={s} />)}</Flex>
            <Flex direction="column">{right.map((s) => <ShortcutRow key={s[0]} item={s} />)}</Flex>
          </Grid>
        </ModalBody>
        <ModalFooter justifyContent="center">
          <Button bg={WA.green} color="white" rounded="full" px={8} _hover={{ bg: WA.greenDark }} onClick={onClose}>
            OK
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
