import { describe, expect, it } from 'vitest'

import { TermsPage } from './TermsPage'
import { renderWithProviders, screen } from '@/test/utils'

describe('TermsPage', () => {
  it('exibe a regra de retenção de 7 dias', () => {
    renderWithProviders(<TermsPage />)
    expect(screen.getByText(/Retenção de histórico e mídias/)).toBeInTheDocument()
    expect(screen.getByText(/Mensagens com mais de/)).toBeInTheDocument()
    expect(screen.getByText(/00:01/)).toBeInTheDocument()
  })
})
