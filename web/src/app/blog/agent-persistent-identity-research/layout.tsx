import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'arXiv 最新论文：AI Agent 的「持续身份」——多锚点架构如何让 Agent 不再失忆',
  description:
    '2026年3月 arXiv 论文提出多锚点身份理论：参考人类记忆障碍的神经科学研究，论证 AI Agent 需要偏好、决策、关系、价值观、叙事五个锚点来维持持续身份。Moltable 的三层架构完整实现了这一理论。',
  keywords: [
    'AI持续身份',
    'Agent身份锚点',
    'arXiv论文解读',
    '多锚点架构',
    'AI记忆',
    'Agent identity',
    '神经科学AI',
  ],
  openGraph: {
    title: 'arXiv 论文解读：AI Agent 的「持续身份」——多锚点架构',
    description:
      '2026年3月 arXiv 论文提出多锚点身份理论：五个锚点维持 AI Agent 持续身份。Moltable 三层架构完整实现了这一理论。',
    url: 'https://www.moltable.ai/blog/agent-persistent-identity-research',
    siteName: 'Moltable',
    type: 'article',
    publishedTime: '2026-08-04',
    images: [
      {
        url: '/logo-horizontal.svg',
        width: 1200,
        height: 630,
        alt: 'AI Agent 持续身份研究',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'arXiv 论文解读：AI Agent 的「持续身份」',
    description:
      '五个锚点维持 AI Agent 持续身份——多锚点架构论文解读。',
    images: ['/logo-horizontal.svg'],
  },
  alternates: {
    canonical: 'https://www.moltable.ai/blog/agent-persistent-identity-research',
  },
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return children
}
