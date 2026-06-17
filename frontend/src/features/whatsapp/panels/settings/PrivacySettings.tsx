import { Box } from '@chakra-ui/react'

import { SectionLabel, SettingNavRow, SettingToggleRow, SettingsHeader } from './rows'

export function PrivacySettings({ onBack }: { onBack: () => void }) {
  return (
    <Box pb={6}>
      <SettingsHeader title="Privacy" onBack={onBack} />
      <SectionLabel>Who can see my personal info</SectionLabel>
      <SettingNavRow title="Last seen and online" value="Nobody" chevron />
      <SettingNavRow title="Profile picture" value="My contacts" chevron />
      <SettingNavRow title="About" value="My contacts" chevron />
      <SettingNavRow title="Status" value="My contacts" chevron />
      <SettingToggleRow
        title="Read receipts"
        subtitle="If turned off, you won't send or receive read receipts. Read receipts are always sent for group chats."
      />
      <SectionLabel>Disappearing messages</SectionLabel>
      <SettingNavRow title="Default message timer" value="Off" chevron />
      <SettingNavRow title="Groups" value="My contacts" chevron />
      <SettingNavRow title="Blocked contacts" value="71" chevron />
      <SettingNavRow title="App lock" subtitle="Require password to unlock WhatsApp" chevron />
      <SectionLabel>Advanced</SectionLabel>
    </Box>
  )
}
