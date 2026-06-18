import {
  Button,
  Checkbox,
  LightMode,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Radio,
  RadioGroup,
  Stack,
  Text,
} from '@chakra-ui/react'
import { useState } from 'react'

import { useChatStore } from '@/store/chat.store'
import type { DeleteScope } from '@/types/chat'
import { WA } from '../ui'

interface DeleteConversationDialogProps {
  conversationId: string
  conversationName: string
  isOpen: boolean
  onClose: () => void
}

export function DeleteConversationDialog({
  conversationId,
  conversationName,
  isOpen,
  onClose,
}: DeleteConversationDialogProps) {
  const [scope, setScope] = useState<DeleteScope>('me')
  const [deleteMedia, setDeleteMedia] = useState(false)
  const deleteConversation = useChatStore((s) => s.deleteConversation)

  const confirm = async () => {
    try {
      await deleteConversation(conversationId, scope, deleteMedia)
    } finally {
      onClose()
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <LightMode>
        <ModalOverlay />
        <ModalContent bg={WA.panelBg} color={WA.textPrimary}>
          <ModalHeader color={WA.textPrimary}>Excluir conversa?</ModalHeader>
          <ModalBody>
            <Text fontSize="sm" color={WA.textSecondary} mb={4}>
              Esta ação não pode ser desfeita para a conversa com {conversationName}.
            </Text>
            <RadioGroup value={scope} onChange={(value) => setScope(value as DeleteScope)}>
              <Stack spacing={2}>
                <Radio value="me" colorScheme="green">
                  <Text color={WA.textPrimary}>Excluir só para mim</Text>
                </Radio>
                <Radio value="everyone" colorScheme="green">
                  <Text color={WA.textPrimary}>Excluir para todos</Text>
                </Radio>
              </Stack>
            </RadioGroup>
            <Checkbox
              mt={4}
              colorScheme="green"
              isChecked={deleteMedia}
              onChange={(event) => setDeleteMedia(event.target.checked)}
            >
              <Text color={WA.textPrimary}>
                Apagar também as mídias (fotos, arquivos e áudios)
              </Text>
            </Checkbox>
          </ModalBody>
          <ModalFooter gap={2}>
            <Button variant="ghost" color={WA.textPrimary} onClick={onClose}>
              Cancelar
            </Button>
            <Button colorScheme="red" bg={WA.danger} color="white" onClick={confirm}>
              Excluir
            </Button>
          </ModalFooter>
        </ModalContent>
      </LightMode>
    </Modal>
  )
}
