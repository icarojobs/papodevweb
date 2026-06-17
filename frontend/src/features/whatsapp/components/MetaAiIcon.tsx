import { Box } from '@chakra-ui/react'

interface MetaAiIconProps {
  size?: number
}

// Ícone "flor" colorido do Meta AI (gradiente azul→roxo→rosa).
export function MetaAiIcon({ size = 24 }: MetaAiIconProps) {
  return (
    <Box as="span" display="inline-flex" lineHeight={0}>
      <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden>
        <defs>
          <linearGradient id="metaAiGrad" x1="0" y1="0" x2="32" y2="32">
            <stop offset="0%" stopColor="#0098FA" />
            <stop offset="50%" stopColor="#7C5CFC" />
            <stop offset="100%" stopColor="#E1306C" />
          </linearGradient>
        </defs>
        <g fill="url(#metaAiGrad)">
          {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
            <ellipse key={deg} cx="16" cy="6.5" rx="3" ry="6" transform={`rotate(${deg} 16 16)`} />
          ))}
          <circle cx="16" cy="16" r="3.2" fill="#fff" />
        </g>
      </svg>
    </Box>
  )
}
