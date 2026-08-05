import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable',
  description:
    '从开源到商业，从向量搜索到图谱记忆——2026年主流AI Agent记忆系统横向对比。帮你选择最适合技术栈的记忆方案：mem0、Zep、Moltable 功能/架构/定价全维度分析。',
  keywords: [
    'AI Agent 记忆对比',
    'mem0 vs Zep',
    'Agent memory comparison',
    '向量记忆',
    '知识图谱记忆',
    'AI记忆系统测评',
  ],
  openGraph: {
    title: 'AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable',
    description:
      '2026年主流AI Agent记忆系统横向对比。mem0、Zep、Moltable 功能/架构/定价全维度分析。',
    url: 'https://www.moltable.ai/blog/agent-memory-landscape-2026',
    siteName: 'Moltable.ai',
    type: 'article',
    publishedTime: '2026-07-10',
    images: [
      {
        url: '/logo-horizontal.svg',
        width: 1200,
        height: 630,
        alt: 'AI Agent 记忆系统全景对比',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Agent 记忆系统全景对比 2026',
    description:
      'mem0 vs Zep vs Moltable — 功能/架构/定价全维度对比分析。',
    images: ['/logo-horizontal.svg'],
  },
  alternates: {
    canonical: 'https://www.moltable.ai/blog/agent-memory-landscape-2026',
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Article',
            headline: 'AI Agent 记忆系统全景对比 2026：mem0 vs Zep vs Moltable',
            description:
              '从开源到商业，从向量搜索到图谱记忆——2026年主流AI Agent记忆系统横向对比。mem0、Zep、Moltable 功能/架构/定价全维度分析。',
            datePublished: '2026-07-10',
            author: { '@type': 'Organization', name: 'Moltable' },
            publisher: {
              '@type': 'Organization',
              name: 'Moltable.ai',
              logo: { '@type': 'ImageObject', url: 'https://www.moltable.ai/logo.svg' },
            },
            mainEntityOfPage: { '@type': 'WebPage', '@id': 'https://www.moltable.ai/blog/agent-memory-landscape-2026' },
            image: 'https://www.moltable.ai/logo-horizontal.svg',
          }),
        }}
      />
      {children}
    </>
  )
}
