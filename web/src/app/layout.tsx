import type { Metadata } from 'next'
import './globals.css'
import { LanguageProvider } from '@/contexts/LanguageContext'
import { ToastProvider } from '@/contexts/ToastContext'
import PublicShell from '@/components/PublicShell'

export const metadata: Metadata = {
  title: 'Moltable — AI Identity Layer (DID+VC)',
  description: '在任何 AI 里加载你的 Moltable，AI 就自动认识你。跨平台 AI 身份同步，DID+VC 密码学身份，多 Persona 切换。',
  keywords: ['AI身份', 'AI记忆', '跨平台', 'DID', 'VC', 'MCP', 'Agent', 'Persona'],
  openGraph: {
    title: 'Moltable — AI Identity Layer',
    description: '在任何 AI 里加载你的 Moltable，AI 就自动认识你。',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;590&display=swap" rel="stylesheet" />
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
