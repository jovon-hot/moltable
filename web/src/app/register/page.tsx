'use client'

import { useState } from 'react'
import { localRegister } from '@/lib/supabase'
import { useLang } from '@/contexts/LanguageContext'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

function RegisterForm() {
  const { t } = useLang()
  const searchParams = useSearchParams()
  const planParam = searchParams.get('plan') || ''
  const a = t.auth
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await localRegister(email, password)
      if (data.key) {
        // Store key in sessionStorage (not URL) — avoid browser history/log leaks
        sessionStorage.setItem('moltable_new_key', data.key)
        const params = new URLSearchParams({ new: 'true' })
        if (planParam === 'pro') params.set('plan', 'pro')
        window.location.href = `/connect?${params.toString()}`
      } else {
        window.location.href = '/dashboard'
      }
    } catch (err: any) {
      setError(err.message || a.registerFailed)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#0D0D14' }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl mb-1" style={{ fontWeight: 590, letterSpacing: '-0.3px', color: '#ffffff' }}>{a.registerTitle}</h1>
          <p className="text-sm" style={{ color: '#888888' }}>
            {planParam === 'pro' ? 'Pro · 90天免费' : 'Moltable'}
          </p>
        </div>

        <form onSubmit={handleRegister} className="space-y-3">
          <input type="email" placeholder={a.emailPlaceholder} value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#14141E', color: '#ffffff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #4338CA'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <input type="password" placeholder={a.passwordPlaceholder} value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-[6px] text-sm outline-none transition-all placeholder:text-sm"
            style={{ background: '#14141E', color: '#ffffff', boxShadow: '0 0 0 1px rgba(255,255,255,0.08)', fontWeight: 400 }}
            onFocus={e => e.target.style.boxShadow = '0 0 0 1px #4338CA'}
            onBlur={e => e.target.style.boxShadow = '0 0 0 1px rgba(255,255,255,0.08)'}
            required />
          <p className="text-xs" style={{ color: '#5a5f68' }}>{a.passwordHint}</p>
          {error && <p className="text-sm" style={{ color: '#f87171' }}>{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-[6px] text-sm font-medium disabled:opacity-50 transition-all hover:opacity-90"
            style={{ background: '#4338CA', color: '#fff', fontWeight: 510 }}>
            {loading ? a.registering : a.registerBtn}
          </button>
        </form>

        <p className="text-sm text-center mt-6" style={{ color: '#888888' }}>
          {a.hasAccount} <a href="/login" style={{ color: '#3730A3' }} className="hover:underline">{a.goLogin}</a>
        </p>
      </div>
    </div>
  )
}

export default function RegisterPage() {
  return <Suspense fallback={<div />}><RegisterForm /></Suspense>
}
