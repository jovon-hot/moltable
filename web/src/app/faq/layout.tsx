import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '常见问题 — Moltable',
  description: 'Moltable FAQ: Agent soul backup, MCP protocol, cross-framework migration, pricing, security.',
}

export default function FAQLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
