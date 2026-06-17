import { Box, Text } from '@chakra-ui/react'
import { FiFileText, FiHelpCircle } from 'react-icons/fi'
import { BsBug, BsQuestionSquare } from 'react-icons/bs'
import { MdOutlineReport } from 'react-icons/md'

import { WA } from '../../ui'
import { SettingNavRow, SettingToggleRow, SettingsHeader } from './rows'

export function HelpSettings({ onBack }: { onBack: () => void }) {
  return (
    <Box pb={6}>
      <SettingsHeader title="Help and feedback" onBack={onBack} />
      <SettingNavRow icon={FiHelpCircle} title="Help Centre" subtitle="Frequently asked questions" />
      <SettingNavRow icon={BsQuestionSquare} title="Contact us" subtitle="Chat with support to get answers" />
      <SettingNavRow icon={BsBug} title="Send feedback" subtitle="Technical issues, suggestions" />
      <SettingNavRow icon={FiFileText} title="Terms and Privacy Policy" />
      <SettingNavRow icon={MdOutlineReport} title="Channels reports" />
      <SettingToggleRow title="Join the beta" subtitle="Get new features before they are released. Report bugs using the Contact us form above." />
      <Text textAlign="center" pt={4} fontSize="sm" color={WA.textSecondary}>
        Version 2.3000.1041637338
      </Text>
    </Box>
  )
}
