import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  // No Supabase configured → demo mode, allow all
  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.next()
  }

  let response = NextResponse.next()
  const path = request.nextUrl.pathname

  // Try auth — but don't block if Supabase is unreachable
  try {
    const supabase = createServerClient(supabaseUrl, supabaseKey, {
      cookies: {
        get(name) { return request.cookies.get(name)?.value },
        set(name, value, options) { response.cookies.set({ name, value, ...options }) },
        remove(name, options) { response.cookies.set({ name, value: '', ...options }) },
      },
    })

    const { data: { user } } = await supabase.auth.getUser()

    if (user) {
      // Logged in: redirect away from login/register
      if (path === '/login' || path === '/register') {
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }
      return response
    }
  } catch {
    // Supabase unreachable → demo mode
  }

  // No user: dashboard shows demo, auth pages stay accessible
  // No redirects — let each page handle demo/empty state
  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register'],
}
