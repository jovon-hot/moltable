import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '定价 — Moltable',
  description:
    'Moltable 定价方案：Free 始终免费，Pro 限时免费体验。30 天免费试用全部 Pro 功能。',
  openGraph: {
    title: '定价 — Moltable',
    description:
      'Moltable 定价方案：Free 始终免费，Pro 限时免费体验。',
  },
}

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
