import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '定价 — Moltable',
  description:
    'Moltable 定价方案：Free 1 Agent · 2 Persona · 100 记忆，Pro 5 Agent · 10 Persona · 1万记忆 · 1GB 备份存储，Ultra 无限 Agent · 无限 Persona · 5万记忆 · 10GB 备份存储。',
  openGraph: {
    title: '定价 — Moltable',
    description:
      'Moltable 定价方案：Free 1 Agent · 2 Persona · 100 记忆，Pro 5 Agent · 10 Persona · 1万记忆 · 1GB 备份存储，Ultra 无限 Agent · 无限 Persona · 5万记忆 · 10GB 备份存储。',
  },
}

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
