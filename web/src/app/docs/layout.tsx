import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Moltable 开发者文档 — MCP 协议接入指南',
  description:
    'Moltable API 参考文档：MCP 协议接入、API 端点、Hermes/Claude Agent 配置。快速开始你的 AI 身份层集成。',
  openGraph: {
    title: 'Moltable 开发者文档 — MCP 协议接入指南',
    description:
      'Moltable API 参考文档：MCP 协议接入、API 端点、Hermes/Claude Agent 配置。',
  },
}

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
