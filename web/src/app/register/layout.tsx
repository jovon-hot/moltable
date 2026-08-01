import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '注册 Moltable — 免费开始',
  description:
    '注册 Moltable，免费开始使用 AI 身份同步服务。90 天免费试用，支持 Hermes、Claude、ChatGPT、Cursor。',
  openGraph: {
    title: '注册 Moltable — 免费开始',
    description:
      '注册 Moltable，免费开始使用 AI 身份同步服务。',
  },
}

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
