import type { Metadata } from 'next'
import { Suspense } from 'react'

export const metadata: Metadata = {
  title: '30 秒接入 Moltable — 备份你的 Agent 灵魂',
  description:
    '一行命令备份你的 Agent。30 秒完成 Hermes Agent、Claude、OpenClaw 的配置，换框架不换灵魂。',
  openGraph: {
    title: '30 秒接入 Moltable — 备份你的 Agent 灵魂',
    description:
      '一行命令备份你的 Agent。30 秒完成 Hermes Agent、Claude、OpenClaw 的配置。',
  },
}

export default function ConnectLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div />}>{children}</Suspense>
}
