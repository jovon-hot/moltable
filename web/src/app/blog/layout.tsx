import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Moltable 博客 — Agent 灵魂备份与迁移实践',
  description:
    'Agent 灵魂资产、MCP 协议、跨框架迁移 — 关于 AI Agent 灵魂备份与版本化的深度技术博客。',
  alternates: {
    types: {
      'application/rss+xml': '/blog/feed.xml',
    },
  },
  openGraph: {
    title: 'Moltable 博客 — Agent 灵魂备份与迁移实践',
    description:
      'Agent 灵魂资产、MCP 协议、跨框架迁移 — 关于 AI Agent 灵魂备份与版本化的深度技术博客。',
  },
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
