import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
  description:
    '换一台新 Mac，Claude、Cursor、Codex 全部失忆？手把手教你用 Moltable 在 3 分钟内恢复完整 AI 工作环境——从 Persona 到 MCP 配置，从项目记忆到工具偏好，一条命令全搞定。',
  keywords: [
    'AI环境恢复',
    '换电脑AI配置',
    'Claude记忆恢复',
    'AI身份同步',
    'MCP配置迁移',
    'Persona同步',
    'AI开发环境',
  ],
  openGraph: {
    title: '换电脑不换脑子：3 分钟恢复完整 AI 开发环境实战指南',
    description:
      '换一台新 Mac，AI 全部失忆了？本文手把手教你用 Moltable 在 3 分钟内恢复完整 AI 工作环境。含 Claude、Cursor、Codex 多 Agent 同步方案。',
    url: 'https://www.moltable.ai/blog/three-minute-env-recovery',
    siteName: 'Moltable',
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
  return children
}
