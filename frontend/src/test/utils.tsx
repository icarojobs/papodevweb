import { ChakraProvider } from '@chakra-ui/react'
import { render, type RenderOptions } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'
import { MemoryRouter } from 'react-router-dom'

import { theme } from '@/theme'

function Providers({ children }: { children: ReactNode }) {
  return (
    <ChakraProvider theme={theme}>
      <MemoryRouter>{children}</MemoryRouter>
    </ChakraProvider>
  )
}

export function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  return render(ui, { wrapper: Providers, ...options })
}

export * from '@testing-library/react'
