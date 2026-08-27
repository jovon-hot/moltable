import type { Metadata, Viewport } from 'next'
import './globals.css'
import { LanguageProvider } from '@/contexts/LanguageContext'
import { ToastProvider } from '@/contexts/ToastContext'
import PublicShell from '@/components/PublicShell'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const metadata: Metadata = {
  metadataBase: new URL('https://www.moltable.ai'),
  title: {
    default: 'Moltable.ai — Your AI, Always in Sync',
    template: '%s | Moltable.ai',
  },
  description:
    'One account that syncs your tuned AI identity, memories, personas, and projects across devices and agents — with file-level backup and cross-framework migration as a safety net. Your AI, always in sync.',
  keywords: [
    'AI agent sync',
    'online agent memory',
    'cross-framework migration',
    'AI agent versioning',
    'MCP tools',
    'agent environment',
    'auto provision',
    'agent identity sync',
  ],
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
    title: 'Moltable — Your AI, Always in Sync',
    description:
      'Sync your tuned AI across devices and agents — identity, memory, personas, projects. Hermes · OpenClaw · Claude · Codex.',
    url: 'https://www.moltable.ai',
    siteName: 'Moltable.ai',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Moltable — Your AI, Always in Sync',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Moltable — Your AI, Always in Sync',
    description:
      'Sync your tuned AI identity, memory, personas, and projects across devices and agents.',
    images: ['/og-image.png'],
  },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      name: 'Moltable.ai',
      url: 'https://www.moltable.ai',
      logo: 'https://www.moltable.ai/logo-icon.svg',
      sameAs: ['https://github.com/jovon-hot/moltable'],
      description:
        'Agent online sync layer — sync, version, and migrate your tuned AI agents across frameworks.',
    },
    {
      '@type': 'SoftwareApplication',
      name: 'Moltable.ai',
      applicationCategory: 'AIApplication',
      operatingSystem: 'Web',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD',
      },
      description:
        'Sync, version, and migrate your tuned AI agents (identity, memory, personas, projects) across Hermes, OpenClaw, Claude, Codex and MCP-compatible agents.',
      url: 'https://www.moltable.ai',
    },
  ],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
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
