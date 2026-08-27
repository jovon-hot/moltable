import type { Metadata } from 'next'
import { Suspense } from 'react'

export const metadata: Metadata = {
  title: '30 秒接入 Moltable — 你的 AI 永远顺手',
  description:
    '通过 MCP 一行接入，30 秒完成 Hermes Agent、Claude、OpenClaw 的配置，身份与记忆自动同步。你的 AI，永远顺手。',
  openGraph: {
    title: '30 秒接入 Moltable — 你的 AI 永远顺手',
    description:
      '通过 MCP 一行接入，30 秒完成 Hermes Agent、Claude、OpenClaw 的配置，身份与记忆自动同步。',
  },
}

export default function ConnectLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div />}>{children}</Suspense>
}
