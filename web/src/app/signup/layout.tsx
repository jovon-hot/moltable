import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Join Moltable — AI Identity Layer',
  description:
    'You\'ve been invited to Moltable — the cross-platform AI identity sync platform. One registration, every AI knows you. Start free.',
  openGraph: {
    title: 'Join Moltable — AI Identity Layer',
    description:
      'You\'ve been invited to Moltable. Cross-platform AI identity sync in 3 minutes.',
  },
}

export default function SignupLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
