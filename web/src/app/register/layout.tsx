import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '注册 Moltable — 免费开始',
  description:
    '注册 Moltable，免费开始在线同步你的 Agent。1 Agent · 2 Persona · 100 记忆，支持 Hermes、Claude、OpenClaw。',
  openGraph: {
    title: '注册 Moltable — 免费开始',
    description:
      '注册 Moltable，免费开始在线同步你的 Agent。',
  },
}

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
