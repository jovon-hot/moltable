import type { Metadata } from 'next'
import BlogLayout from '@/components/BlogLayout'

export const metadata: Metadata = {
  title: 'Moltable vs mem0: 在线同步和记忆层的本质区别',
  description: '为什么你的 AI Agent 有了记忆还是不认识你？深度剖析 Agent 在线同步和记忆层的本质差异，帮你做出正确的技术选型。',
  alternates: { canonical: 'https://www.moltable.ai/blog/moltable-vs-mem0-identity-vs-memory' },
  openGraph: {
    title: 'Moltable vs mem0: Online Sync vs Memory — 本质区别',
    description: '在线同步不是记忆层。从架构哲学、数据模型、多 Agent 协作三个维度深度对比。',
    url: 'https://www.moltable.ai/blog/moltable-vs-mem0-identity-vs-memory',
    type: 'article',
    publishedTime: '2026-08-05',
    tags: ['AI', 'MCP', 'Identity', 'Memory', 'mem0'],
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <BlogLayout>{children}</BlogLayout>
}
