import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '服务条款 — Moltable',
  description:
    'Moltable 服务条款：使用 Agent 在线同步与迁移服务需遵守的条款与条件，包括账户责任、使用限制和退款政策。',
  openGraph: {
    title: '服务条款 — Moltable',
    description:
      'Moltable 服务条款：使用 Agent 在线同步与迁移服务需遵守的条款与条件。',
  },
}

export default function TermsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
