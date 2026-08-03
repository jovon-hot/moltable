import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '评测基准 — Moltable AI Identity Sync',
  description:
    'Moltable 三个自研评测基准：Cross-Agent Recall、Persona Fidelity、Provision Completeness，以及与 mem0 / Zep 的对比。',
  openGraph: {
    title: '评测基准 — Moltable AI Identity Sync',
    description: 'Moltable 自研评测基准与 mem0 / Zep 对比。',
  },
}

export default function ResearchLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
