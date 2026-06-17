// Dados de exemplo (mock) que reproduzem o conteúdo dos prints do WhatsApp Web.
// Ainda não há backend de chat; servem para montar a UI fielmente.

export interface Conversation {
  id: string
  name: string
  preview: string
  time: string
  unread?: number
  pinned?: boolean
  muted?: boolean
  you?: boolean
}

export interface StatusUpdate {
  id: string
  name: string
  time: string
  viewed?: boolean
}

export interface Channel {
  id: string
  name: string
  preview: string
  time: string
  unread?: number
}

export interface CommunityGroup {
  label: string
  preview: string
  time: string
  unread?: number
  announcement?: boolean
}

export interface Community {
  id: string
  name: string
  groups: CommunityGroup[]
}

export const CONVERSATIONS: Conversation[] = [
  {
    id: '1',
    name: 'Analytics - Produto',
    preview: 'Alice Data Science Analytics: https://meet.google.com/kmr-dhco-hrc',
    time: '9:59 am',
    pinned: true,
  },
  {
    id: '2',
    name: 'Meu Cel Claro 2024 (You)',
    preview: 'Video Git + Github youtube: https://youtu.be/VPu6xm3W8H0',
    time: 'Yesterday',
    pinned: true,
    you: true,
  },
  { id: '3', name: 'Tiago Da Noite', preview: '🎤 1:39', time: '10:05 am', unread: 2 },
  {
    id: '4',
    name: 'Solidworks Comunidade E.A²',
    preview: '~Paulo Pamplona: Bom dia pessoal. Fiz um desenho e preciso enviar para o engenheiro...',
    time: '9:52 am',
    unread: 344,
  },
  {
    id: '5',
    name: 'Minha familia linda',
    preview: 'Anne sobrinha: Volin essa Mara viu',
    time: '9:49 am',
    unread: 9,
    muted: true,
  },
  { id: '6', name: 'Carla Alves do Aldimar', preview: 'Combinado', time: '9:29 am' },
  {
    id: '7',
    name: 'ABSS - Associação Bank Skate Spot',
    preview: 'Henrique Gordo BSS: 📷 Video',
    time: '9:14 am',
    unread: 107,
  },
  {
    id: '8',
    name: 'Tr@nsito 4 Ribeirão Preto',
    preview: '~Marcos Faria: 🎤 0:15',
    time: '9:06 am',
    unread: 148,
    muted: true,
  },
]

export const STATUSES: StatusUpdate[] = [
  { id: '1', name: 'Janaina Freezer Horizontal 2.350,00', time: 'Today at 10:23 am' },
  { id: '2', name: 'Gralha Tatoo', time: 'Today at 10:18 am' },
  { id: '3', name: 'Calil Beer Chopp Express Chop Klaro', time: 'Today at 10:17 am' },
  { id: '4', name: 'Elaine Ferreira - Mesa Inox', time: 'Today at 10:08 am', viewed: true },
  { id: '5', name: 'TX ON - tablet xiaomi 256gb', time: 'Today at 10:02 am' },
  { id: '6', name: 'Robsom Nugroove', time: 'Today at 9:51 am' },
  { id: '7', name: 'Fabio Spimpolo Tattoo', time: 'Today at 9:48 am', viewed: true },
  { id: '8', name: 'Mario - Leiturista CPFL', time: 'Today at 9:45 am' },
  { id: '9', name: 'Chico (Velho Chico)', time: 'Today at 9:43 am' },
  { id: '10', name: 'João Neto - Aldo', time: 'Today at 9:31 am' },
]

export const CHANNELS: Channel[] = [
  { id: '1', name: 'CazeTV', preview: 'SERÁ QUE CR7 MARCA E VENCE NA ESTREIA? Diz aí qual será o placar...', time: '9:39 am', unread: 223 },
  { id: '2', name: 'Learn English | IELTS | Grammar', preview: "10 Other Ways to Say \"I'm Sad\" 1. I'm upset 2. I'm down 3. I'm heartbroken", time: '9:38 am', unread: 99 },
  { id: '3', name: 'FC Barcelona', preview: 'Can you imagine owning a Barça jersey signed by the players with eFootball? Enter now...', time: '9:16 am', unread: 74 },
  { id: '4', name: 'Pack de Figurinhas 😍', preview: 'This channel is closed in Brazil', time: '9:05 am', unread: 999 },
  { id: '5', name: 'Epic Watch Party', preview: 'Steve Carell: Hard to believe he was in this chat not long ago', time: 'Yesterday', unread: 27 },
  { id: '6', name: 'Duolingo Brasil', preview: 'cuide desse presente que eu te dei 👍', time: 'Yesterday', unread: 103 },
  { id: '7', name: 'ENGLISH GRAMMAR LEARN IELTS SPEAKING TOEFL', preview: 'Which life is better? - School life - College life - University life - Single Life', time: 'Yesterday', unread: 33 },
  { id: '8', name: 'English', preview: 'Choose the correctly spelled word: A. Medical B. Medicle C. Medicel', time: 'Monday', unread: 13 },
  { id: '9', name: 'YESMEN', preview: 'Yess', time: '10/6/2026', unread: 25 },
  { id: '10', name: 'Rafa & Luiz', preview: 'É amanhã, e já estamos em Vitória ❤️', time: '15/5/2026', unread: 2 },
]

export const COMMUNITIES: Community[] = [
  {
    id: '1',
    name: 'DEV NA GRINGA',
    groups: [
      { label: 'Announcements', preview: 'Welcome to the community!', time: '27/5/2026', announcement: true },
      { label: 'Geral', preview: '~Danilo Reis: Nunca vi', time: '8:13 am' },
    ],
  },
  {
    id: '2',
    name: 'Comunicados White',
    groups: [
      { label: 'Announcements', preview: '~Mamed: 🎤 0:14', time: 'Thursday', unread: 8, announcement: true },
      { label: 'Geral', preview: '+55 16 99718-7409 joined from the community', time: '29/5/2026' },
    ],
  },
  {
    id: '3',
    name: 'Filament Community',
    groups: [
      { label: 'Announcements', preview: 'Elias: Renovaçao Expose', time: '17/5/2026', unread: 10, announcement: true },
    ],
  },
]

// Mensagens de exemplo para a conversa aberta.
export const SAMPLE_MESSAGES = [
  'Conheça os pacotes para um fluxo bistrô em inglês. Comece por aproximadamente 15 lições. Tenha tré sessões.',
  'Mantenha a prática e revise o conteúdo das lições anteriores antes de avançar.',
  'Conheça os pacotes para um fluxo bistrô em inglês. Comece por aproximadamente 15 lições.',
  'Continue a sua jornada de aprendizado no seu ritmo. Cada lição constrói sobre a anterior.',
  'Mantenha a prática e revise o conteúdo das lições anteriores antes de avançar.',
]
