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
    default: 'Moltable.ai — AI Identity Sync: One Registration, Every AI Knows You',
    template: '%s | Moltable.ai',
  },
  description:
    'Cross-platform AI identity sync. Restore your full AI environment in 3 minutes. Supports Hermes, Claude, ChatGPT, Cursor. 90-day free trial.',
  keywords: [
    'AI identity',
    'AI memory',
    'cross-platform AI',
    'agent environment',
    'MCP tools',
    'persona sync',
    'AI agent identity',
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
    title: 'Moltable — AI Identity Sync',
    description:
      'Cross-platform AI identity sync. Restore your full AI environment in 3 minutes. Hermes · Claude · ChatGPT · Cursor.',
    url: 'https://www.moltable.ai',
    siteName: 'Moltable.ai',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Moltable — AI Identity Sync',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Moltable — AI Identity Sync',
    description:
      'Cross-platform AI identity sync. Restore your full AI environment in 3 minutes.',
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
      sameAs: ['https://github.com/Moltable'],
      description:
        'Cross-platform AI identity sync — one registration, every AI agent knows you.',
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
        'Cross-platform AI identity sync — supports Hermes, Claude, ChatGPT, Cursor and MCP-compatible AI agents.',
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
        {/* Umami Analytics */}
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
