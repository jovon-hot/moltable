import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI Agent 记忆与身份平台对比 2026：Moltable vs mem0 vs Zep',
  description:
    '从架构、功能、定价、生态、开源五个维度全面对比 Moltable、mem0、Zep 三大 AI Agent 记忆/身份基础设施平台。帮助开发者和团队做出最佳技术选型。',
  keywords: [
    'Moltable vs mem0',
    'AI Agent 记忆对比',
    'mem0 alternative',
    'Zep alternative',
    'AI Identity 平台',
    'Agent memory comparison',
    'MCP 工具对比',
  ],
  openGraph: {
    title: 'AI Agent 记忆与身份平台对比 2026：Moltable vs mem0 vs Zep',
    description:
      '从架构、功能、定价、生态、开源五个维度全面对比三大平台。含详细功能对比表、架构分析、定价对比和选型建议。',
    url: 'https://www.moltable.ai/compare',
    siteName: 'Moltable.ai',
    locale: 'zh_CN',
    type: 'article',
    images: [
      {
        url: '/logo-horizontal.svg',
        width: 1200,
        height: 630,
        alt: 'Moltable vs mem0 vs Zep comparison',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Agent 记忆与身份平台对比 2026',
    description:
      'Moltable vs mem0 vs Zep — 全面对比三大 AI Agent 基础设施平台',
    images: ['/logo-horizontal.svg'],
  },
  alternates: {
    canonical: 'https://www.moltable.ai/compare',
  },
}

export default function CompareLayout({ children }: { children: React.ReactNode }) {
  return children
}
