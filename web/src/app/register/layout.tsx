import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '注册 Moltable — 免费开始',
  description:
    '注册 Moltable，免费开始备份你的 Agent 灵魂资产。3 个备份源、500MB 存储，支持 Hermes、Claude、OpenClaw。',
  openGraph: {
    title: '注册 Moltable — 免费开始',
    description:
      '注册 Moltable，免费开始备份你的 Agent 灵魂资产。',
  },
}

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
