// Utilitários de formatação de data/hora e presença para a UI do chat (pt-br).

const DAY_MS = 86_400_000

export function formatMessageTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

export function formatListTime(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const diffDays = Math.floor((startOfToday - new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime()) / DAY_MS)
  if (diffDays <= 0) return formatMessageTime(iso)
  if (diffDays === 1) return 'Ontem'
  return date.toLocaleDateString('pt-BR')
}

export function formatLastSeen(iso: string | null): string {
  if (!iso) return 'offline'
  return `visto por último ${formatListTime(iso)} às ${formatMessageTime(iso)}`
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
