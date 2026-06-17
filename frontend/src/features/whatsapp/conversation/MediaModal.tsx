import {
  Box,
  Grid,
  Icon,
  IconButton,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Tab,
  TabList,
  Tabs,
} from '@chakra-ui/react'
import { FiDownload } from 'react-icons/fi'

import { WA } from '../ui'

const SWATCHES = ['#cfd8dc', '#aed581', '#ffe082', '#80cbc4', '#ef9a9a', '#b0bec5', '#a5d6a7', '#ffcc80', '#90caf9']

interface MediaModalProps {
  isOpen: boolean
  onClose: () => void
}

// Modal "Media, links and docs" (reproduz o print medias/01).
export function MediaModal({ isOpen, onClose }: MediaModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="3xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent bg={WA.panelBg}>
        <ModalHeader display="flex" alignItems="center" justifyContent="space-between" pr={12}>
          <Box fontSize="md" color={WA.textPrimary}>
            Media
          </Box>
          <IconButton aria-label="Baixar" icon={<Icon as={FiDownload} />} size="sm" variant="ghost" />
        </ModalHeader>
        <ModalCloseButton />
        <Tabs colorScheme="green">
          <TabList px={6}>
            <Tab>Media</Tab>
            <Tab>Docs</Tab>
            <Tab>Links</Tab>
          </TabList>
          <ModalBody py={4}>
            <Grid templateColumns="repeat(4, 1fr)" gap={1}>
              {Array.from({ length: 24 }).map((_, i) => (
                <Box key={i} pb="100%" position="relative" rounded="sm" overflow="hidden">
                  <Box position="absolute" inset={0} bg={SWATCHES[i % SWATCHES.length]} />
                </Box>
              ))}
            </Grid>
          </ModalBody>
        </Tabs>
      </ModalContent>
    </Modal>
  )
}
