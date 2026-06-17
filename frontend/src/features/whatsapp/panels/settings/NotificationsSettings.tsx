import { Box, Text } from '@chakra-ui/react'
import { MdOutlineChat, MdOutlinePeople } from 'react-icons/md'
import { TbCircleDashed } from 'react-icons/tb'

import { WA } from '../../ui'
import { SettingNavRow, SettingToggleRow, SettingsHeader } from './rows'

export function NotificationsSettings({ onBack }: { onBack: () => void }) {
  return (
    <Box pb={6}>
      <SettingsHeader title="Notifications" onBack={onBack} />
      <SettingNavRow icon={MdOutlineChat} title="Messages" value="Off" chevron />
      <SettingNavRow icon={MdOutlinePeople} title="Groups" value="Off" chevron />
      <SettingNavRow icon={TbCircleDashed} title="Status" value="Off" chevron />
      <SettingToggleRow title="Show previews" subtitle="Preview message text inside message notifications." />
      <SettingToggleRow title="Play sound for outgoing messages" />
      <SettingToggleRow title="Background sync" subtitle="Get faster performance by syncing messages in the background." />
      <Text px={6} pt={4} fontSize="sm" color={WA.textSecondary}>
        To get notifications, make sure they're turned on in your browser and device settings.
      </Text>
    </Box>
  )
}
