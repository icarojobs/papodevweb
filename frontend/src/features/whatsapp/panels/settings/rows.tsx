import { Box, Flex, Icon, IconButton, Switch, Text } from '@chakra-ui/react'
import type { ReactNode } from 'react'
import type { IconType } from 'react-icons'
import { FiArrowLeft, FiChevronRight } from 'react-icons/fi'

import { WA } from '../../ui'

export function SettingsHeader({ title, onBack }: { title: string; onBack?: () => void }) {
  return (
    <Flex align="center" gap={4} px={5} py={4}>
      {onBack && (
        <IconButton aria-label="Back" icon={<Icon as={FiArrowLeft} boxSize={5} />} variant="ghost" rounded="full" size="sm" onClick={onBack} />
      )}
      <Text fontSize="xl" fontWeight="semibold" color={WA.textPrimary}>
        {title}
      </Text>
    </Flex>
  )
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <Text px={6} pt={5} pb={2} fontSize="sm" color={WA.textSecondary} fontWeight="medium">
      {children}
    </Text>
  )
}

interface RowProps {
  icon?: IconType
  iconColor?: string
  title: string
  subtitle?: string
  value?: string
  chevron?: boolean
  danger?: boolean
  onClick?: () => void
}

// Linha de navegação/ação das configurações (ícone + título + subtítulo + chevron opcional).
export function SettingNavRow({ icon, iconColor, title, subtitle, value, chevron, danger, onClick }: RowProps) {
  const color = danger ? WA.danger : WA.textPrimary
  return (
    <Flex align="center" gap={5} px={6} py={3} cursor="pointer" _hover={{ bg: WA.hover }} onClick={onClick}>
      {icon && <Icon as={icon} boxSize={5} color={danger ? WA.danger : iconColor ?? WA.textSecondary} />}
      <Box flex="1" minW={0} borderBottom={`1px solid ${WA.divider}`} pb={3} mt={3} mb={-3}>
        <Text fontSize="md" color={color}>
          {title}
        </Text>
        {(subtitle ?? value) && (
          <Text fontSize="sm" color={WA.textSecondary} noOfLines={1}>
            {value ?? subtitle}
          </Text>
        )}
      </Box>
      {chevron && <Icon as={FiChevronRight} boxSize={5} color={WA.textSecondary} />}
    </Flex>
  )
}

interface ToggleRowProps {
  title: string
  subtitle?: string
  defaultChecked?: boolean
}

export function SettingToggleRow({ title, subtitle, defaultChecked }: ToggleRowProps) {
  return (
    <Flex align="center" gap={5} px={6} py={3}>
      <Box flex="1" minW={0} borderBottom={`1px solid ${WA.divider}`} pb={3} mt={3} mb={-3}>
        <Text fontSize="md" color={WA.textPrimary}>
          {title}
        </Text>
        {subtitle && (
          <Text fontSize="sm" color={WA.textSecondary}>
            {subtitle}
          </Text>
        )}
      </Box>
      <Switch colorScheme="whatsapp" defaultChecked={defaultChecked} />
    </Flex>
  )
}
