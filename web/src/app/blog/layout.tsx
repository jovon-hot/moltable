import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Moltable 博客 — Agent 在线同步与身份基础设施',
  description:
    'Agent 在线同步、MCP 协议、跨 Agent 身份 — 你的 AI 永远顺手。关于 AI Agent 在线同步层的深度技术博客。',
  alternates: {
    types: {
      'application/rss+xml': '/blog/feed.xml',
    },
  },
  openGraph: {
    title: 'Moltable 博客 — Agent 在线同步与身份基础设施',
    description:
      'Agent 在线同步、MCP 协议、跨 Agent 身份 — 你的 AI 永远顺手。关于 AI Agent 在线同步层的深度技术博客。',
  },
}

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
