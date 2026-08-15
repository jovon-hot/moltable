import { isLocalMode, getLocalKey } from './supabase'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://api.moltable.ai'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL

async function getSupabaseToken(): Promise<string | undefined> {
  if (!SUPABASE_URL) return undefined
  try {
    const supabase = (await import('@supabase/ssr')).createBrowserClient(
      SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )
    return (await supabase.auth.getSession()).data.session?.access_token
  } catch {
    return undefined
  }
}

export async function getToken(): Promise<string | undefined> {
  const localKey = getLocalKey()
  if (localKey) return localKey
  if (SUPABASE_URL) return await getSupabaseToken()
  return undefined
}

export async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getToken()
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-API-Key': token } : {}),
      ...(options.headers || {}),
    },
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${text || res.statusText}`)
  }
  if (res.status === 204) return {} as T
  return res.json()
}

export async function activateTrial(plan: 'pro' | 'team' = 'pro'): Promise<{activated: boolean; message: string; expires_at?: string}> {
  const token = await getToken()
  if (!token) throw new Error('Login required to activate trial')

  const res = await fetch(`${API_BASE}/api/billing/activate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': token,
    },
    body: JSON.stringify({ plan, accept_terms: true }),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Activation ${res.status}: ${text}`)
  }
  return res.json()
}

export async function createCheckout(plan: 'pro' | 'team' = 'pro', period: 'monthly' | 'yearly' = 'monthly'): Promise<{url: string}> {
  const token = await getToken()
  if (!token) throw new Error('Login required to subscribe')

  const res = await fetch(`${API_BASE}/api/billing/checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': token,
    },
    body: JSON.stringify({ plan, period }),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Checkout ${res.status}: ${text}`)
  }
  const data = await res.json()
  window.location.href = data.url
  return data
}
