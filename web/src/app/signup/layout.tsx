import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Join Moltable — Agent Soul Backup',
  description:
    'Back up your Agent soul — SOUL.md, skills, MCP config, memories. Switch agents, keep your soul. Start free.',
  openGraph: {
    title: 'Join Moltable — Agent Soul Backup',
    description:
      'Back up your Agent soul. Switch agents, keep your soul.',
  },
}

export default function SignupLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
