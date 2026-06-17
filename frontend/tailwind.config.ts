import type { Config } from 'tailwindcss'

// Paleta extraída do WhatsApp Web para manter o look-and-feel real.
const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        whatsapp: {
          green: '#00a884',
          'green-dark': '#008069',
          teal: '#128c7e',
          'panel-dark': '#111b21',
          'panel-header': '#202c33',
          'bg-light': '#f0f2f5',
          'chat-bg': '#0b141a',
        },
      },
    },
  },
  plugins: [],
}

export default config
