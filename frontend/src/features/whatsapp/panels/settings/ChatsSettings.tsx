import { Box } from '@chakra-ui/react'

import { SectionLabel, SettingNavRow, SettingToggleRow, SettingsHeader } from './rows'

export function ChatsSettings({ onBack }: { onBack: () => void }) {
  return (
    <Box pb={6}>
      <SettingsHeader title="Chats" onBack={onBack} />
      <SectionLabel>Display</SectionLabel>
      <SettingNavRow title="Theme" value="System default" chevron />
      <SettingNavRow title="Wallpaper" chevron />
      <SectionLabel>Chat settings</SectionLabel>
      <SettingNavRow title="Media upload quality" chevron />
      <SettingNavRow title="Media auto-download" chevron />
      <SettingToggleRow title="Spell check" subtitle="Check spelling while typing" />
      <SettingToggleRow title="Replace text with emoji" subtitle="Emoji will replace specific text as you type" />
      <SettingToggleRow title="Enter is send" subtitle="Enter key will send your message" defaultChecked />
    </Box>
  )
}
