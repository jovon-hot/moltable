import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Moltable 开发者文档 — 在线同步与 MCP 接入指南',
  description:
    'Moltable API 参考文档：MCP 同步接口、文件级备份 API 端点、Hermes/Claude Agent 配置。快速开始同步你的 Agent。',
  openGraph: {
    title: 'Moltable 开发者文档 — 在线同步与 MCP 接入指南',
    description:
      'Moltable API 参考文档：MCP 同步接口、文件级备份 API 端点、Hermes/Claude Agent 配置。',
  },
}

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
