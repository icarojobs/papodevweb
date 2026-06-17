import { Box, Button, Flex, Icon, Text, VStack } from '@chakra-ui/react'
import type { ReactNode } from 'react'
import { FiFileText, FiUserPlus } from 'react-icons/fi'

import { WA } from '../ui'
import { MetaAiIcon } from './MetaAiIcon'

function LaptopIllustration() {
  return (
    <svg width="120" height="96" viewBox="0 0 120 96" fill="none" aria-hidden>
      <rect x="22" y="14" width="76" height="52" rx="6" fill="#fff" stroke="#3b4a54" strokeWidth="3" />
      <rect x="28" y="20" width="34" height="40" rx="3" fill={WA.green} />
      <path d="M70 30 a14 14 0 0 1 14 14 v6 a4 4 0 0 1-4 4 h-2 a3 3 0 0 1-3-3 v-5 a5 5 0 0 0-10 0" fill="#3b4a54" />
      <rect x="10" y="66" width="100" height="8" rx="4" fill="#3b4a54" />
    </svg>
  )
}

interface ActionProps {
  icon: ReactNode
  label: string
}

function QuickAction({ icon, label }: ActionProps) {
  return (
    <VStack spacing={2}>
      <Flex
        w="48px"
        h="48px"
        rounded="full"
        bg="#e9edef"
        align="center"
        justify="center"
        cursor="pointer"
        _hover={{ bg: '#dfe5e7' }}
      >
        {icon}
      </Flex>
      <Text fontSize="xs" color={WA.textSecondary}>
        {label}
      </Text>
    </VStack>
  )
}

// Card de "Download WhatsApp for Windows" + ações rápidas (estado vazio à direita).
export function DownloadPromo() {
  return (
    <VStack spacing={10}>
      <Box bg="#fff" rounded="2xl" px={12} py={10} boxShadow="sm" maxW="360px" textAlign="center">
        <Flex justify="center" mb={6}>
          <LaptopIllustration />
        </Flex>
        <Text fontSize="2xl" fontWeight="semibold" color={WA.textPrimary} lineHeight="short">
          Download WhatsApp for Windows
        </Text>
        <Text fontSize="sm" color={WA.textSecondary} mt={3} mb={6}>
          Get extra features like voice and video calling, screen sharing and more.
        </Text>
        <Button bg="#d9fdd3" color={WA.greenDark} rounded="full" px={6} _hover={{ bg: '#c5f7bc' }}>
          Download
        </Button>
      </Box>

      <Flex gap={10}>
        <QuickAction icon={<Icon as={FiFileText} boxSize={5} color={WA.textPrimary} />} label="Send document" />
        <QuickAction icon={<Icon as={FiUserPlus} boxSize={5} color={WA.textPrimary} />} label="Add contact" />
        <QuickAction icon={<MetaAiIcon size={22} />} label="Ask Meta AI" />
      </Flex>
    </VStack>
  )
}
