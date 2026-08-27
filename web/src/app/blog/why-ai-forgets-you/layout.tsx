import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案',
  description:
    '每天早上打开 Claude，它都像第一次见你。不是 AI 笨，是你的调教成果从没被真正备份过。本文剖析 AI「失忆」的五个根因——偏好重置、项目上下文丢失、工具配置消失、Persona 被遗忘、无限自我介绍，并给出 Moltable 的灵魂资产备份解决方案：一次配置，所有 Agent 共享。',
  keywords: [
    'AI失忆',
    'AI记忆',
    'AI身份',
    'Soul Backup',
    'AI偏好管理',
    'Claude记忆',
    'Agent 化身',
    'Agent灵魂备份',
    'AI持久化',
    'Moltable',
  ],
  openGraph: {
    title: '为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案',
    description:
      '你的 AI 每天像第一次见你？本文剖析 AI「失忆」的五个根因，并给出 Moltable 的灵魂资产备份解决方案——一次配置，所有 Agent 共享。',
    url: 'https://www.moltable.ai/blog/why-ai-forgets-you',
    siteName: 'Moltable.ai',
    type: 'article',
    publishedTime: '2026-08-05',
    images: [
      {
        url: '/logo-horizontal.svg',
        width: 1200,
        height: 630,
        alt: '为什么你的 AI 每次都不记得你是谁',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '为什么你的 AI 每次都不记得你是谁',
    description: '不是 AI 笨，是你的调教成果从没被真正备份过。AI 失忆的五个根因与终极解决方案。',
    images: ['/logo-horizontal.svg'],
  },
  alternates: {
    canonical: 'https://www.moltable.ai/blog/why-ai-forgets-you',
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
            headline: '为什么你的 AI 每次都不记得你是谁 —— 以及 2026 年的终极解决方案',
            description:
              '每天早上打开 Claude，它都像第一次见你。本文剖析 AI「失忆」的五个根因，并给出 Moltable 的灵魂资产备份解决方案——一次配置，所有 Agent 共享。',
            datePublished: '2026-08-05',
            author: { '@type': 'Organization', name: 'Moltable' },
            publisher: {
              '@type': 'Organization',
              name: 'Moltable.ai',
              logo: { '@type': 'ImageObject', url: 'https://www.moltable.ai/logo-icon.svg' },
            },
            mainEntityOfPage: { '@type': 'WebPage', '@id': 'https://www.moltable.ai/blog/why-ai-forgets-you' },
            image: 'https://www.moltable.ai/logo-horizontal.svg',
          }),
        }}
      />
      {children}
    </>
  )
}
