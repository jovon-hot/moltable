import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Agent 在线同步平台对比 2026：Moltable vs mem0 vs Zep',
  description:
    '从定位、功能、定价、架构四个维度对比 Moltable（Agent 在线同步层）与 mem0、Zep（记忆层）。帮助开发者和团队理解两者的本质区别。',
  keywords: [
    'Moltable vs mem0',
    'agent online sync',
    'mem0 alternative',
    'Zep alternative',
    'Agent 在线同步',
    'Agent 同步对比',
    'MCP 工具对比',
  ],
  openGraph: {
    title: 'Agent 在线同步平台对比 2026：Moltable vs mem0 vs Zep',
    description:
      'Moltable 做 Agent 在线同步，mem0/Zep 做记忆层。含功能对比表、架构分析、定价对比和选型建议。',
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
    title: 'Agent 在线同步平台对比 2026',
    description:
      'Moltable vs mem0 vs Zep — Agent 在线同步 vs 记忆层',
    images: ['/logo-horizontal.svg'],
  },
  alternates: {
    canonical: 'https://www.moltable.ai/compare',
  },
}

export default function CompareLayout({ children }: { children: React.ReactNode }) {
  return children
}
