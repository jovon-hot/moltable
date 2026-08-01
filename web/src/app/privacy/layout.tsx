import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '隐私政策 — Moltable',
  description:
    'Moltable 隐私政策：了解我们如何收集、存储和保护你的数据。绝不用于 AI 训练，你的数据属于你。',
  openGraph: {
    title: '隐私政策 — Moltable',
    description:
      'Moltable 隐私政策：了解我们如何收集、存储和保护你的数据。',
  },
}

export default function PrivacyLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
