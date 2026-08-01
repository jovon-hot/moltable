import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '常见问题 — Moltable',
  description: 'Moltable FAQ: AI identity sync, MCP protocol, cross-platform Agent memory, pricing, security.',
}

export default function FAQLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
