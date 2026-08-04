import type { Metadata } from 'next'
import './globals.css'
import { LanguageProvider } from '@/contexts/LanguageContext'
import { ToastProvider } from '@/contexts/ToastContext'
import PublicShell from '@/components/PublicShell'

export const metadata: Metadata = {
  metadataBase: new URL('https://www.moltable.ai'),
  title: {
    default: 'Moltable — AI 身份同步：一次注册，所有 AI 都认识你',
    template: '%s | Moltable — AI Identity Sync',
  },
  description:
    '跨平台 AI 身份同步服务。换电脑 3 分钟恢复完整 AI 环境。支持 Hermes、Claude、ChatGPT、Cursor。90 天免费试用。',
  keywords: [
    'AI身份同步',
    'AI记忆',
    '跨平台AI',
    'Agent环境恢复',
    'MCP工具',
    'Persona',
    'AI Identity',
  ],
  viewport: 'width=device-width, initial-scale=1',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    title: 'Moltable — AI 身份同步：一次注册，所有 AI 都认识你',
    description:
      '跨平台 AI 身份同步服务。换电脑 3 分钟恢复完整 AI 环境。支持 Hermes、Claude、ChatGPT、Cursor。90 天免费试用。',
    url: 'https://www.moltable.ai',
    siteName: 'Moltable',
    locale: 'zh_CN',
    type: 'website',
    images: [
      {
        url: '/logo-horizontal.svg',
        width: 1200,
        height: 630,
        alt: 'Moltable — AI Identity Sync',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Moltable — AI 身份同步：一次注册，所有 AI 都认识你',
    description:
      '跨平台 AI 身份同步服务。换电脑 3 分钟恢复完整 AI 环境。支持 Hermes、Claude、ChatGPT、Cursor。',
    images: ['/logo-horizontal.svg'],
  },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      name: 'Moltable',
      url: 'https://www.moltable.ai',
      logo: 'https://www.moltable.ai/logo.svg',
      sameAs: ['https://github.com/moltable'],
      description:
        '跨平台 AI 身份同步服务。一次注册，所有 AI 都认识你。',
    },
    {
      '@type': 'SoftwareApplication',
      name: 'Moltable',
      applicationCategory: 'AIApplication',
      operatingSystem: 'Web',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'CNY',
      },
      description:
        '跨平台 AI 身份同步服务 — 支持 Hermes、Claude、ChatGPT、Cursor 等 MCP 兼容 AI Agent。',
      url: 'https://www.moltable.ai',
    },
  ],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <head>
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;590&display=swap"
          rel="stylesheet"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        {/* Umami Analytics — privacy-first, self-hostable web analytics */}
        <script
          defer
          src="https://umami.moltable.ai/script.js"
          data-website-id={process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID || 'moltable'}
        />
      </head>
      <body className="antialiased bg-ln-bg text-ln-text">
        <LanguageProvider>
          <ToastProvider>
            <PublicShell>{children}</PublicShell>
          </ToastProvider>
        </LanguageProvider>
      </body>
    </html>
  )
}
