import type { Metadata } from 'next'
import { redirect } from 'next/navigation'
import { cookies } from 'next/headers'
import { createServerClient } from '@supabase/ssr'

export const metadata: Metadata = {
  title: 'Admin Dashboard — Moltable',
  robots: { index: false },
}

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  // Demo mode (no Supabase) — same as middleware, allow through
  if (supabaseUrl && supabaseKey) {
    const cookieStore = await cookies()
    const supabase = createServerClient(supabaseUrl, supabaseKey, {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options))
          } catch {
            // setAll throws when called from a Server Component; middleware handles refresh
          }
        },
      },
    })

    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      redirect('/login')
    }
  }

  return <>{children}</>
}
