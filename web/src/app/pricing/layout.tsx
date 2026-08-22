import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '定价 — Moltable',
  description:
    'Moltable 定价方案：Free 3 个备份源，Pro 10 个备份源 + 10GB 存储。',
  openGraph: {
    title: '定价 — Moltable',
    description:
      'Moltable 定价方案：Free 3 个备份源，Pro 10 个备份源 + 10GB 存储。',
  },
}

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
