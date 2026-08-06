import type { Metadata } from 'next'
import BlogLayout from '@/components/BlogLayout'

export const metadata: Metadata = {
  title: 'Moltable vs Zep: Temporal Memory & Identity — Who Wins the Agent Memory Race?',
  description: 'Deep-dive comparison of Moltable vs Zep on temporal memory, identity layers, architecture, and pricing. Who wins the agent memory race?',
  alternates: { canonical: 'https://www.moltable.ai/blog/moltable-vs-zep-temporal-memory' },
  openGraph: {
    title: 'Moltable vs Zep: Temporal Memory & Identity — Who Wins the Agent Memory Race?',
    description: 'Temporal tracking vs temporal knowledge graph. Identity sync, memory health, persona — four-in-one vs enterprise memory-only.',
    url: 'https://www.moltable.ai/blog/moltable-vs-zep-temporal-memory',
    type: 'article',
    publishedTime: '2026-08-06',
    tags: ['comparison', 'zep', 'temporal-memory', 'identity', 'agent-memory'],
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <BlogLayout>{children}</BlogLayout>
}
