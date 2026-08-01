import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '登录 Moltable',
  description: '登录 Moltable 账户，管理你的 AI 身份、Persona 和记忆。',
  openGraph: {
    title: '登录 Moltable',
    description: '登录 Moltable 账户，管理你的 AI 身份、Persona 和记忆。',
  },
}

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
