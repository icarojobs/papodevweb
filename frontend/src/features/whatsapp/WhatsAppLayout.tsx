import { Box, Flex, Icon, LightMode, Text } from '@chakra-ui/react'
import { useState } from 'react'
import { BsBroadcast } from 'react-icons/bs'
import { HiOutlineUserGroup } from 'react-icons/hi2'
import { TbCircleDashed } from 'react-icons/tb'

import { useAuthStore } from '@/store/auth.store'
import { DownloadPromo } from './components/DownloadPromo'
import { EmptyState } from './components/EmptyState'
import { MetaAiIcon } from './components/MetaAiIcon'
import { NavRail, type Section } from './components/NavRail'
import { ChatView } from './conversation/ChatView'
import type { Conversation } from './data/mock'
import { ChannelsPanel } from './panels/ChannelsPanel'
import { ChatsPanel } from './panels/ChatsPanel'
import { CommunitiesPanel } from './panels/CommunitiesPanel'
import { SettingsPanel } from './panels/settings/SettingsPanel'
import { StatusPanel } from './panels/StatusPanel'
import { LIST_WIDTH, WA } from './ui'

const ABOUT = 'Disponível'
const PHONE = '+55 16 99244-2063'

function PromoPane() {
  return (
    <Flex h="100%" align="center" justify="center" bg={WA.rightBg}>
      <DownloadPromo />
    </Flex>
  )
}

export function WhatsAppLayout() {
  const [section, setSection] = useState<Section>('chats')
  const [selectedChat, setSelectedChat] = useState<Conversation | null>(null)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const userName = user?.full_name ?? 'Você'

  const renderPanel = () => {
    switch (section) {
      case 'chats':
        return <ChatsPanel selectedId={selectedChat?.id} onSelectChat={setSelectedChat} />
      case 'status':
        return <StatusPanel userName={userName} />
      case 'channels':
        return <ChannelsPanel />
      case 'communities':
        return <CommunitiesPanel />
      case 'settings':
        return <SettingsPanel userName={userName} about={ABOUT} phone={PHONE} onLogout={logout} />
      case 'meta':
        return (
          <Box p={6} bg={WA.panelBg} h="100%">
            <Text fontSize="2xl" fontWeight="semibold" color={WA.textPrimary}>
              Meta AI
            </Text>
          </Box>
        )
    }
  }

  const renderRight = () => {
    switch (section) {
      case 'chats':
        return selectedChat ? <ChatView conversation={selectedChat} /> : <PromoPane />
      case 'settings':
        return <PromoPane />
      case 'status':
        return (
          <EmptyState
            icon={<Icon as={TbCircleDashed} boxSize="72px" color="#d1d7db" />}
            title="Share status updates"
            subtitle="Share photos, videos and text that disappear after 24 hours."
          />
        )
      case 'channels':
        return (
          <EmptyState
            icon={<Icon as={BsBroadcast} boxSize="72px" color="#d1d7db" />}
            title="Discover channels"
            subtitle="Entertainment, sports, news, lifestyle, people and more. Follow the channels that interest you"
          />
        )
      case 'communities':
        return (
          <EmptyState
            icon={<Icon as={HiOutlineUserGroup} boxSize="72px" color="#d1d7db" />}
            title="Create communities"
            subtitle="Bring members together in topic-based groups and easily send them admin announcements."
            footer={
              <Text fontSize="xs" color={WA.textMuted}>
                🔒 Your personal messages in communities are end-to-end encrypted
              </Text>
            }
          />
        )
      case 'meta':
        return (
          <EmptyState
            icon={<MetaAiIcon size={72} />}
            title="Meta AI"
            subtitle="Pergunte qualquer coisa para a Meta AI."
          />
        )
    }
  }

  return (
    <LightMode>
      <Flex h="100vh" bg={WA.panelBg} overflow="hidden" color={WA.textPrimary}>
        <NavRail active={section} onSelect={setSection} userName={userName} unreadChats={27} />
        <Box w={LIST_WIDTH} flexShrink={0} borderRight={`1px solid ${WA.border}`} h="100%">
          {renderPanel()}
        </Box>
        <Box flex="1" h="100%">
          {renderRight()}
        </Box>
      </Flex>
    </LightMode>
  )
}
