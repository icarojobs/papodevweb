import { Box, useDisclosure } from '@chakra-ui/react'
import { useState } from 'react'

import { WA } from '../../ui'
import { AccountSettings } from './AccountSettings'
import { ChatsSettings } from './ChatsSettings'
import { EditProfile } from './EditProfile'
import { HelpSettings } from './HelpSettings'
import { KeyboardShortcutsModal } from './KeyboardShortcutsModal'
import { NotificationsSettings } from './NotificationsSettings'
import { PrivacySettings } from './PrivacySettings'
import { SettingsOverview } from './SettingsOverview'

type Screen = 'overview' | 'edit' | 'account' | 'privacy' | 'chats' | 'notifications' | 'help'

interface SettingsPanelProps {
  userName: string
  about: string
  phone: string
  onLogout: () => void
}

export function SettingsPanel({ userName, about, phone, onLogout }: SettingsPanelProps) {
  const [screen, setScreen] = useState<Screen>('overview')
  const shortcuts = useDisclosure()
  const back = () => setScreen('overview')

  return (
    <Box h="100%" overflowY="auto" bg={WA.panelBg}>
      {screen === 'overview' && (
        <SettingsOverview
          userName={userName}
          about={about}
          onNavigate={setScreen}
          onOpenShortcuts={shortcuts.onOpen}
          onLogout={onLogout}
        />
      )}
      {screen === 'edit' && <EditProfile userName={userName} about={about} phone={phone} onBack={back} />}
      {screen === 'account' && <AccountSettings onBack={back} />}
      {screen === 'privacy' && <PrivacySettings onBack={back} />}
      {screen === 'chats' && <ChatsSettings onBack={back} />}
      {screen === 'notifications' && <NotificationsSettings onBack={back} />}
      {screen === 'help' && <HelpSettings onBack={back} />}

      <KeyboardShortcutsModal isOpen={shortcuts.isOpen} onClose={shortcuts.onClose} />
    </Box>
  )
}
