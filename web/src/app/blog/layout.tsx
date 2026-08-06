import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Moltable 博客 — AI 身份同步技术与实践',
  description:
    'AI 身份层、MCP 协议、跨平台 Persona 管理 — 关于 AI Agent 身份基础设施的深度技术博客。',
  alternates: {
    types: {
      'application/rss+xml': '/blog/feed.xml',
    },
  },
  openGraph: {
    title: 'Moltable 博客 — AI 身份同步技术与实践',
    description:
      'AI 身份层、MCP 协议、跨平台 Persona 管理 — 关于 AI Agent 身份基础设施的深度技术博客。',
  },
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
