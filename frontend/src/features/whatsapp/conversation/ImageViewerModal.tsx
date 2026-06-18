import {
  Button,
  Flex,
  Icon,
  Image,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalOverlay,
} from '@chakra-ui/react'
import { useRef } from 'react'
import { FiMaximize } from 'react-icons/fi'

interface ImageViewerModalProps {
  src: string
  alt: string
  isOpen: boolean
  onClose: () => void
}

export function ImageViewerModal({ src, alt, isOpen, onClose }: ImageViewerModalProps) {
  const imageRef = useRef<HTMLImageElement>(null)

  const openFullscreen = () => {
    imageRef.current?.requestFullscreen?.()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="4xl" isCentered>
      <ModalOverlay bg="blackAlpha.800" />
      <ModalContent bg="transparent" boxShadow="none">
        <ModalCloseButton color="white" />
        <ModalBody p={0}>
          <Flex direction="column" align="center" gap={3}>
            <Image
              ref={imageRef}
              src={src}
              alt={alt}
              maxH="80vh"
              objectFit="contain"
              rounded="md"
              bg="black"
            />
            <Button
              leftIcon={<Icon as={FiMaximize} />}
              onClick={openFullscreen}
              colorScheme="whiteAlpha"
              size="sm"
            >
              Tela cheia
            </Button>
          </Flex>
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}
