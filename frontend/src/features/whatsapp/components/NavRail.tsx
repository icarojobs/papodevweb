import { Avatar, Box, Flex, Icon, Tooltip } from '@chakra-ui/react'
import type { ReactNode } from 'react'
import type { IconType } from 'react-icons'
import { BsBroadcast, BsChatText } from 'react-icons/bs'
import { FiSettings } from 'react-icons/fi'
import { MdOutlinePeople } from 'react-icons/md'
import { TbCircleDashed } from 'react-icons/tb'

import { NAV_WIDTH, WA } from '../ui'
import { MetaAiIcon } from './MetaAiIcon'

export type Section = 'chats' | 'status' | 'channels' | 'communities' | 'meta' | 'settings'

interface NavButtonProps {
  label: string
  active: boolean
  onClick: () => void
  icon?: IconType
  badge?: number
  children?: ReactNode
}

function NavButton({ label, active, onClick, icon, badge, children }: NavButtonProps) {
  return (
    <Tooltip label={label} placement="right" openDelay={300} hasArrow>
      <Flex
        as="button"
        aria-label={label}
        position="relative"
        w="44px"
        h="44px"
        rounded="full"
        align="center"
        justify="center"
        onClick={onClick}
        bg={active ? '#e7f3ef' : 'transparent'}
        _hover={{ bg: active ? '#e7f3ef' : '#ececec' }}
        transition="background 0.15s"
      >
        {icon ? (
          <Icon as={icon} boxSize="24px" color={active ? WA.greenDark : '#54656f'} />
        ) : (
          children
        )}
        {!!badge && (
          <Flex
            position="absolute"
            top="-2px"
            right="-2px"
            minW="18px"
            h="18px"
            px="5px"
            rounded="full"
            bg={WA.unread}
            color="white"
            fontSize="11px"
            fontWeight="bold"
            align="center"
            justify="center"
          >
            {badge}
          </Flex>
        )}
      </Flex>
    </Tooltip>
  )
}

interface NavRailProps {
  active: Section
  onSelect: (section: Section) => void
  userName: string
  unreadChats?: number
}

export function NavRail({ active, onSelect, userName, unreadChats }: NavRailProps) {
  return (
    <Flex
      direction="column"
      align="center"
      justify="space-between"
      w={NAV_WIDTH}
      h="100%"
      bg={WA.railBg}
      py={3}
      borderRight={`1px solid ${WA.border}`}
    >
      <Flex direction="column" align="center" gap={1}>
        <NavButton label="Conversas" icon={BsChatText} active={active === 'chats'} badge={unreadChats} onClick={() => onSelect('chats')} />
        <NavButton label="Status" icon={TbCircleDashed} active={active === 'status'} onClick={() => onSelect('status')} />
        <NavButton label="Canais" icon={BsBroadcast} active={active === 'channels'} onClick={() => onSelect('channels')} />
        <NavButton label="Comunidades" icon={MdOutlinePeople} active={active === 'communities'} onClick={() => onSelect('communities')} />
        <NavButton label="Meta AI" active={active === 'meta'} onClick={() => onSelect('meta')}>
          <MetaAiIcon size={24} />
        </NavButton>
      </Flex>

      <Flex direction="column" align="center" gap={2}>
        <NavButton label="Configurações" icon={FiSettings} active={active === 'settings'} onClick={() => onSelect('settings')} />
        <Box as="button" aria-label="Perfil" onClick={() => onSelect('settings')}>
          <Avatar size="sm" name={userName} />
        </Box>
      </Flex>
    </Flex>
  )
}
