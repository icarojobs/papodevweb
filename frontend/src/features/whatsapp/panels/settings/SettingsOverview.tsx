import { Avatar, Box, Flex, Icon, Input, InputGroup, InputLeftElement, Text } from '@chakra-ui/react'
import { FiSearch } from 'react-icons/fi'
import {
  MdHelpOutline,
  MdLockOutline,
  MdLogout,
  MdNotificationsNone,
  MdOutlineChat,
  MdOutlineKeyboard,
  MdOutlineVpnKey,
  MdPersonOutline,
} from 'react-icons/md'

import { WA } from '../../ui'
import { SettingNavRow } from './rows'

interface SettingsOverviewProps {
  userName: string
  about: string
  onNavigate: (screen: 'edit' | 'account' | 'privacy' | 'chats' | 'notifications' | 'help') => void
  onOpenShortcuts: () => void
  onLogout: () => void
}

export function SettingsOverview({ userName, about, onNavigate, onOpenShortcuts, onLogout }: SettingsOverviewProps) {
  return (
    <Box>
      <Text px={6} pt={6} pb={4} fontSize="2xl" fontWeight="semibold" color={WA.textPrimary}>
        {userName}
      </Text>

      <Box px={5} pb={4}>
        <InputGroup>
          <InputLeftElement pointerEvents="none">
            <Icon as={FiSearch} color={WA.textSecondary} />
          </InputLeftElement>
          <Input placeholder="Search" rounded="full" borderColor={WA.green} _focus={{ borderColor: WA.green, boxShadow: `0 0 0 1px ${WA.green}` }} />
        </InputGroup>
      </Box>

      <Flex direction="column" align="center" py={4}>
        <Box bg="#fff" boxShadow="sm" rounded="2xl" px={4} py={2} mb={-3} zIndex={1}>
          <Text fontSize="sm" color={WA.textPrimary}>
            {about}
          </Text>
        </Box>
        <Avatar size="xl" name={userName} />
      </Flex>

      <Box mt={2}>
        <SettingNavRow icon={MdPersonOutline} title="Profile" subtitle="Name, profile picture" onClick={() => onNavigate('edit')} />
        <SettingNavRow icon={MdOutlineVpnKey} title="Account" subtitle="Security notifications, account info" onClick={() => onNavigate('account')} />
        <SettingNavRow icon={MdLockOutline} title="Privacy" subtitle="Blocked contacts, disappearing messages" onClick={() => onNavigate('privacy')} />
        <SettingNavRow icon={MdOutlineChat} title="Chats" subtitle="Theme, wallpaper, chat settings" onClick={() => onNavigate('chats')} />
        <SettingNavRow icon={MdNotificationsNone} title="Notifications" subtitle="Messages, groups, sounds" onClick={() => onNavigate('notifications')} />
        <SettingNavRow icon={MdOutlineKeyboard} title="Keyboard shortcuts" subtitle="Quick actions" onClick={onOpenShortcuts} />
        <SettingNavRow icon={MdHelpOutline} title="Help and feedback" subtitle="Help centre, contact us, privacy policy" onClick={() => onNavigate('help')} />
        <SettingNavRow icon={MdLogout} title="Log out" danger onClick={onLogout} />
      </Box>
    </Box>
  )
}
