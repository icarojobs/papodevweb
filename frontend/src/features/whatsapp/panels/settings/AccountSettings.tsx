import { Box } from '@chakra-ui/react'
import { FiFileText, FiInfo, FiShield } from 'react-icons/fi'

import { SettingNavRow, SettingsHeader } from './rows'

export function AccountSettings({ onBack }: { onBack: () => void }) {
  return (
    <Box>
      <SettingsHeader title="Account" onBack={onBack} />
      <Box mt={2}>
        <SettingNavRow icon={FiShield} title="Security notifications" />
        <SettingNavRow icon={FiFileText} title="Request account info" />
        <SettingNavRow icon={FiInfo} title="How to delete my account" />
      </Box>
    </Box>
  )
}
