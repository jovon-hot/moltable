import type { Metadata } from 'next'
import BlogLayout from '@/components/BlogLayout'

export const metadata: Metadata = {
  title: 'AI 失忆的真实成本：开发者每年浪费多少小时在「重新认识你」上？',
  description:
    '我们分析了 200+ 开发者的 AI 使用习惯，发现平均每人每周浪费 3.2 小时在「重新教 AI 认识自己」上。本文用真实数据量化 AI 失忆的隐性成本，并给出零摩擦的 Identity Layer 解决方案。',
  keywords: [
    'AI失忆',
    'AI身份层',
    'AI效率',
    'AI记忆',
    'Identity Layer',
    '开发者效率',
    'AI onboarding',
    'Moltable',
  ],
  alternates: { canonical: 'https://www.moltable.ai/blog/hidden-cost-of-ai-amnesia' },
  openGraph: {
    title: 'AI 失忆的真实成本：开发者每年浪费多少小时在「重新认识你」上？',
    description:
      '200+ 开发者实测：平均每周 3.2 小时浪费在「重新教 AI 认识自己」。用真实数据量化 AI 失忆的隐性成本，以及 Identity Layer 的零摩擦解法。',
    url: 'https://www.moltable.ai/blog/hidden-cost-of-ai-amnesia',
    siteName: 'Moltable.ai',
    type: 'article',
    publishedTime: '2026-08-06',
    tags: ['研究', '效率', '数据', 'Identity', 'AI'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI 失忆的真实成本：每周 3.2 小时，每年 21 个工作日',
    description:
      '200+ 开发者实测：平均每周 3.2 小时浪费在「重新教 AI 认识自己」。Identity Layer 如何把这项开销降到零。',
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <BlogLayout>{children}</BlogLayout>
}
