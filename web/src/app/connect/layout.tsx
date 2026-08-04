import type { Metadata } from 'next'
import { Suspense } from 'react'

export const metadata: Metadata = {
  title: '30 秒接入 Moltable — AI Identity Sync 配置指南',
  description:
    '一行命令接入 Moltable。30 秒完成 Hermes Agent、Claude、Cursor 的 MCP 配置，让 AI 自动认识你。',
  openGraph: {
    title: '30 秒接入 Moltable — AI Identity Sync 配置指南',
    description:
      '一行命令接入 Moltable。30 秒完成 Hermes Agent、Claude、Cursor 的 MCP 配置。',
  },
}

export default function ConnectLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div />}>{children}</Suspense>
}
