import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
  description:
    '换一台新 Mac，Claude、Cursor、Codex 全部失忆？手把手教你用 Moltable 在线同步 + auto_provision 在 3 分钟内恢复完整 AI 工作环境——身份、记忆、技能偏好一键到位。',
  keywords: [
    'AI环境恢复',
    '换电脑AI配置',
    'Claude记忆恢复',
    'Agent在线同步',
    'MCP配置迁移',
    'Agent 在线同步',
    'AI开发环境',
  ],
  openGraph: {
    title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
    description:
      '换一台新 Mac，AI 全部失忆了？本文手把手教你用 Moltable 在 3 分钟内恢复完整 AI 工作环境。含 Claude、Cursor、Codex 多 Agent 同步方案。',
    url: 'https://www.moltable.ai/blog/three-minute-env-recovery',
    siteName: 'Moltable.ai',
    type: 'article',
    publishedTime: '2026-08-04',
    images: [
      {
        url: '/logo-horizontal.svg',
        width: 1200,
        height: 630,
        alt: '3分钟恢复AI开发环境',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境',
    description:
      '换一台新 Mac，AI 全部失忆？3 分钟恢复 Claude、Cursor、Codex 全部环境。',
    images: ['/logo-horizontal.svg'],
  },
  alternates: {
    canonical: 'https://www.moltable.ai/blog/three-minute-env-recovery',
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
            headline: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
            description:
              '换一台新 Mac，AI 全部失忆了？本文手把手教你用 Moltable 在 3 分钟内恢复完整 AI 工作环境。含 Claude、Cursor、Codex 多 Agent 同步方案。',
            datePublished: '2026-08-04',
            author: { '@type': 'Organization', name: 'Moltable' },
            publisher: {
              '@type': 'Organization',
              name: 'Moltable.ai',
              logo: { '@type': 'ImageObject', url: 'https://www.moltable.ai/logo-icon.svg' },
            },
            mainEntityOfPage: { '@type': 'WebPage', '@id': 'https://www.moltable.ai/blog/three-minute-env-recovery' },
            image: 'https://www.moltable.ai/logo-horizontal.svg',
          }),
        }}
      />
      {children}
    </>
  )
}
