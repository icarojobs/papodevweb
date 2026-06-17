import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
}

// Tema Chakra alinhado às cores do WhatsApp Web.
export const theme = extendTheme({
  config,
  colors: {
    // Escala completa (50–900) para o colorScheme "whatsapp" funcionar
    // corretamente, inclusive no dark mode.
    whatsapp: {
      50: '#e6fff6',
      100: '#b3f7e0',
      200: '#80efc9',
      300: '#4de7b2',
      400: '#1adf9b',
      500: '#00a884',
      600: '#008069',
      700: '#006653',
      800: '#004d3e',
      900: '#003329',
    },
  },
  components: {
    Button: {
      variants: {
        // Botão principal verde do WhatsApp com texto branco, legível em
        // qualquer color mode (evita o solid escuro padrão do dark mode).
        whatsapp: {
          bg: 'whatsapp.500',
          color: 'white',
          _hover: {
            bg: 'whatsapp.600',
            _disabled: { bg: 'whatsapp.500' },
          },
          _active: { bg: 'whatsapp.600' },
        },
      },
    },
  },
  styles: {
    global: {
      body: {
        bg: '#0b141a',
        color: 'whiteAlpha.900',
      },
    },
  },
})
