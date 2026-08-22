import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Moltable 开发者文档 — 备份与 MCP 接入指南',
  description:
    'Moltable API 参考文档：备份 API 端点、MCP 协议接入、Hermes/Claude Agent 配置。快速开始备份你的 Agent 灵魂资产。',
  openGraph: {
    title: 'Moltable 开发者文档 — 备份与 MCP 接入指南',
    description:
      'Moltable API 参考文档：备份 API 端点、MCP 协议接入、Hermes/Claude Agent 配置。',
  },
}

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
