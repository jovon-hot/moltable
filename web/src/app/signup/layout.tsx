import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Join Moltable — Your AI, Always in Sync',
  description:
    'Sync your Agent identity, memories, personas, and projects across devices and agents. Your AI, always in sync. Start free.',
  openGraph: {
    title: 'Join Moltable — Your AI, Always in Sync',
    description:
      'Sync your Agent across devices and agents. Your AI, always in sync.',
  },
}

export default function SignupLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
