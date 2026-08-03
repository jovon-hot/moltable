'use client'

import { usePathname } from 'next/navigation'
import PublicHeader from '@/components/PublicHeader'
import PublicFooter from '@/components/PublicFooter'

// Paths that should NOT get the public header/footer shell
const dashboardPrefix = '/dashboard'

const publicPaths = new Set([
  '/',
  '/login',
  '/register',
  '/pricing',
  '/docs',
  '/research',
  '/privacy',
  '/about',
  '/blog',
])

export default function PublicShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  // Check if current path is dashboard (or any non-public path)
  const isDashboard = pathname.startsWith(dashboardPrefix)

  // If it's a dashboard/internal path, render children directly (those pages have their own layout)
  if (isDashboard) {
    return <>{children}</>
  }

  // For public pages, wrap with header & footer
  return (
    <>
      <PublicHeader />
      <main className="min-h-screen pt-14">
        {children}
      </main>
      <PublicFooter />
    </>
  )
}
