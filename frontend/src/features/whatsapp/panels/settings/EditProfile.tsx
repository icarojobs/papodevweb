import { Avatar, Box, Button, Flex, Icon, IconButton, Text } from '@chakra-ui/react'
import type { ReactNode } from 'react'
import { FiCamera, FiCopy, FiEdit2, FiPhone } from 'react-icons/fi'

import { WA } from '../../ui'
import { SettingsHeader } from './rows'

interface EditProfileProps {
  userName: string
  about: string
  phone: string
  onBack: () => void
}

function Field({ label, value, action }: { label: string; value: string; action: ReactNode }) {
  return (
    <Box px={6} py={4}>
      <Text fontSize="sm" color={WA.textSecondary} mb={2}>
        {label}
      </Text>
      <Flex align="center" justify="space-between" gap={3}>
        <Text fontSize="md" color={WA.textPrimary} noOfLines={1}>
          {value}
        </Text>
        {action}
      </Flex>
    </Box>
  )
}

export function EditProfile({ userName, about, phone, onBack }: EditProfileProps) {
  return (
    <Box>
      <SettingsHeader title="Edit profile" onBack={onBack} />

      <Flex direction="column" align="center" py={4}>
        <Avatar size="2xl" name={userName} />
        <Button mt={-4} leftIcon={<Icon as={FiCamera} />} size="sm" rounded="full" bg="#fff" boxShadow="sm" color={WA.greenDark} variant="solid" _hover={{ bg: '#f0f2f5' }}>
          Edit
        </Button>
      </Flex>

      <Field
        label="Name"
        value={userName}
        action={<IconButton aria-label="Editar nome" icon={<Icon as={FiEdit2} />} size="sm" variant="ghost" color={WA.textSecondary} />}
      />
      <Field label="About" value={about} action={<IconButton aria-label="Editar sobre" icon={<Icon as={FiEdit2} />} size="sm" variant="ghost" color={WA.textSecondary} />} />
      <Box px={6} py={4}>
        <Text fontSize="sm" color={WA.textSecondary} mb={2}>
          Phone
        </Text>
        <Flex align="center" justify="space-between">
          <Flex align="center" gap={3}>
            <Icon as={FiPhone} color={WA.textSecondary} />
            <Text fontSize="md" color={WA.textPrimary}>
              {phone}
            </Text>
          </Flex>
          <IconButton aria-label="Copiar telefone" icon={<Icon as={FiCopy} />} size="sm" variant="ghost" color={WA.textSecondary} />
        </Flex>
      </Box>
    </Box>
  )
}
