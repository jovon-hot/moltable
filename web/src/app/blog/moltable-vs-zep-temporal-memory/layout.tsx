import type { Metadata } from 'next'
import BlogLayout from '@/components/BlogLayout'

export const metadata: Metadata = {
  title: 'Moltable vs Zep: Temporal Memory vs Online Sync — Who Wins the Agent Memory Race?',
  description: 'Deep-dive comparison of Moltable vs Zep on temporal memory, online sync, architecture, and pricing. Who wins the agent memory race?',
  alternates: { canonical: 'https://www.moltable.ai/blog/moltable-vs-zep-temporal-memory' },
  openGraph: {
    title: 'Moltable vs Zep: Temporal Memory vs Online Sync — Who Wins the Agent Memory Race?',
    description: 'Online sync vs temporal knowledge graph. Version snapshots, incremental dedup, cross-framework migration — sync layer with file-level backup fallback vs enterprise memory-only.',
    url: 'https://www.moltable.ai/blog/moltable-vs-zep-temporal-memory',
    type: 'article',
    publishedTime: '2026-08-06',
    tags: ['comparison', 'zep', 'temporal-memory', 'identity', 'agent-memory'],
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <BlogLayout>{children}</BlogLayout>
}
