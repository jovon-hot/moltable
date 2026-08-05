import type { Metadata } from 'next'
import BlogLayout from '@/components/BlogLayout'

export const metadata: Metadata = {
  title: 'RAG vs Fine-Tuning vs Identity Layer：AI 个性化的不可能三角与破局之道',
  description: 'RAG 喂文档，Fine-Tuning 改模型，Identity Layer 建模身份——三种 AI 个性化方案深度对比。2026 年正确的技术选型是什么？',
  alternates: { canonical: 'https://www.moltable.ai/blog/rag-vs-finetuning-vs-identity' },
  openGraph: {
    title: 'RAG vs Fine-Tuning vs Identity Layer — AI 个性化不可能三角',
    description: '为什么 AI 还是不记得你？三种方案的架构对比、成本分析和最佳实践组合。',
    url: 'https://www.moltable.ai/blog/rag-vs-finetuning-vs-identity',
    type: 'article',
    publishedTime: '2026-08-06',
    tags: ['AI', 'RAG', 'Fine-Tuning', 'Identity', '架构'],
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <BlogLayout>{children}</BlogLayout>
}
